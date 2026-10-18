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

    def test_nonfinite_and_duplicate_event_keys_rejected(self):
        for text in ('{"x":1,"x":1}','{"x":NaN}','{"x":1e999}'):
            with self.subTest(text=text),self.assertRaises(ValueError): capture.loads(text)

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
