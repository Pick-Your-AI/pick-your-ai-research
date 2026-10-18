"""Existing real records plus synthetic rejection fixtures; no GPU execution."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
try:
    import mr09_output_reservation as audit
finally:
    sys.path.pop(0)


class OutputReservationTests(unittest.TestCase):
    def record(self):
        return json.loads((ROOT/"research/market/measurements/native-qualification-2026-10-18/init-r1.json").read_text())

    def test_bound_report_recomputes_and_rejects_error_admission(self):
        result = audit.analyze()
        published = json.loads((ROOT/audit.DIRECTORY/"matching-report.json").read_text())
        audit.validate_published(result, published)
        self.assertTrue(result["reservation_count_match"])
        self.assertFalse(result["numerical_error_comparison_admitted"])
        self.assertEqual(result["accepted_estimator_pairs"], 0)
        for key, value in (("numerical_error_comparison_admitted", True),
                           ("accepted_estimator_pairs", 1), ("accepted_estimator_pairs", False)):
            changed = copy.deepcopy(published); changed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                audit.validate_published(result, changed)

    def test_host_readback_is_separate_from_graph_capacity(self):
        result = audit.runtime_readback(self.record())
        self.assertEqual(result["prompt_graph"]["outputs"], 256)
        self.assertEqual(result["n_outputs_max_per_seq"], 1)
        self.assertEqual(result["observed_host_output_mib_text"], "0.19")
        self.assertEqual(result["host_output_rounding_enclosure_mib"], ["0.185", "0.195"])

    def test_ambiguous_or_changed_runtime_reservation_rejected(self):
        original = self.record()
        for old, new in (("output buffer size =     0.19", "output buffer size =    48.56"),
                         ("n_outputs_max         = 256", "n_outputs_max         = 1"),
                         ("n_outputs_max_per_seq = 1", "n_outputs_max_per_seq = 256")):
            record = copy.deepcopy(original)
            self.assertIn(old, record["stderr"])
            record["stderr"] = record["stderr"].replace(old, new)
            with self.subTest(old=old), self.assertRaises(ValueError): audit.runtime_readback(record)
        original["stderr"] += "llama_context: n_outputs_max = 256\n"
        with self.assertRaises(ValueError): audit.runtime_readback(original)

    def test_historical_or_source_audit_edits_fail_before_reanalysis(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in audit.INPUT_SHA256:
                dest = root/relative; dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/relative, dest)
            for relative in (next(iter(audit.INPUT_SHA256)), str(audit.DIRECTORY/"source-audit.json")):
                path = root/relative; original = path.read_bytes()
                path.write_bytes(original+b" ")
                with self.subTest(relative=relative), self.assertRaises(ValueError): audit.analyze(root)
                path.write_bytes(original)

    def test_external_source_verification_rejects_full_and_fragment_drift(self):
        # Entire fixture is synthetic and temporary, never research evidence.
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"synthetic.txt"; path.write_bytes(b"first\nsecond\n")
            item = {"file":path.name, "bytes":path.stat().st_size,
                    "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                    "inspected_fragments":[{"lines":[2,2], "sha256":hashlib.sha256(b"second\n").hexdigest()}]}
            audit.verify_source_copies(Path(temp), {"files":[item]})
            item["inspected_fragments"][0]["sha256"] = "0"*64
            with self.assertRaises(ValueError): audit.verify_source_copies(Path(temp), {"files":[item]})
            item["sha256"] = "0"*64
            with self.assertRaises(ValueError): audit.verify_source_copies(Path(temp), {"files":[item]})


if __name__ == "__main__":
    unittest.main()
