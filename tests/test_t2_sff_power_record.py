"""Check the per-card power record against its raw nvidia-smi captures.

Claim-to-source integrity only: the record's numbers must be reproducible from
the stored CSV files, the files must be the ones the record names, and the
record must carry none of the banned wording.
"""
import csv
import hashlib
import json
import re
from pathlib import Path
import statistics
import unittest

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "research/T2-infrastructure/measurements"
RECORD = MEASUREMENTS / "rtx-pro-4000-blackwell-sff-power-2026-10-19.json"
IDLE_CSV = MEASUREMENTS / "raw/raw-capture-IDLE-20261019T000959Z.csv"
LOAD_CSV = MEASUREMENTS / "raw/raw-capture-A-20261018T235741Z.csv"
TOLERANCE_W = 0.01
BANNED = ["2x", "dual-card", "two-card"]


def read_rows(path):
    with open(path, newline="") as handle:
        reader = csv.reader(handle)
        header = [cell.strip() for cell in next(reader)]
        return [dict(zip(header, [cell.strip() for cell in row])) for row in reader]


def number(cell):
    return float(cell.split()[0])


def idle_run(rows):
    """Leading rows of GPU 0 with 0 % utilization, 244 MiB and pstate P5."""
    run = []
    for row in (r for r in rows if r["index"] == "0"):
        if (number(row["utilization.gpu [%]"]) == 0
                and row["memory.used [MiB]"] == "244 MiB" and row["pstate"] == "P5"):
            run.append(row)
        else:
            break
    return run


def load_powers(rows, index):
    return [number(r["power.draw [W]"]) for r in rows
            if r["index"] == index and number(r["utilization.gpu [%]"]) >= 80]


class PowerRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = RECORD.read_text()
        cls.record = json.loads(cls.text)
        cls.idle_rows = read_rows(IDLE_CSV)
        cls.load_rows = read_rows(LOAD_CSV)

    def assertClose(self, actual, expected, label):
        self.assertAlmostEqual(actual, expected, delta=TOLERANCE_W,
                               msg="%s: recomputed %s, record says %s" % (label, actual, expected))

    def test_idle_statistics_recompute_from_csv(self):
        run = idle_run(self.idle_rows)
        power = [number(r["power.draw [W]"]) for r in run]
        rec = self.record["idle"]
        self.assertEqual(len(run), rec["samples"], "idle sample count")
        self.assertClose(min(power), rec["power_draw_w"]["min"], "idle min")
        self.assertClose(statistics.mean(power), rec["power_draw_w"]["mean"], "idle mean")
        self.assertClose(statistics.median(power), rec["power_draw_w"]["median"], "idle median")
        self.assertClose(max(power), rec["power_draw_w"]["max"], "idle max")

    def test_idle_rows_never_include_a_loading_model(self):
        run = idle_run(self.idle_rows)
        self.assertTrue(run)
        self.assertEqual({r["pstate"] for r in run}, {"P5"})
        self.assertEqual({r["memory.used [MiB]"] for r in run}, {"244 MiB"})
        excluded = self.record["idle"]["excluded_rows"]
        gpu0 = [r for r in self.idle_rows if r["index"] == "0"]
        self.assertEqual(len(gpu0) - len(run), excluded["count"], "excluded row count")
        self.assertEqual(len(excluded["rows"]), excluded["count"])

    def test_load_series_recompute_from_csv(self):
        sources = {"A_gpu_index_0": (self.load_rows, "0"),
                   "A_gpu_index_1": (self.load_rows, "1"),
                   "IDLE_gpu_index_1": (self.idle_rows, "1")}
        means = []
        for name, (rows, index) in sources.items():
            power = load_powers(rows, index)
            rec = self.record["load"]["series"][name]
            self.assertEqual(len(power), rec["samples_used"], name + " samples used")
            self.assertClose(min(power), rec["min_w"], name + " min")
            self.assertClose(statistics.mean(power), rec["mean_w"], name + " mean")
            self.assertClose(max(power), rec["max_w"], name + " max")
            self.assertEqual(sum(p > 70.0 for p in power), rec["samples_above_limit"], name + " above limit")
            means.append(statistics.mean(power))
        rng = self.record["load"]["range_of_series_means_w"]
        self.assertClose(min(means), rng["low"], "load range low")
        self.assertClose(max(means), rng["high"], "load range high")
        every = [p for rows, index in sources.values() for p in load_powers(rows, index)]
        self.assertClose(max(every), self.record["load"]["max_sample_w"], "load max sample")

    def test_limits_and_identity_match_csv(self):
        rows = self.idle_rows + self.load_rows
        card = self.record["card"]
        self.assertEqual({r["power.limit [W]"] for r in rows}, {"%.2f W" % card["power_limit_w"]})
        self.assertEqual({r["power.min_limit [W]"] for r in rows}, {"%.2f W" % card["power_min_limit_w"]})
        self.assertEqual({r["power.max_limit [W]"] for r in rows}, {"%.2f W" % card["power_max_limit_w"]})
        self.assertEqual({r["driver_version"] for r in rows}, {card["driver"]})
        self.assertEqual({r["vbios_version"] for r in rows}, {card["vbios"]})
        self.assertEqual({r["name"] for r in rows}, {card["name"]})

    def test_csv_hashes_match_record(self):
        listed = {Path(f["path"]).name: f["sha256"] for f in self.record["raw_evidence"]["files"]}
        for path in (IDLE_CSV, LOAD_CSV):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, listed[path.name], "sha256 of " + path.name)
        self.assertEqual(len(listed), 2)

    def test_published_csvs_carry_no_gpu_uuid(self):
        for path in (IDLE_CSV, LOAD_CSV):
            text = path.read_text()
            self.assertNotIn("GPU-", text, "GPU uuid left in " + path.name)
            rows = read_rows(path)
            self.assertEqual(len(rows), 180, path.name)
            self.assertEqual({r["uuid"] for r in rows}, {"REDACTED"}, path.name)

    def test_redaction_is_declared_with_original_hashes(self):
        raw = self.record["raw_evidence"]
        self.assertEqual(raw["redaction"], "uuid column replaced with REDACTED; no other change; "
                         "original_sha256 is the hash of the unredacted capture")
        self.assertNotIn("byte for byte", raw["preservation"])
        for entry in raw["files"]:
            self.assertRegex(entry["original_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotEqual(entry["original_sha256"], entry["sha256"])
            self.assertEqual(entry["bytes"], (ROOT / entry["path"]).stat().st_size, entry["path"])

    def test_datasheet_power_matches_quote_and_driver_limit(self):
        card = self.record["card"]
        quoted = re.findall(r"(\d+)\s*W\b", card["datasheet"]["quote"])
        self.assertEqual(len(quoted), 1, "datasheet quote must hold exactly one 'N W' figure")
        self.assertEqual(card["datasheet_total_board_power_w"], int(quoted[0]), "datasheet figure vs quote")
        self.assertEqual(card["datasheet_total_board_power_w"], card["power_limit_w"], "datasheet figure vs driver limit")

    def test_record_carries_no_banned_wording(self):
        for word in BANNED:
            self.assertNotIn(word, self.text, "banned wording in power record: " + word)

    def test_record_states_observed_wording_and_status(self):
        self.assertEqual(self.record["evidence_disposition"], "unverified_contributor_report")
        self.assertEqual(self.record["load"]["wording"], "observed under inference load")
        for key in ("workload_pinned", "model_pinned", "engine_pinned"):
            self.assertIs(self.record["load"][key], False, key)


if __name__ == "__main__":
    unittest.main()
