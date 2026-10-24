#!/usr/bin/env python3
"""Validate lint, parser, diagram, smoke-test, fixture, and ClawHub bundle gates."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

try:
    import yaml
except ImportError:  # pragma: no cover - reported clearly at runtime
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "env", "ENV", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
             "scans", "compiled", "reports", "fixtures", "out"}
URL_SAFE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".docx", ".ttf", ".otf", ".woff", ".woff2"}
TEXT_SUFFIXES = {
    "", ".css", ".cfg", ".csv", ".gitignore", ".gitattributes", ".html", ".ini", ".j2", ".js", ".json",
    ".md", ".mmd", ".ps1", ".py", ".sh", ".svg", ".toml", ".txt", ".yaml", ".yml",
}
SPECIAL_TEXT_FILES = {"LICENSE", "README", "SKILL.md", "QUALITY.md", "CLAW_HUB_PUBLISHING.md", ".clawhubignore"}
DEFAULT_CLAWHUBIGNORE_PATTERNS = [
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.pdf", "*.docx", "*.ipynb", "*.ttf", "*.otf", "*.woff", "*.woff2",
    "preview/", "output/", "scans/", "compiled/", "reports/", "tests/fixtures/", "tests/out/",
    "__pycache__/", "*.py[cod]", "*$py.class", ".mypy_cache/", ".pytest_cache/", ".ruff_cache/",
    ".venv/", "venv/", "env/", "ENV/", ".env", ".env.*", "secrets.json", "*_secret.ini", "*_local.ini", "*.tmp",
    ".DS_Store", "Thumbs.db", "desktop.ini",
]


def iter_files(*suffixes: str) -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix in suffixes:
            files.append(path)
    return sorted(files)


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def run_ruff() -> None:
    if shutil.which("ruff"):
        run(["ruff", "check", "."])
        return
    try:
        run([sys.executable, "-m", "ruff", "check", "."])
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    raise RuntimeError("ruff is required for quality validation")


def compile_python() -> None:
    for path in iter_files(".py"):
        py_compile.compile(str(path), doraise=True)
    print("python compile ok")


def parse_structured_files() -> None:
    yaml_files = iter_files(".yaml", ".yml")
    yaml_module = cast(Any, yaml)
    if yaml_files and yaml_module is None:
        raise RuntimeError("PyYAML is required to parse YAML files")
    for path in yaml_files:
        yaml_module.safe_load(path.read_text(encoding="utf-8"))
    for path in iter_files(".json"):
        json.loads(path.read_text(encoding="utf-8"))
    print("structured files ok")


def validate_mermaid(skip: bool) -> None:
    diagrams = iter_files(".mmd")
    if not diagrams:
        print("mermaid skipped: no .mmd files")
        return
    if skip or not shutil.which("mmdc"):
        print("mermaid skipped: %s" % ("requested" if skip else "mmdc not available"))
        return
    with tempfile.TemporaryDirectory(prefix="skill-mermaid-") as tmp:
        out_dir = Path(tmp)
        config_path = out_dir / "puppeteer-config.json"
        config_path.write_text(json.dumps({"args": ["--no-sandbox", "--disable-setuid-sandbox"]}), encoding="utf-8")
        for index, path in enumerate(diagrams, start=1):
            run(["mmdc", "-i", str(path), "-o", str(out_dir / f"diagram-{index}.svg"), "-b", "white", "-p", str(config_path)])
    print("mermaid ok")


def smoke_pipeline() -> None:
    for script in ("run_pipeline.py", "compile_ai_logs.py", "analyze_events.py", "build_report.py", "ledger.py", "ledger_store.py", "detect_hosts.py",
                   "anonymize.py", "schedule.py", "render_ledger_doc.py", "render_pdf.py", "ledger_archive.py", "ledger_query.py", "scoped_report.py"):
        run([sys.executable, str(ROOT / "scripts" / script), "--help"])
    print("pipeline smoke ok")


def run_report_tests() -> None:
    for pattern in ("test_pricing.py", "test_scoped_report.py", "test_package_mini_swe.py", "test_goose*.py"):
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"])
    print("pricing, scoped report and Goose native suites ok")


def run_fixture_suite() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "tests" / "make_fixtures.py")], cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    if result.returncode != 0 or "ALL OK" not in result.stdout:
        sys.stderr.write(result.stderr)
        raise RuntimeError("parser fixture suite failed")
    print("fixture suite ok")
    env = dict(os.environ, AI_USAGE_LEDGER_HOME=str(ROOT / "tests" / "out" / "home"))
    result = subprocess.run([sys.executable, str(ROOT / "tests" / "test_store.py")], cwd=ROOT, capture_output=True, text=True, env=env)
    sys.stdout.write(result.stdout)
    if result.returncode != 0 or "STORE OK" not in result.stdout:
        sys.stderr.write(result.stderr)
        raise RuntimeError("store / onboarding suite failed")
    print("store suite ok")
    result = subprocess.run([sys.executable, str(ROOT / "tests" / "test_security.py")], cwd=ROOT, capture_output=True, text=True, env=env)
    sys.stdout.write(result.stdout)
    if result.returncode != 0 or "SECURITY OK" not in result.stdout:
        sys.stderr.write(result.stderr)
        raise RuntimeError("security suite failed")
    shutil.rmtree(ROOT / "tests" / "fixtures", ignore_errors=True)
    shutil.rmtree(ROOT / "tests" / "out", ignore_errors=True)
    print("security suite ok")


def frontmatter() -> dict[str, Any]:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise RuntimeError("SKILL.md must start with YAML frontmatter")
    yaml_module = cast(Any, yaml)
    if yaml_module is None:
        raise RuntimeError("PyYAML is required to parse SKILL.md frontmatter")
    data = yaml_module.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        raise RuntimeError("SKILL.md frontmatter must be a mapping")
    return data


def ignore_patterns() -> list[str]:
    ignore_file = ROOT / ".clawhubignore"
    if not ignore_file.exists():
        if (ROOT / ".git").exists():
            raise RuntimeError(".clawhubignore is required for ClawHub publishing")
        print("clawhub ignore defaults used: .clawhubignore is not present in this installed package")
        return DEFAULT_CLAWHUBIGNORE_PATTERNS.copy()
    patterns = []
    for raw in ignore_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def ignored(rel: str, patterns: list[str]) -> bool:
    rel = rel.replace("\\", "/")
    for pattern in patterns:
        negated = pattern.startswith("!")
        candidate = pattern[1:] if negated else pattern
        if candidate.endswith("/"):
            matched = rel == candidate[:-1] or rel.startswith(candidate) or ("/" + candidate) in ("/" + rel)
        elif "/" in candidate:
            matched = fnmatch.fnmatch(rel, candidate)
        else:
            matched = fnmatch.fnmatch(Path(rel).name, candidate)
        if matched:
            return not negated
    return False


def publish_candidate_files(patterns: list[str]) -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in SKIP_DIRS for part in Path(rel).parts):
            continue
        if ignored(rel, patterns):
            continue
        files.append(path)
    return sorted(files)


def package_name(spec: str) -> str:
    return re.split(r"[<>=!~]", spec, 1)[0].strip().lower()


def assert_dependency(openclaw: dict[str, Any], package: str) -> None:
    installs = openclaw.get("install") or []
    packages = {package_name(str(item.get("package", ""))) for item in installs if isinstance(item, dict)}
    if package.lower() not in packages:
        raise RuntimeError(f"metadata.openclaw.install must declare {package}")


def validate_self_contained_pages() -> None:
    """Committed example pages must not reference anything on the network and must carry a CSP."""
    ext = re.compile(r"""(?:src|href)\s*=\s*["']https?://""", re.IGNORECASE)
    for name in ("example.html", "example-study.html"):
        path = ROOT / "assets" / "examples" / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ext.search(text) or "fonts.googleapis" in text:
            raise RuntimeError(f"{name} references an external resource; generated pages must be self-contained")
        if "Content-Security-Policy" not in text:
            raise RuntimeError(f"{name} has no Content-Security-Policy meta tag")
    print("self-contained pages ok")


