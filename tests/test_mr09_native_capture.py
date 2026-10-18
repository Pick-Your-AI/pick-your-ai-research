"""Real qualification-record integrity and synthetic capture rejection fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
try:
    import mr09_native_capture as capture
finally:
    sys.path.pop(0)
DIRECTORY=ROOT/capture.DIRECTORY

class NativeCaptureTests(unittest.TestCase):
    def setUp(self): self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
    def mutate_event(self,key,value,field,new_value):
        events=[json.loads(l) for l in self.record["stdout"].splitlines()]
        event=next(e for e in events if e.get(key)==value)
        event[field]=new_value
        self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"

    def test_committed_qualification_recomputes(self):
        actual=capture.summarize(DIRECTORY)
        expected=json.loads((DIRECTORY/"qualification-summary.json").read_text())
        self.assertEqual(actual,expected)
        self.assertEqual(actual["initialization_trials"],3)
        self.assertEqual(actual["accepted_estimator_pairs"],0)
        self.assertEqual({r["exact_admitted_live_buffer_bytes"] for r in actual["observations"]},{334511360})
        self.assertTrue(all(r["cleanup_live_bytes"]==0 for r in actual["observations"]))

    def test_no_alloc_and_effective_type_aliases_rejected(self):
        for field,value in (("no_alloc",True),("sequences",True),("generation_forwards",1),("extra_buffer_types",True)):
            self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
            self.mutate_event("mr09_event","effective",field,value)
            with self.subTest(field=field),self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_cap_or_graph_attempt_drift_rejected(self):
        for field,value in (("live_bytes",3*2**30),("graph_denials",2),("admission_denials",2)):
            self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
            events=[json.loads(l) for l in self.record["stdout"].splitlines()]
            next(e for e in events if e.get("stage")=="before_capture")[field]=value
            self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
            with self.subTest(field=field),self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_duplicate_capture_event_rejected(self):
        line=next(l for l in self.record["stdout"].splitlines() if 'fit_memory_breakdown' in l)
        self.record["stdout"]+=line+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_native_rounding_must_reconcile_with_live_ledger(self):
        events=[json.loads(l) for l in self.record["stdout"].splitlines()]
        event=next(e for e in events if e.get("type")=="fit_memory_breakdown")
        event["data"]["rows"][0]["self"]=318
        self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_mixed_hardware_cohort_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
            path=dest/"init-r2.json";record=json.loads(path.read_text())
            record["driver_csv"]=record["driver_csv"].replace('610.88','synthetic-other-driver')
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError): capture.summarize(dest)

    def test_failed_publication_keeps_all_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
            path=dest/"init-r3.json";record=json.loads(path.read_text());record["exit_code"]=1
            path.write_text(json.dumps(record))
            before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
            with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
            self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
            self.assertFalse((Path(temp)/"archive").exists())

    def test_consistently_changed_pins_or_command_rejected(self):
        for field,value in (("model_sha256","0"*64),("harness_git_ref","0"*40),
                            ("launcher_sha256","0"*64),("argv",["synthetic-other-command"])):
            with self.subTest(field=field),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                for path in dest.glob("init-r?.json"):
                    record=json.loads(path.read_text());record[field]=value
                    path.write_text(json.dumps(record))
                with self.assertRaises(ValueError): capture.summarize(dest)

    def test_nonfinite_and_duplicate_event_keys_rejected(self):
        for text in ('{"x":1,"x":1}','{"x":NaN}','{"x":1e999}'):
            with self.subTest(text=text),self.assertRaises(ValueError): capture.loads(text)

    def test_driver_csv_ambiguity_rejected_but_quoted_reordering_supported(self):
        original=self.record["driver_csv"]
        for text in (
            original.replace("driver_version,", "driver_version,driver_version,").replace("610.88,", "conflicting,610.88,"),
            original.replace("driver_version,", "driver_version, driver_version ,").replace("610.88,", "conflicting,610.88,"),
            original.replace("name,", "name, ,").replace("NVIDIA", "value,NVIDIA",1),
            original+",extra",
        ):
            with self.subTest(text=text),self.assertRaises(ValueError): capture.driver_readback(text)
        reordered='"memory.free [MiB]","driver_version","name","memory.total [MiB]"\n"10134 MiB","610.88","NVIDIA, synthetic quoted name","16303 MiB"'
        parsed=capture.driver_readback(reordered)
        self.assertEqual(parsed["name"],"NVIDIA, synthetic quoted name")
        self.assertEqual(parsed["driver_version"],"610.88")

    def test_rehashed_invalid_preflights_rejected_without_publication(self):
        def set_nested(record,group,key,value): record[group][key]=value
        cases=[
            lambda r:r.update(guards={}),
            lambda r:r.update(status="blocked"),
            lambda r:set_nested(r,"observed","available_host_ram_bytes",1),
            lambda r:set_nested(r,"guards","available_host_ram_bytes",1),
            lambda r:set_nested(r,"observed","available_host_ram_bytes",float(r["observed"]["available_host_ram_bytes"])),
            lambda r:set_nested(r,"thresholds","available_host_ram_bytes",1),
            lambda r:r.update(methods=[]),
            lambda r:r.update(observed_utc="2026-10-19T00:00:00+00:00"),
            lambda r:r.update(observed_utc="2026-10-18T06:40:00+00:00"),
            lambda r:set_nested(r,"observed","nvidia_smi_free_mib",999999),
        ]
        for index,change in enumerate(cases):
            with self.subTest(case=index),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                preflight=dest/"init-r1-preflight.json";screen=json.loads(preflight.read_text())
                change(screen);preflight.write_text(json.dumps(screen))
                path=dest/"init-r1.json";record=json.loads(path.read_text())
                record["preflight_sha256"]=capture.sha(preflight);path.write_text(json.dumps(record))
                before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
                with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
                self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
                self.assertFalse((Path(temp)/"archive").exists())

    def test_capture_cannot_move_after_cleanup(self):
        lines=self.record["stdout"].splitlines()
        line=next(l for l in lines if 'fit_memory_breakdown' in l)
        lines.remove(line);lines.append(line)
        self.record["stdout"]="\n".join(lines)+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_cleanup_peak_cannot_decrease(self):
        events=[json.loads(l) for l in self.record["stdout"].splitlines()]
        next(e for e in events if e.get("stage")=="after_cleanup")["peak_admitted_bytes"]=8388608
        self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_native_discovery_requires_typed_sufficient_consistent_bytes(self):
        for field,value in (("cuda_reported_free_bytes",0),("cuda_reported_free_bytes",2**65),
                            ("driver_total_bytes",17094475776.0),("cuda_reported_free_bytes",True)):
            self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
            self.mutate_event("mr09_event","qualification",field,value)
            with self.subTest(field=field,value=value),self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_native_capture_capacity_matches_discovery(self):
        for field,value in (("total",1),("total",16302.0),("total",True),
                            ("free",-1),("free",20000),("free",14717.0)):
            with self.subTest(field=field,value=value),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                path=dest/"init-r1.json";record=json.loads(path.read_text())
                events=[json.loads(line) for line in record["stdout"].splitlines()]
                event=next(e for e in events if e.get("type")=="fit_memory_breakdown")
                event["data"]["rows"][0][field]=value
                record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
                path.write_text(json.dumps(record))
                before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
                with self.assertRaises(ValueError): capture.summarize(dest)
                with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
                self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
                self.assertFalse((Path(temp)/"archive").exists())

    def test_rehashed_overlapping_trials_cannot_count_as_serial(self):
        for mode in ("overlap","reused_screen"):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                first=json.loads((dest/"init-r1.json").read_text())
                path=dest/"init-r2.json";second=json.loads(path.read_text())
                preflight=dest/second["preflight_file"]
                screen=json.loads(preflight.read_text())
                if mode=="overlap":
                    screen["observed_utc"]=json.loads((dest/"init-r1-preflight.json").read_text())["observed_utc"]
                    second["started_utc"]=first["started_utc"]
                    second["finished_utc"]=first["finished_utc"]
                else:
                    # Still within the existing 30-second freshness bound, but
                    # obtained before the preceding child had finished.
                    screen["observed_utc"]=first["started_utc"]
                    second["started_utc"]="2026-10-18T06:45:50+00:00"
                    second["finished_utc"]="2026-10-18T06:45:51+00:00"
                preflight.write_text(json.dumps(screen))
                second["preflight_sha256"]=capture.sha(preflight)
                path.write_text(json.dumps(second))
                before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
                with self.assertRaises(ValueError): capture.summarize(dest)
                with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
                self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
                self.assertFalse((Path(temp)/"archive").exists())

    def test_native_quota_portable_cpu_selftest(self):
        compiler=shutil.which("g++")
        if not compiler: self.skipTest("portable compiler absent; MSVC execution separately recorded")
        with tempfile.TemporaryDirectory() as temp:
            exe=Path(temp)/"quota-test"
            subprocess.run([compiler,"-std=c++17","-pthread","-UNDEBUG","-I",str(ROOT/"research/market/measurements/native"),str(ROOT/"tests/native/mr09_quota_selftest.cpp"),"-o",str(exe)],check=True,capture_output=True)
            result=json.loads(subprocess.check_output([str(exe)],text=True))
            self.assertEqual(result["concurrent_admissions"],16000)
            self.assertEqual(result["boundary_denials"],2)
            self.assertEqual(result["final_live_bytes"],0)

if __name__=="__main__":unittest.main()
