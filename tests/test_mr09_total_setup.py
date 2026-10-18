"""Synthetic future-log fixtures and real CPU-estimator setup integrity; no GPU."""
import copy
from fractions import Fraction
import hashlib
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
    def reject_setup_mutations(self, mutations):
        """Keep every input byte intact when an altered proposal is rejected."""
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json", "preparation.json", "gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name, directory/name)
            original = json.loads((DIRECTORY/"setup.json").read_text())
            for path, value in mutations:
                changed = copy.deepcopy(original)
                target = changed
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                (directory/"setup.json").write_text(json.dumps(changed))
                before = {p.name: p.read_bytes() for p in directory.iterdir()}
                with self.subTest(path=path, value=value), self.assertRaises(ValueError):
                    MODULE.validate_setup(directory)
                self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})

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

    def test_runtime_workload_and_target_bindings_reject_changes(self):
        self.reject_setup_mutations([
            (("runtime", "offload_layers"), 0), (("runtime", "device"), "CPU"),
            (("runtime", "device"), "CUDA1"), (("runtime", "name"), "another/runtime"),
            (("runtime", "release"), "b11668"), (("runtime", "commit"), "0"*40),
            (("runtime", "planned_archive"), "another-build.zip"),
            (("runtime", "planned_archive_sha256"), "0"*64),
            (("runtime", "planned_cudart_archive"), "another-cudart.zip"),
            (("runtime", "planned_cudart_sha256"), "0"*64),
            (("runtime", "archive_verification"), "synthetic claim of local execution"),
            (("configuration", "mmap"), False), (("configuration", "main_gpu"), 1),
            (("configuration", "warmup"), True), (("configuration", "generation_forwards"), 32),
            (("configuration", "tensor_split"), [0, 1]),
            (("configuration", "logical_batch"), 512), (("configuration", "physical_batch"), 128),
            (("configuration", "kv_key"), "q8_0"), (("configuration", "kv_value"), "q8_0"),
            (("estimator", "name"), "another/estimator"), (("estimator", "version"), "v0.26.3"),
            (("estimator", "commit"), "0"*40),
            (("artifact", "repo"), "another/model"), (("artifact", "revision"), "0"*40),
            (("artifact", "file"), "SmolLM2-135M-Instruct-Q4_K_M.gguf"),
            (("comparison", "estimator_path"), "estimate.items[0].ram.nonuma"),
            (("comparison", "runtime_field"), "fit_memory_breakdown.rows[kind=host].self"),
            (("comparison", "runtime_source_unit"), "bytes"),
            (("comparison", "includes"), ["whole-process peak"]),
            (("comparison", "excludes"), []),
            (("envelope", "preparation_min_gpu_free_mib"), 1),
            (("envelope", "spare_local_only"), False), (("envelope", "paid_compute"), True),
        ])

    def test_numeric_boolean_aliases_rejected_throughout_bound_groups(self):
        original = json.loads((DIRECTORY/"setup.json").read_text())
        mutations = []
        def visit(value, path):
            if type(value) is dict:
                for key, item in value.items(): visit(item, (*path, key))
            elif type(value) is list:
                for index, item in enumerate(value): visit(item, (*path, index))
            elif type(value) is bool:
                mutations.append((path, int(value)))
            elif type(value) is int:
                mutations.append((path, float(value)))
                if value in (0, 1): mutations.append((path, bool(value)))
        for group in ("estimator", "runtime", "configuration", "comparison", "envelope"):
            visit(original[group], (group,))
        self.reject_setup_mutations(mutations)

    def test_missing_or_undeclared_runtime_controls_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json", "preparation.json", "gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name, directory/name)
            original = json.loads((DIRECTORY/"setup.json").read_text())
            for group in ("runtime", "configuration"):
                for key in original[group]:
                    changed = copy.deepcopy(original)
                    del changed[group][key]
                    (directory/"setup.json").write_text(json.dumps(changed))
                    with self.subTest(group=group, key=key), self.assertRaises(ValueError):
                        MODULE.validate_setup(directory)
        self.reject_setup_mutations([(("runtime", "rpc_server"), "synthetic.invalid"),
                                     (("configuration", "kqv_offload"), False)])

    def test_matching_receipt_edits_cannot_replace_reviewed_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            shutil.copyfile(DIRECTORY/"gguf-parser-estimate.json", directory/"gguf-parser-estimate.json")
            for group, key, receipt_key, value in (
                ("artifact", "sha256", "artifact_sha256", "0"*64),
                ("artifact", "bytes", "artifact_bytes", 270885953),
                ("estimator", "windows_exe_sha256", "estimator_exe_sha256", "0"*64),
            ):
                setup = json.loads((DIRECTORY/"setup.json").read_text())
                preparation = json.loads((DIRECTORY/"preparation.json").read_text())
                setup[group][key] = preparation[receipt_key] = value
                (directory/"setup.json").write_text(json.dumps(setup))
                (directory/"preparation.json").write_text(json.dumps(preparation))
                with self.subTest(key=key), self.assertRaises(ValueError): MODULE.validate_setup(directory)

    def test_recorded_command_version_and_exit_status_are_bound(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json", "preparation.json", "gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name, directory/name)
            original = json.loads((DIRECTORY/"preparation.json").read_text())
            argv = copy.deepcopy(original["argv"])
            argv[argv.index("--gpu-layers") + 1] = "0"
            for key, value in (("argv", argv), ("exit_code", False), ("exit_code", 1),
                               ("estimator_version", "gguf-parser.exe version v0.26.3"),
                               ("artifact_bytes", 270885952.0), ("runtime_execution", "success")):
                changed = copy.deepcopy(original)
                changed[key] = value
                (directory/"preparation.json").write_text(json.dumps(changed))
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    MODULE.validate_setup(directory)

    def test_rehashed_effective_output_still_requires_exact_scalar_types(self):
        mutations = [(("estimate", "noMMap"), 0), (("estimate", "flashAttention"), 0),
                     (("metadata", "fileSize"), 270885952.0),
                     (("architecture", "blockCount"), 30.0),
                     (("estimate", "items", 0, "offloadLayers"), 31.0),
                     (("estimate", "items", 0, "fullOffloaded"), 1),
                     (("estimate", "items", 0, "vrams", 0, "position"), False),
                     (("estimate", "items", 0, "vrams", 0, "remote"), 0),
                     (("estimate", "items", 0, "vrams", 0, "handleOutputLayer"), 1)]
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            shutil.copyfile(DIRECTORY/"setup.json", directory/"setup.json")
            original = json.loads((DIRECTORY/"gguf-parser-estimate.json").read_text())
            preparation = json.loads((DIRECTORY/"preparation.json").read_text())
            for path, value in mutations:
                changed = copy.deepcopy(original)
                target = changed
                for key in path[:-1]: target = target[key]
                target[path[-1]] = value
                raw_path = directory/"gguf-parser-estimate.json"
                raw_path.write_text(json.dumps(changed))
                preparation["estimate_sha256"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
                (directory/"preparation.json").write_text(json.dumps(preparation))
                with self.subTest(path=path), self.assertRaises(ValueError): MODULE.validate_setup(directory)

    def test_a_lower_future_cap_remains_an_unqualified_proposal(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in ("setup.json", "preparation.json", "gguf-parser-estimate.json"):
                shutil.copyfile(DIRECTORY/name, directory/name)
            setup = json.loads((directory/"setup.json").read_text())
            setup["envelope"]["future_managed_allocation_cap_bytes"] = 2**30
            (directory/"setup.json").write_text(json.dumps(setup))
            result = MODULE.validate_setup(directory)
            self.assertIs(result["execution_enabled"], False)
            self.assertEqual(result["runtime_observations"], 0)
            self.assertEqual(result["outstanding_gates"], setup["qualification_gates"])

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