def validate_clawhub_bundle() -> None:
    data = frontmatter()
    name = data.get("name")
    version = data.get("version")
    metadata = data.get("metadata") or {}
    openclaw = metadata.get("openclaw") or {}
    for field in ["name", "description", "version"]:
        if not data.get(field):
            raise RuntimeError(f"SKILL.md frontmatter missing {field}")
    if not URL_SAFE_RE.fullmatch(str(name)):
        raise RuntimeError(f"skill name is not a URL-safe ClawHub slug: {name}")
    if not SEMVER_RE.fullmatch(str(version)):
        raise RuntimeError(f"version is not semver: {version}")
    if openclaw.get("skillKey") != name:
        raise RuntimeError("metadata.openclaw.skillKey must match name")
    homepage = openclaw.get("homepage")
    if not homepage or not str(homepage).startswith("https://github.com/CompleteTech-LLC/"):
        raise RuntimeError("metadata.openclaw.homepage must point to the CompleteTech GitHub repo")
    requires = openclaw.get("requires") or {}
    bins = requires.get("bins") or []
    if list((ROOT / "scripts").glob("*.py")) and "python3" not in bins:
        raise RuntimeError("Python-backed skills must declare requires.bins: python3")
    py_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in iter_files(".py"))
    if re.search(r"(?m)^\s*import\s+yaml\b", py_text):
        assert_dependency(openclaw, "pyyaml")

    patterns = ignore_patterns()
    for required_pattern in ["*.png", "*.pdf", "*.docx", "*.ttf", "preview/", "output/", ".env", "*.tmp", "scans/", "compiled/", "reports/"]:
        if required_pattern not in patterns:
            raise RuntimeError(f".clawhubignore missing required pattern: {required_pattern}")
    candidate_files = publish_candidate_files(patterns)
    for path in candidate_files:
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in BINARY_SUFFIXES:
            raise RuntimeError(f"binary file would be included in ClawHub bundle: {rel}")
        if path.name in SPECIAL_TEXT_FILES or path.suffix.lower() in TEXT_SUFFIXES:
            continue
        raise RuntimeError(f"non-text or unknown file would be included in ClawHub bundle: {rel}")
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "per-skill pricing" in skill_text.lower() or "paid skill" in skill_text.lower():
        raise RuntimeError("SKILL.md appears to contain unsupported ClawHub pricing language")
    if not (ROOT / "CLAW_HUB_PUBLISHING.md").exists():
        raise RuntimeError("CLAW_HUB_PUBLISHING.md is required")
    print(f"clawhub bundle ok ({len(candidate_files)} text files)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mermaid", action="store_true", help="Skip Mermaid render validation when local tooling is unavailable.")
    parser.add_argument("--skip-fixtures", action="store_true", help="Skip the parser fixture suite.")
    args = parser.parse_args()

    compile_python()
    run_ruff()
    parse_structured_files()
    validate_mermaid(args.skip_mermaid)
    smoke_pipeline()
    run_report_tests()
    if not args.skip_fixtures:
        run_fixture_suite()
    validate_self_contained_pages()
    validate_clawhub_bundle()
    print("quality validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
