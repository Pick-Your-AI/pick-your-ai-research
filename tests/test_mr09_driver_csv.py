"""Synthetic driver-CSV regressions only; no GPU observations or downloads."""

import contextlib
import csv
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "mr09_measure_fixtures", Path(__file__).with_name("test_mr09_measure.py"))
FIXTURES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURES)


class DriverCsvValidationTests(unittest.TestCase):
    def assert_rejected_before_publication(self, csv_text):
        for sanitize in (False, True):
            with self.subTest(sanitize=sanitize), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                first = FIXTURES.write_synthetic_run(root, FIXTURES.synthetic_run())
                invalid = FIXTURES.synthetic_run(2)
                invalid["hardware"]["nvidia_smi_csv"] = csv_text
                second = FIXTURES.write_synthetic_run(root, invalid)
                summary = root / "mr09-results-summary.json"
                summary.write_bytes(b"synthetic existing summary; preserve verbatim\n")
                paths = (first, second, summary)
                before = [path.read_bytes() for path in paths]
                arguments = ["mr09_summarize.py", "--directory", str(root)]
                if sanitize:
                    arguments.append("--sanitize")
                with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(ValueError, "NVIDIA"):
                        FIXTURES.SUMMARY.main()
                self.assertEqual([path.read_bytes() for path in paths], before)

    def test_duplicate_columns_cannot_conceal_driver_identity(self):
        header, row = FIXTURES.synthetic_run()["hardware"]["nvidia_smi_csv"].splitlines()
        for duplicate in (" driver_version", "driver_version", '"\tdriver_version\t"'):
            for first_driver in ("synthetic-driver", "contradictory-driver"):
                with self.subTest(duplicate=duplicate, first_driver=first_driver):
                    self.assert_rejected_before_publication(
                        header + "," + duplicate + "\n"
                        + row.replace("synthetic-driver", first_driver)
                        + ", synthetic-driver")

    def test_duplicate_optional_and_blank_columns_are_ambiguous(self):
        header, row = FIXTURES.synthetic_run()["hardware"]["nvidia_smi_csv"].splitlines()
        for extra_header in ("memory.used [MiB]", "", " \t "):
            with self.subTest(extra_header=extra_header):
                self.assert_rejected_before_publication(
                    header + "," + extra_header + "\n" + row + ", 1 MiB")

    def test_unique_reordered_columns_preserve_the_measurement_cohort(self):
        first = FIXTURES.synthetic_run()
        second = FIXTURES.synthetic_run(2)
        header, row = list(csv.reader(first["hardware"]["nvidia_smi_csv"].splitlines()))
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL)
        writer.writerow([key.strip() for key in reversed(header)])
        writer.writerow([value.strip() for value in reversed(row)])
        second["hardware"]["nvidia_smi_csv"] = csv_buffer.getvalue()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [FIXTURES.write_synthetic_run(root, run) for run in (first, second)]
            before = [path.read_bytes() for path in paths]
            result = FIXTURES.SUMMARY.summarize(root)
            self.assertEqual(result["status_counts"], {"success": 2})
            self.assertEqual([path.read_bytes() for path in paths], before)


if __name__ == "__main__":
    unittest.main()
