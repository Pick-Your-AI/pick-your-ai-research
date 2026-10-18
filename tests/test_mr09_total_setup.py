"""Synthetic future-log fixtures and real CPU-estimator setup integrity; no GPU."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/mr09_total_memory_setup.py"
SPEC = importlib.util.spec_from_file_location("mr09_total_setup",SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
DIRECTORY = ROOT / MODULE.DIRECTORY

def synthetic_event():
    return {"metric":"managed_device_buffers_snapshot","no_alloc":False,"unit":"MiB",
            "rows":[{"kind":"device","name":"CUDA0","self":275,"model":256,"context":11,"compute":8}]}

class NativeMeasurementSemantics(unittest.TestCase):
    def test_floor_resolution_is_preserved(self):
        self.assertEqual(MODULE.managed_snapshot_interval(synthetic_event()),(275*2**20,276*2**20-1))

    def test_self_is_not_reconstructed_from_rounded_components(self):
        event = synthetic_event()
        event["rows"][0]["self"] = 277
        self.assertEqual(MODULE.managed_snapshot_interval(event)[0],277*2**20)
        event["rows"][0]["self"] = 278
        with self.assertRaises(ValueError): MODULE.managed_snapshot_interval(event)

    def test_no_alloc_or_peak_cannot_be_promoted(self):
        for key,value in (("no_alloc",True),("metric","peak_allocated_bytes"),("unit","GB")):
            event = synthetic_event()
            event[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): MODULE.managed_snapshot_interval(event)

    def test_single_device_and_integer_counter_required(self):
        event = synthetic_event()
        event["rows"].append(copy.deepcopy(event["rows"][0]))
        with self.assertRaises(ValueError): MODULE.managed_snapshot_interval(event)
        for value in (True,-1,0,275.0):
            event = synthetic_event()
            event["rows"][0]["self"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): MODULE.managed_snapshot_interval(event)

    def test_error_interval_uses_positive_measured_endpoints(self):
        result = MODULE.error_interval(110,(100,120))
        self.assertEqual(result["signed_bytes"],[-10,10])
        self.assertEqual(result["absolute_bytes"],[0,10])
        self.assertEqual([Fraction(x) for x in result["signed_relative_percent_exact"]],[Fraction(-25,3),Fraction(10)])

    def test_unavailable_measurement_does_not_give_zero_error(self):
        for measured in ((0,1),(120,100),(-1,2)):
            with self.subTest(measured=measured), self.assertRaises(ValueError): MODULE.error_interval(110,measured)

class PreparedSetupIntegrity(unittest.TestCase):
    def test_real_cpu_only_setup_remains_unexecuted(self):
        result = MODULE.validate_setup(DIRECTORY)
        self.assertEqual(result["estimated_managed_device_bytes"],288499968)
        self.assertFalse(result["execution_enabled"])
        self.assertEqual(result["runtime_observations"],0)
        self.assertEqual(result["total_buffer_pairs"],0)
        self.assertEqual(result["whole_process_peak_pairs"],0)

    def test_workload_platform_or_execution_drift_rejected(self):
        mutations = [("configuration","context_capacity",1024),
                     ("configuration","active_sequences",2),
                     ("estimator","platform_footprint_mib",[150,250]),
                     ("runtime","auto_fit",True),
                     ("envelope","future_managed_allocation_cap_bytes",3*2**30),
                     ("comparison","whole_process_peak_equivalent",True),
                     ("comparison","total_buffer_pair_count",1)]
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json","preparation.json","gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name,directory/name)
            original = json.loads((DIRECTORY/"setup.json").read_text())
            for group,key,value in mutations:
                changed = copy.deepcopy(original)
                changed[group][key] = value
                (directory/"setup.json").write_text(json.dumps(changed))
                with self.subTest(key=key), self.assertRaises(ValueError): MODULE.validate_setup(directory)
            original["execution_enabled"] = True
            (directory/"setup.json").write_text(json.dumps(original))
            with self.assertRaises(ValueError): MODULE.validate_setup(directory)

    def test_every_declared_setup_binding_is_frozen_with_exact_types(self):
        original = json.loads((DIRECTORY/"setup.json").read_text())
        def leaves(value, trail=()):
            if isinstance(value,dict):
                for k,v in value.items():
                    if k != "prepared_utc": yield from leaves(v,trail+(k,))
            elif isinstance(value,list):
                for k,v in enumerate(value): yield from leaves(v,trail+(k,))
            else: yield trail,value
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json","preparation.json","gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name,directory/name)
            for trail,value in leaves(original):
                changed = copy.deepcopy(original)
                cursor = changed
                for key in trail[:-1]: cursor = cursor[key]
                replacement = (not value if type(value) is bool else
                               True if type(value) is int and value == 1 else
                               value+1 if type(value) is int else
                               "synthetic-binding-drift")
                cursor[trail[-1]] = replacement
                (directory/"setup.json").write_text(json.dumps(changed))
                with self.subTest(trail=trail),self.assertRaises(ValueError): MODULE.validate_setup(directory)

    def test_preparation_exit_version_and_actual_command_are_bound(self):
        original = json.loads((DIRECTORY/"preparation.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json","preparation.json","gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name,directory/name)
            mutations = []
            for key,value in (("exit_code",1),("exit_code",False),("estimator_version","synthetic-wrong-version")):
                changed=copy.deepcopy(original);changed[key]=value;mutations.append(changed)
            changed=copy.deepcopy(original)
            changed["argv"][changed["argv"].index("--cache-type-k")+1]="q4_0"
            mutations.append(changed)
            for changed in mutations:
                (directory/"preparation.json").write_text(json.dumps(changed))
                with self.assertRaises(ValueError): MODULE.validate_setup(directory)

    def test_duplicate_nonfinite_inputs_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"synthetic.json"
            for raw in ('{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}','{"a":1e999}'):
                path.write_text(raw)
                with self.subTest(raw=raw), self.assertRaises(ValueError): MODULE.strict_json(path)

    def test_estimator_hash_change_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json","preparation.json","gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name,directory/name)
            with (directory/"gguf-parser-estimate.json").open('a') as output: output.write(' ')
            with self.assertRaises(ValueError): MODULE.validate_setup(directory)

if __name__ == "__main__": unittest.main()
