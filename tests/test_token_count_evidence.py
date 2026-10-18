from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[1]
FIXTURES: Final = ROOT / "tests/fixtures/token-count-panel.json"
OBSERVATIONS: Final = ROOT / "research/T1-model-selection/token-count-observations.json"
MANIFEST: Final = ROOT / "evidence/t1-qwen3-8b-tokenizer.json"


class TokenCountEvidence(unittest.TestCase):
    def test_observations_bind_exact_fixture_bytes_and_complete_panel(self) -> None:
        fixture_bytes = FIXTURES.read_bytes()
        fixtures = json.loads(fixture_bytes)
        observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        self.assertEqual(
            observations["fixture_sha256"], hashlib.sha256(fixture_bytes).hexdigest()
        )
        expected = [sample["id"] for sample in fixtures["samples"]]
        actual = [row["id"] for row in observations["observations"]]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(set(actual)))

    def test_tokenizer_identity_matches_external_manifest(self) -> None:
        observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(observations["tokenizer_sha256"], manifest["sha256"])
        self.assertEqual(observations["model_revision"], manifest["version"])

    def test_recorded_text_units_and_residuals_reconcile(self) -> None:
        fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
        observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        for sample, row in zip(
            fixtures["samples"], observations["observations"], strict=True
        ):
            with self.subTest(sample=sample["id"]):
                self.assertEqual(row["unicode_codepoints"], len(sample["text"]))
                self.assertEqual(row["utf8_bytes"], len(sample["text"].encode("utf-8")))
                self.assertIs(type(row["observed_tokens"]), int)
                self.assertGreaterEqual(row["observed_tokens"], 0)
                self.assertEqual(
                    row["ceil_codepoints_div_4"], math.ceil(len(sample["text"]) / 4)
                )
                self.assertEqual(
                    row["signed_residual_tokens"],
                    row["observed_tokens"] - row["ceil_codepoints_div_4"],
                )
