"""Offline reporter regressions using explicitly synthetic copies of H1 records.

These tests never launch a native process, query a driver or create measurements.
The committed historical cohort and its thirteen-file freeze are read-only.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import mr09_local_compare_report as reporter
finally:
    sys.path.pop(0)

COHORT = Path("research/market/measurements/local-comparison-2026-10-19")
TOTAL = 300885760
WINNER = 25460736
OTHER_TERMS = 275425024


class LocalCompareReporterTests(unittest.TestCase):
    @contextmanager
    def cohort(self, computation, *, estimate=TOTAL):
        """Rebind only a synthetic prediction and its dependent file receipts.

        Real hash, chronology, placement and native-readback validators still run.
        This permits the arithmetic tests to reach the raw operand boundary without
        disabling file integrity checks or changing the archived source records.
        """
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            directory = base / COHORT
            freeze = reporter.read_json(ROOT / COHORT / "prediction-freeze.json")
            paths = set(freeze["files"])
            paths.add((COHORT / "prediction-freeze.json").as_posix())
            paths.add((COHORT / "runtime-artifacts.json").as_posix())
            for repetition in (1, 2, 3):
                paths.add((COHORT / f"H1-r{repetition}.json").as_posix())
                paths.add((COHORT / f"H1-r{repetition}-preflight.json").as_posix())
            for relative in sorted(paths):
                target = base / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)

            def write(path, value):
                path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n",
                                encoding="utf-8")

            prediction_path = base / freeze["prediction_file"]
            prediction = reporter.read_json(prediction_path)
            prediction["estimate"]["devices"][1]["computation"].update(computation)
            write(prediction_path, prediction)
            prediction_sha = reporter.sha(prediction_path)
            receipt_path = directory / "prediction-receipt.json"
            receipt = reporter.read_json(receipt_path)
            receipt["raw_prediction_sha256"] = prediction_sha
            receipt["managed_device_estimate_bytes"] = estimate
            write(receipt_path, receipt)
            freeze["managed_device_estimate_bytes"] = estimate
            freeze["files"] = {relative: reporter.sha(base / relative)
                               for relative in freeze["files"]}
            freeze_path = directory / "prediction-freeze.json"
            write(freeze_path, freeze)
            for repetition in (1, 2, 3):
                record_path = directory / f"H1-r{repetition}.json"
                record = reporter.read_json(record_path)
                record["prediction_sha256"] = prediction_sha
                record["prediction_freeze_sha256"] = reporter.sha(freeze_path)
                write(record_path, record)
            with mock.patch.object(reporter, "ROOT", base):
                yield directory

    def assert_estimate(self, directory, expected):
        result = reporter.summarize(directory)
        self.assertEqual(result["predicted_managed_device_bytes"], expected)
        self.assertEqual([row["predicted_managed_device_bytes"]
                          for row in result["observations"]], [expected] * 3)
        self.assertEqual(result["configuration_count"], 1)
        self.assertEqual(result["technical_matched_pairs"], 3)
        self.assertEqual(result["accepted_pairs"], 0)
        self.assertEqual(result["whole_runtime_peak_pairs"], 0)
        self.assertIsNone(result["tolerance"])
        self.assertIsNone(result["fit_verdict"])

    @contextmanager
    def copied_captured_cohort(self):
        """Copy receipts for synthetic mutation; use all real report checks."""
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "synthetic-cohort"
            shutil.copytree(ROOT / COHORT, directory)
            yield directory

    def test_captured_cohort_report_remains_byte_exact_without_native_calls(self):
        expected = (ROOT / COHORT / "comparison-summary.json").read_bytes()
        with mock.patch("subprocess.Popen", side_effect=AssertionError("no child permitted")):
            actual = reporter.summarize(ROOT / COHORT)
        self.assertEqual((json.dumps(actual, indent=2, allow_nan=False) + "\n").encode(),
                         expected)
        self.assertEqual(actual["predicted_managed_device_bytes"], TOTAL)

    def test_discarded_graph_numeric_values_are_rejected(self):
        for value in (False, True, -1, -(2**64), 0.0, 0.5, 2162688.0):
            with self.subTest(value=value, kind=type(value).__name__):
                with self.cohort({"graph": value}) as directory:
                    with self.assertRaisesRegex(ValueError, "exact integer byte terms required"):
                        reporter.summarize(directory)

    def test_discarded_output_numeric_values_are_rejected(self):
        for value in (False, True, -1, -(2**64), 0.0, 0.5, 2162688.0):
            with self.subTest(value=value, kind=type(value).__name__):
                with self.cohort({"graph": WINNER, "output": value}) as directory:
                    with self.assertRaisesRegex(ValueError, "exact integer byte terms required"):
                        reporter.summarize(directory)

    def test_non_numeric_raw_operands_raise_explicit_validation_error(self):
        for field in ("graph", "output"):
            for value in (None, "0", [], {}, [0]):
                with self.subTest(field=field, value=value):
                    with self.cohort({"graph": WINNER, "output": WINNER,
                                      field: value}) as directory:
                        with self.assertRaisesRegex(ValueError, "exact integer byte terms required"):
                            reporter.summarize(directory)

    def test_uint64_overflow_raw_operands_are_rejected(self):
        for field in ("graph", "output"):
            for value in (2**64, 2**64 + 1):
                with self.subTest(field=field, value=value):
                    with self.cohort({field: value}) as directory:
                        with self.assertRaisesRegex(ValueError, "exact integer byte terms required"):
                            reporter.summarize(directory)

    def test_zero_equality_and_either_winner_keep_one_maximum_term(self):
        for graph, output, expected in ((0, 0, OTHER_TERMS),
                                        (0, WINNER, TOTAL),
                                        (WINNER, 0, TOTAL),
                                        (WINNER, WINNER, TOTAL),
                                        (2162688, WINNER, TOTAL),
                                        (WINNER, 2162688, TOTAL)):
            with self.subTest(graph=graph, output=output):
                with self.cohort({"graph": graph, "output": output},
                                  estimate=expected) as directory:
                    self.assert_estimate(directory, expected)

    def test_maximum_uint64_operands_keep_existing_exact_python_sum(self):
        largest = 2**64 - 1
        for graph, output in ((largest, 0), (0, largest), (largest, largest)):
            with self.subTest(graph=graph, output=output):
                with self.cohort({"graph": graph, "output": output},
                                  estimate=OTHER_TERMS + largest) as directory:
                    self.assert_estimate(directory, OTHER_TERMS + largest)

    def test_unbound_prediction_edit_keeps_artifact_drift_precedence(self):
        with self.cohort({}) as directory:
            path = directory / "estimator-prediction.json"
            prediction = reporter.read_json(path)
            prediction["estimate"]["devices"][1]["computation"]["graph"] = False
            path.write_text(json.dumps(prediction), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "artifact drift"):
                reporter.summarize(directory)

    def test_cohort_prediction_identity_still_binds_after_valid_arithmetic(self):
        with self.cohort({}) as directory:
            path = directory / "H1-r1.json"
            record = reporter.read_json(path)
            record["prediction_sha256"] = "0" * 64
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cohort identity drift"):
                reporter.summarize(directory)

    def test_other_computation_terms_keep_exact_integer_validation(self):
        for field in ("footprint", "input"):
            with self.subTest(field=field):
                with self.cohort({field: True}) as directory:
                    with self.assertRaisesRegex(ValueError, "exact integer byte terms required"):
                        reporter.summarize(directory)

    def test_declared_total_still_matches_the_single_maximum_aggregation(self):
        with self.cohort({}, estimate=TOTAL + 1) as directory:
            with self.assertRaisesRegex(ValueError, "prediction aggregation drift"):
                reporter.summarize(directory)

    def test_native_receipt_rejects_boolean_and_float_aliases_in_every_trial(self):
        for repetition in (1, 2, 3):
            for field in ("exact_admitted_live_buffer_bytes", "native_self_byte_interval",
                          "cap_bytes", "cleanup_live_bytes", "model_graph_dispatches"):
                aliases = ("float", "bool") if field in ("cleanup_live_bytes", "model_graph_dispatches") else ("float",)
                for alias in aliases:
                    with self.subTest(repetition=repetition, field=field, alias=alias):
                        with self.copied_captured_cohort() as directory:
                            path = directory / f"H1-r{repetition}.json"
                            record = reporter.read_json(path)
                            value = record["native_validation"][field]
                            record["native_validation"][field] = (
                                False if alias == "bool" else
                                [float(item) for item in value] if isinstance(value, list) else float(value))
                            path.write_text(json.dumps(record), encoding="utf-8")
                            with self.assertRaisesRegex(ValueError, "native validation receipt drift"):
                                reporter.summarize(directory)

    def test_native_receipt_member_order_is_irrelevant_and_correction_recovers(self):
        with self.copied_captured_cohort() as directory:
            path = directory / "H1-r1.json"
            original = reporter.read_json(path)
            reordered = dict(original)
            reordered["native_validation"] = dict(reversed(list(original["native_validation"].items())))
            path.write_text(json.dumps(reordered), encoding="utf-8")
            self.assert_estimate(directory, TOTAL)
            changed = reporter.read_json(path)
            changed["native_validation"]["cleanup_live_bytes"] = False
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "native validation receipt drift"):
                reporter.summarize(directory)
            path.write_text(json.dumps(reordered), encoding="utf-8")
            self.assert_estimate(directory, TOTAL)

    def test_native_receipt_structure_and_interval_order_still_reject(self):
        for change in ("missing", "extra", "interval_order"):
            with self.subTest(change=change), self.copied_captured_cohort() as directory:
                path = directory / "H1-r1.json"
                record = reporter.read_json(path)
                if change == "missing":
                    del record["native_validation"]["cleanup_live_bytes"]
                elif change == "extra":
                    record["native_validation"]["extra"] = 0
                else:
                    record["native_validation"]["native_self_byte_interval"].reverse()
                path.write_text(json.dumps(record), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "native validation receipt drift"):
                    reporter.summarize(directory)


if __name__ == "__main__":
    unittest.main()
