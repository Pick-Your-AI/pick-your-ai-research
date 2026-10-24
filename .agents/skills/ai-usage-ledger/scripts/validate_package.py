#!/usr/bin/env python3
"""Read-only, standard-library validation of a full CompleteTech skill checkout."""
from __future__ import annotations
import argparse
import json
import re
import struct
import zlib
from pathlib import Path
from urllib.parse import unquote, urlsplit

FAMILY = "completetech-skills"
FIELDS = set("schema_version family repository skill_name kind entrypoints example_inputs network_mode private".split())
FILES = ("README.md", "SKILL.md", "LICENSE", "BRAND_ASSETS.md", "ONBOARDING.md", "CONTRIBUTING.md", "BRANDING.md", "AGENTS.md", "requirements.txt", "agents/openai.yaml")
NAVIGATION = ("CompleteTech LLC Skills", "[Start here](ONBOARDING.md)", "[Contributing](CONTRIBUTING.md)", "assets/logo.png")
KINDS = ("catalog-renderer", "config-generator", "orchestrator", "usage-ledger")
NETWORK_MODES = ("local", "operator-selected-hosts", "optional-receipts")


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def local_file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value):
        raise ValueError(f"invalid package path: {value!r}")
    if "\\" in value or ":" in value or value.startswith("/") or any(p in ("", ".", "..") for p in value.split("/")):
        raise ValueError(f"unsafe package path: {value!r}")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"missing or escaping package file: {value}")
    return path


def validate_png(path: Path) -> None:
    """Check bounded chunks and CRCs; decoding and visual review remain separate."""
    with path.open("rb") as handle:
        data = handle.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("invalid or oversized PNG")
    offset, header, image = 8, False, False
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        end = offset + length + 12
        if end > len(data):
            raise ValueError("truncated PNG chunk")
        payload = data[offset + 8:end - 4]
        if zlib.crc32(kind + payload) != struct.unpack_from(">I", data, end - 4)[0]:
            raise ValueError("PNG checksum mismatch")
        if not header and kind != b"IHDR":
            raise ValueError("PNG must start with IHDR")
        if kind == b"IHDR":
            if header or length != 13:
                raise ValueError("invalid PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
            if not 0 < width < 2**31 or not 0 < height < 2**31 or depth not in depths.get(color, ()) or compression or filtering or interlace not in (0, 1):
                raise ValueError("invalid PNG parameters")
            header = True
        elif kind == b"IDAT":
            image = image or bool(length)
        elif kind == b"IEND":
            if length or not image or end != len(data):
                raise ValueError("invalid PNG end")
            return
        offset = end
    raise ValueError("incomplete PNG")


def allowed_repositories(name: object) -> tuple[str, ...]:
    if not isinstance(name, str):
        return ()
    repo = f"CompleteTech-LLC/{name}"
    return (repo,) if name.endswith("-skill") else (repo, repo + "-skill")


def activation_name(skill: str) -> str | None:
    """Read one simple top-level name scalar; reject duplicate keys first."""
    header = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", skill, re.S)
    if not header:
        return None
    # Count keys independently of their values, including comments/block scalars.
    keys = re.findall(r'''(?m)^(['"]?)name\1[ \t]*:(.*)$''', header.group(1))
    if len(keys) != 1:
        return None
    value = re.fullmatch(r'''[ \t]*(['"]?)([a-z0-9-]+)\1(?:[ \t]+\#.*|[ \t]*)''', keys[0][1])
    return value.group(2) if value else None


def markdown_targets(text: str) -> list[str]:
    """Extract ordinary inline-link destinations, excluding code and titles.

    This is not a complete Markdown linter: reference links, HTML and anchors
    remain outside this checkout contract. Quoted titles and angle destinations
    are supported, including spaces in angle-delimited local filenames.
    """
    text = re.sub(r"(?ms)^([`~]{3,})[^\n]*\n.*?^\1[^\n]*(?:\n|$)", "", text)
    text = re.sub(r"(`+).*?\1", "", text)
    pattern = r'''\[[^\]\n]*\]\([ \t]*(?:<([^>\n]+)>|([^\s()]+))(?:[ \t]+(?:"[^"\n]*"|'[^'\n]*'|\([^\n)]*\)))?[ \t]*\)'''
    return [match.group(1) or match.group(2) for match in re.finditer(pattern, text)]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(local_file(root, "skill-package.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        if not isinstance(manifest, dict) or set(manifest) != FIELDS:
            raise ValueError("manifest fields must match schema 1")
        name, repo = manifest["skill_name"], manifest["repository"]
        if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1 or manifest["family"] != FAMILY:
            errors.append("invalid schema_version or family")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append("invalid skill_name")
        if not isinstance(repo, str) or repo not in allowed_repositories(name):
            errors.append("repository does not match skill_name")
        if manifest["kind"] not in KINDS or manifest["network_mode"] not in NETWORK_MODES or type(manifest["private"]) is not bool:
            errors.append("invalid kind, network_mode or private")
        paths: list[object] = [*FILES, "assets/logo.png"]
        for field in ("entrypoints", "example_inputs"):
            values = manifest[field]
            if not isinstance(values, list) or not values or not all(isinstance(v, str) for v in values):
                errors.append(f"{field} must be a nonempty string array")
            else:
                if len(set(values)) != len(values):
                    errors.append(f"duplicate {field}")
                paths.extend(values)
        for value in paths:
            try:
                local_file(root, value)
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(str(exc))
        skill = local_file(root, "SKILL.md").read_text(encoding="utf-8")
        if activation_name(skill) != name:
            errors.append("SKILL.md name must match manifest")
        readme = local_file(root, "README.md").read_text(encoding="utf-8")
        errors.extend(f"missing README navigation: {item}" for item in NAVIGATION if item not in readme)
        validate_png(local_file(root, "assets/logo.png"))
        for document in ("ONBOARDING.md", "CONTRIBUTING.md", "BRANDING.md", "AGENTS.md"):
            text = local_file(root, document).read_text(encoding="utf-8")
            for target in markdown_targets(text):
                parsed = urlsplit(target)
                if target.startswith("#") or parsed.scheme in ("https", "http", "mailto"):
                    continue
                if parsed.scheme or parsed.netloc:
                    raise ValueError(f"unsupported documentation link: {target}")
                local_file(root, unquote(parsed.path))
    except (OSError, UnicodeError, ValueError, RuntimeError, RecursionError) as exc:
        errors.append(str(exc))
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    issues = validate(parser.parse_args().root)
    print("\n".join(issues) if issues else "Package contract OK; no specialist commands executed")
    raise SystemExit(bool(issues))
