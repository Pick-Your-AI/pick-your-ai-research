"""Synthetic package regressions; no specialist code or personal data is used."""
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("package", Path(__file__).resolve().parents[1] / "scripts/validate_package.py")
assert SPEC and SPEC.loader
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


def png_fixture():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\0\0\0\0")) + chunk(b"IEND", b"")


class PackageContractTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "checkout"
        self.manifest: dict[str, object] = dict(schema_version=1, family=package.FAMILY, repository="CompleteTech-LLC/demo-skill", skill_name="demo-skill", kind="catalog-renderer", entrypoints=["scripts/render.py"], example_inputs=["example.md"], network_mode="local", private=False)
        for name in (*package.FILES, "scripts/render.py", "example.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("demo\n", encoding="utf-8")
        (self.root / "assets").mkdir()
        (self.root / "assets/logo.png").write_bytes(png_fixture())
        (self.root / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
        (self.root / "README.md").write_text("\n".join(package.NAVIGATION), encoding="utf-8")
        self.save()

    def save(self):
        (self.root / "skill-package.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_valid_and_no_execution(self):
        (self.root / "scripts/render.py").write_text("raise RuntimeError('do not execute')", encoding="utf-8")
        self.assertEqual(package.validate(self.root), [])

    def test_bad_values(self):
        for field, value in (("schema_version", True), ("family", "other"), ("skill_name", "../escape"), ("repository", "other/demo"), ("kind", []), ("network_mode", {}), ("private", "false"), ("entrypoints", []), ("entrypoints", [None]), ("example_inputs", "example.md"), ("example_inputs", ["example.md", "example.md"])):
            with self.subTest(field=field, value=value):
                original = self.manifest[field]
                self.manifest[field] = value
                self.save()
                self.assertTrue(package.validate(self.root))
                self.manifest[field] = original

    def test_json_and_missing_fields(self):
        for text in ("{", "[]", "null", "{}", '{"private":true,"private":false}'):
            (self.root / "skill-package.json").write_text(text, encoding="utf-8")
            self.assertTrue(package.validate(self.root))

    def test_paths_and_links(self):
        for value in ("../escape", "/escape", "C:/escape", "a\\b", "./example.md", "a//b", "bad\npath", "missing.md"):
            with self.subTest(path=value):
                self.manifest["entrypoints"] = [value]
                self.save()
                self.assertTrue(package.validate(self.root))
        self.manifest["entrypoints"] = ["scripts/render.py"]
        self.save()
        for target in ("missing.md", "%2e%2e/outside", "//outside/file", "file:///etc/passwd", "file:example.md"):
            (self.root / "ONBOARDING.md").write_text(f"[Bad]({target})", encoding="utf-8")
            self.assertTrue(package.validate(self.root))

    def test_escaping_symlink(self):
        target = self.root / "example.md"
        outside = self.root.parent / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        target.unlink()
        try:
            target.symlink_to(outside)
        except OSError as exc:
            self.skipTest(str(exc))
        self.assertTrue(package.validate(self.root))

    def test_png_corruption(self):
        image = png_fixture()
        for data in (b"not png", image[:8], image[:-12], image + b"junk", image[:-1] + bytes([image[-1] ^ 1])):
            (self.root / "assets/logo.png").write_bytes(data)
            self.assertTrue(package.validate(self.root))

    def test_missing_required_files(self):
        for name in (*package.FILES, "assets/logo.png"):
            with self.subTest(path=name):
                path = self.root / name
                data = path.read_bytes()
                path.unlink()
                self.assertTrue(package.validate(self.root))
                path.write_bytes(data)

    def test_declared_generator_base_is_required(self):
        self.manifest["kind"] = "config-generator"
        self.save()
        self.assertEqual(package.validate(self.root), [])
        self.manifest["example_inputs"] = ["config.ini", "example.md"]
        self.save()
        self.assertTrue(package.validate(self.root))
        (self.root / "config.ini").write_text("[demo]\n", encoding="utf-8")
        self.assertEqual(package.validate(self.root), [])

    def test_names_and_navigation(self):
        (self.root / "SKILL.md").write_text("---\nname: wrong\n---\n", encoding="utf-8")
        self.assertTrue(package.validate(self.root))
        (self.root / "SKILL.md").write_bytes(b'---\r\nname: "demo-skill"\r\n---\r\n')
        self.assertEqual(package.validate(self.root), [])
        (self.root / "README.md").write_text("no navigation", encoding="utf-8")
        self.assertTrue(package.validate(self.root))

    def test_ledger_install_name_and_links(self):
        self.manifest.update(skill_name="ai-usage-ledger", repository="CompleteTech-LLC/ai-usage-ledger-skill", kind="usage-ledger", network_mode="operator-selected-hosts")
        self.save()
        (self.root / "SKILL.md").write_text("---\nname: ai-usage-ledger\n---\n", encoding="utf-8")
        (self.root / "ONBOARDING.md").write_text("[Read](README.md#demo) [Web](https://example.com) [Here](#here)", encoding="utf-8")
        self.assertEqual(package.validate(self.root), [])


    def test_duplicate_name_with_comment_or_invalid_value(self):
        for second in ("name: other # duplicate", "name: >", "'name': other", '"name": other', "name: [other]"):
            with self.subTest(second=second):
                (self.root / "SKILL.md").write_text("---\nname: demo-skill\n" + second + "\n---\n", encoding="utf-8")
                self.assertTrue(package.validate(self.root))

    def test_name_quotes_and_inline_comments(self):
        for scalar in ("demo-skill # activation", '\"demo-skill\" # activation', "'demo-skill'"):
            (self.root / "SKILL.md").write_text("---\nname: " + scalar + "\n---\n", encoding="utf-8")
            self.assertEqual(package.validate(self.root), [])
        for scalar in ('\"demo-skill\'', "'demo-skill\"", '\"demo-skill', "demo-skill'", "demo-skill#not-a-comment"):
            (self.root / "SKILL.md").write_text("---\nname: " + scalar + "\n---\n", encoding="utf-8")
            self.assertTrue(package.validate(self.root))

    def test_markdown_titles_and_angle_paths(self):
        (self.root / "file name.md").write_text("example", encoding="utf-8")
        for link in ('[Read](README.md "Overview")', "[Read](README.md 'Overview')", "[Read](README.md (Overview))", '[Read](<file name.md> "Overview")'):
            (self.root / "ONBOARDING.md").write_text(link, encoding="utf-8")
            self.assertEqual(package.validate(self.root), [])
        (self.root / "ONBOARDING.md").write_text('[Missing](missing.md "Overview")', encoding="utf-8")
        self.assertTrue(package.validate(self.root))

    def test_documented_code_links_are_not_real_links(self):
        (self.root / "ONBOARDING.md").write_text('`[Example](not-a-file.md)`\n\n```markdown\n[Example](not-a-file.md)\n```\n', encoding="utf-8")
        self.assertEqual(package.validate(self.root), [])

    def test_doubled_skill_suffix_rejected(self):
        self.manifest["repository"] = "CompleteTech-LLC/demo-skill-skill"
        self.save()
        self.assertTrue(package.validate(self.root))

    def test_cyclic_symlink_is_reported(self):
        path = self.root / "example.md"
        path.unlink()
        try:
            path.symlink_to("example.md")
        except OSError as exc:
            self.skipTest(str(exc))
        self.assertTrue(package.validate(self.root))


if __name__ == "__main__":
    unittest.main()
