"""Synthetic driver-CSV regressions only; no GPU observations or downloads."""

import contextlib
import csv
import hashlib
import importlib.util
import io
import json
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
    def assert_rejected_before_publication(self, csv_text, *,
                                           first_csv=None, error="NVIDIA"):
        for sanitize in (False, True):
            with self.subTest(sanitize=sanitize), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                valid = FIXTURES.synthetic_run()
                if first_csv is not None:
                    valid["hardware"]["nvidia_smi_csv"] = first_csv
                first = FIXTURES.write_synthetic_run(root, valid)
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
                stdout = io.StringIO()
                with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(stdout):
                    with self.assertRaisesRegex(ValueError, error):
                        FIXTURES.SUMMARY.main()
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual([path.read_bytes() for path in paths], before)

    @staticmethod
    def quoted_device_csv(name="Synthetic GPU", *, line_ending="\r\n", reverse=False):
        fields = ["index", "name", "driver_version", "pci.bus_id"]
        values = ["0", name, "synthetic-driver", "00000000:02:00.0"]
        if reverse:
            fields.reverse()
            values.reverse()
        output = io.StringIO(newline="")
        csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator=line_ending).writerows(
            (fields, values))
        return output.getvalue()

    def test_malformed_quoted_headers_reject_before_publication(self):
        row = "0,Synthetic GPU,synthetic-driver,00000000:02:00.0"
        headers = (
            'index,"na"me,driver_version,pci.bus_id',
            'index,name,"driver_"version,pci.bus_id',
            'index,name,driver_version,"pci.bus_"id',
            'index,name,driver_version,"pci.bus_id',
        )
        for header in headers:
            with self.subTest(header=header):
                self.assert_rejected_before_publication(header + "\n" + row)

    def test_malformed_quoted_device_rows_reject_before_publication(self):
        header = "index,name,driver_version,pci.bus_id\n"
        rows = (
            '0,"Synthetic" GPU,synthetic-driver,00000000:02:00.0',
            '0,Synthetic GPU,"synthetic-"driver,00000000:02:00.0',
            '0,Synthetic GPU,synthetic-driver,"00000000:02:"00.0',
            '0,Synthetic GPU,synthetic-driver,"00000000:02:00.0',
        )
        for row in rows:
            with self.subTest(row=row):
                self.assert_rejected_before_publication(header + row)

    def test_embedded_quoted_newlines_remain_distinct_cohort_pins(self):
        endings = ("", "\n", "\r", "\r\n")
        for index, first_ending in enumerate(endings):
            for second_ending in endings[index + 1:]:
                with self.subTest(first=first_ending, second=second_ending):
                    self.assert_rejected_before_publication(
                        self.quoted_device_csv("Synthetic" + second_ending + " GPU"),
                        first_csv=self.quoted_device_csv("Synthetic" + first_ending + " GPU"),
                        error="incompatible measurement cohort")

    def test_valid_quoted_fields_and_record_endings_preserve_raw_pins(self):
        for embedded in ("", "\n", "\r", "\r\n"):
            name = 'Synthetic, "quoted"' + embedded + " GPU"
            for line_ending in ("\n", "\r", "\r\n"):
                for sanitize in (False, True):
                    with self.subTest(embedded=embedded, records=line_ending, sanitize=sanitize), tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        first = FIXTURES.synthetic_run()
                        second = FIXTURES.synthetic_run(2)
                        first["hardware"]["nvidia_smi_csv"] = self.quoted_device_csv(name)
                        second["hardware"]["nvidia_smi_csv"] = self.quoted_device_csv(
                            name, line_ending=line_ending, reverse=True)
                        paths = [FIXTURES.write_synthetic_run(root, run) for run in (first, second)]
                        before = [path.read_bytes() for path in paths]
                        result = FIXTURES.SUMMARY.summarize(root, sanitize=sanitize)
                        self.assertEqual(result["status_counts"], {"success": 2})
                        self.assertEqual(result["comparable_competitor_error_pairs"], 0)
                        for path in paths:
                            published = json.loads(path.read_text(encoding="utf-8"))
                            self.assertEqual(
                                published["hardware"]["nvidia_smi_csv"],
                                first["hardware"]["nvidia_smi_csv"] if path == paths[0]
                                else second["hardware"]["nvidia_smi_csv"])
                            signature = json.loads(FIXTURES.SUMMARY.cohort_signature(published))
                            self.assertEqual(signature["hardware"]["nvidia_devices"][0][1], name)
                        if not sanitize:
                            self.assertEqual([path.read_bytes() for path in paths], before)
                        for item in result["input_checksums"]:
                            self.assertEqual(
                                item["sha256"],
                                hashlib.sha256((root / item["file"]).read_bytes()).hexdigest())

    def test_malformed_quote_rejection_allows_owned_input_correction(self):
        for sanitize in (False, True):
            with self.subTest(sanitize=sanitize), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                first = FIXTURES.write_synthetic_run(root, FIXTURES.synthetic_run())
                invalid = FIXTURES.synthetic_run(2)
                invalid["hardware"]["nvidia_smi_csv"] = (
                    'index,name,driver_version,pci.bus_id\n'
                    '0,Synthetic GPU,synthetic-driver,"00000000:02:00.0')
                second = FIXTURES.write_synthetic_run(root, invalid)
                output = root / "mr09-results-summary.json"
                output.write_bytes(b"synthetic existing summary; preserve verbatim\n")
                paths = (first, second, output)
                before = [path.read_bytes() for path in paths]
                arguments = ["mr09_summarize.py", "--directory", str(root)]
                if sanitize:
                    arguments.append("--sanitize")
                stdout = io.StringIO()
                with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(stdout):
                    with self.assertRaisesRegex(ValueError, "invalid NVIDIA driver/device pins"):
                        FIXTURES.SUMMARY.main()
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual([path.read_bytes() for path in paths], before)
                FIXTURES.write_synthetic_run(root, FIXTURES.synthetic_run(2))
                with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(io.StringIO()):
                    FIXTURES.SUMMARY.main()
                summary = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(summary["run_count"], 2)
                self.assertEqual(summary["status_counts"], {"success": 2})
                self.assertEqual(summary["comparable_competitor_error_pairs"], 0)
                for item in summary["input_checksums"]:
                    self.assertEqual(
                        item["sha256"],
                        hashlib.sha256((root / item["file"]).read_bytes()).hexdigest())

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

    @staticmethod
    def two_device_run(repetition=1, second_index="1",
                       second_bus="00000000:03:00.0"):
        """Two synthetic query rows; this does not authorize a GPU experiment."""
        run = FIXTURES.synthetic_run(repetition)
        run["hardware"]["count"] = 2
        header, row = list(csv.reader(run["hardware"]["nvidia_smi_csv"].splitlines()))
        fields = [name.strip() for name in header]
        second = list(row)
        second[fields.index("index")] = second_index
        second[fields.index("pci.bus_id")] = second_bus
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows((header, row, second))
        run["hardware"]["nvidia_smi_csv"] = output.getvalue()
        return run

    def test_duplicate_device_indices_reject_before_publication_and_allow_recovery(self):
        cases = (("0", "00000000:02:00.0"),
                 ("0", "00000000:03:00.0"),
                 (" \t0\t ", "00000000:03:00.0"))
        for second_index, second_bus in cases:
            for sanitize in (False, True):
                with self.subTest(index=second_index, bus=second_bus, sanitize=sanitize), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    first = FIXTURES.write_synthetic_run(
                        root, FIXTURES.synthetic_run(cell="A-synthetic"))
                    invalid = self.two_device_run(2, second_index, second_bus)
                    second = FIXTURES.write_synthetic_run(root, invalid)
                    output = root / "mr09-results-summary.json"
                    output.write_bytes(b"synthetic existing summary; preserve verbatim\n")
                    paths = (first, second, output)
                    before = [path.read_bytes() for path in paths]
                    arguments = ["mr09_summarize.py", "--directory", str(root)]
                    if sanitize:
                        arguments.append("--sanitize")
                    stdout = io.StringIO()
                    with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(stdout):
                        with self.assertRaisesRegex(ValueError, "duplicate NVIDIA device index"):
                            FIXTURES.SUMMARY.main()
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertEqual([path.read_bytes() for path in paths], before)

                    # An operator may correct this owned synthetic input and retry.
                    FIXTURES.write_synthetic_run(root, self.two_device_run(2))
                    with patch.object(sys, "argv", arguments), contextlib.redirect_stdout(io.StringIO()):
                        FIXTURES.SUMMARY.main()
                    summary = json.loads(output.read_text(encoding="utf-8"))
                    self.assertEqual(summary["run_count"], 2)
                    self.assertEqual(summary["status_counts"], {"success": 2})
                    self.assertEqual(summary["comparable_competitor_error_pairs"], 0)
                    for item in summary["input_checksums"]:
                        self.assertEqual(
                            item["sha256"],
                            hashlib.sha256((root / item["file"]).read_bytes()).hexdigest())

    def test_distinct_indices_with_same_model_memory_and_driver_preserve_cohort(self):
        first = self.two_device_run()
        second = self.two_device_run(2)
        header, row0, row1 = list(csv.reader(second["hardware"]["nvidia_smi_csv"].splitlines()))
        output = io.StringIO()
        csv.writer(output).writerows((header, row1, row0))
        second["hardware"]["nvidia_smi_csv"] = output.getvalue()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [FIXTURES.write_synthetic_run(root, run) for run in (first, second)]
            before = [path.read_bytes() for path in paths]
            result = FIXTURES.SUMMARY.summarize(root)
            self.assertEqual(result["status_counts"], {"success": 2})
            self.assertEqual(result["run_count"], 2)
            self.assertEqual(result["comparable_competitor_error_pairs"], 0)
            self.assertEqual(result["cells"]["D-synthetic"]["phases"]["prefill"]["peak_allocated_bytes"],
                             {"n": 2, "min": 10, "median": 10.0, "max": 10})
            self.assertEqual([path.read_bytes() for path in paths], before)


if __name__ == "__main__":
    unittest.main()
