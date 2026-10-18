#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["tokenizers==0.23.3", "pydantic==2.12.5"]
# ///
# How to run:
# Install uv if needed: https://docs.astral.sh/uv/getting-started/installation/
# uv run --python 3.12 scripts/token_count_experiment.py TOKENIZER_JSON FIXTURES_JSON OUTPUT_JSON
# Download the pinned tokenizer outside Git as documented in the research note.
"""Raw-text tokenizer measurements on synthetic fixtures, not model inference."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field
from tokenizers import Tokenizer

ROOT: Final = Path(__file__).resolve().parents[1]
MANIFEST: Final = ROOT / "evidence/t1-qwen3-8b-tokenizer.json"


class FrozenRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Artifact(FrozenRecord):
    id: str
    uri: str
    version: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    access: str
    description: str
    rights: str


class Sample(FrozenRecord):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    stratum: str = Field(min_length=1)
    text: str = Field(max_length=4096)


class Fixtures(FrozenRecord):
    synthetic: Literal[True]
    scope: Literal["raw_text_only"]
    synthetic_budget_tokens: int = Field(gt=0)
    samples: tuple[Sample, ...] = Field(min_length=1, max_length=64)


class Observation(FrozenRecord):
    id: str
    stratum: str
    unicode_codepoints: int
    utf8_bytes: int
    observed_tokens: int
    ceil_codepoints_div_4: int
    signed_residual_tokens: int


def measure(tokenizer: Tokenizer, sample: Sample) -> Observation:
    observed = len(tokenizer.encode(sample.text, add_special_tokens=False).ids)
    estimate = (len(sample.text) + 3) // 4
    return Observation(
        id=sample.id,
        stratum=sample.stratum,
        unicode_codepoints=len(sample.text),
        utf8_bytes=len(sample.text.encode("utf-8")),
        observed_tokens=observed,
        ceil_codepoints_div_4=estimate,
        signed_residual_tokens=observed - estimate,
    )


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: token_count_experiment.py TOKENIZER_JSON FIXTURES_JSON OUTPUT_JSON"
        )
    tokenizer_path, fixture_path, output_path = map(Path, sys.argv[1:])
    artifact = Artifact.model_validate_json(MANIFEST.read_text(encoding="utf-8"))
    tokenizer_bytes = tokenizer_path.read_bytes()
    digest = hashlib.sha256(tokenizer_bytes).hexdigest()
    if digest != artifact.sha256:
        raise SystemExit("Tokenizer SHA-256 mismatch; no observations written.")
    fixture_bytes = fixture_path.read_bytes()
    fixtures = Fixtures.model_validate_json(fixture_bytes)
    ids = tuple(sample.id for sample in fixtures.samples)
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate fixture IDs; no observations written.")
    tokenizer = Tokenizer.from_str(tokenizer_bytes.decode("utf-8"))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    observations = tuple(measure(tokenizer, sample) for sample in fixtures.samples)
    payload = {
        "issue": 7,
        "measured_at": datetime.now(UTC).isoformat(),
        "evidence_class": "local_software_measurement_on_synthetic_inputs",
        "scope": fixtures.scope,
        "synthetic_inputs": True,
        "model_revision": artifact.version,
        "tokenizer_sha256": digest,
        "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
        "python_version": platform.python_version(),
        "tokenizers_version": version("tokenizers"),
        "pydantic_version": version("pydantic"),
        "add_special_tokens": False,
        "truncation": False,
        "padding": False,
        "synthetic_budget_tokens": fixtures.synthetic_budget_tokens,
        "observations": [row.model_dump() for row in observations],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
