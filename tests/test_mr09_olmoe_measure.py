"""Synthetic OLMoE admission/workload tests. They execute no real ML model or GPU."""
from contextlib import nullcontext
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
import uuid
import io
from contextlib import redirect_stdout
from unittest.mock import patch, Mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mr09_olmoe_artifacts as a
import mr09_olmoe_measure as m

NOW = datetime(2026, 10, 20, 6, tzinfo=timezone.utc)
UUID = "GPU-00000000-0000-0000-0000-000000000001"


class Tensor:
    def __init__(self, elements, *, dtype="bf16", device="cuda"):
        self.elements = elements
        self.dtype = dtype
        self.device = SimpleNamespace(type=device)

    def numel(self):
        return self.elements

    def element_size(self):
        return 2


class Inputs:
    def __init__(self, rows):
        self.shape = (len(rows), len(rows[0]))

    def __getitem__(self, index):
        stop = index[1].stop
        return Inputs([[7] * min(stop, self.shape[1]) for _ in range(self.shape[0])])


class Logits:
    def __init__(self, batch):
        self.batch = batch

    def __getitem__(self, index):
        return self

    def argmax(self, **kwargs):
        return Inputs([[7] for _ in range(self.batch)])


class Cache:
    def __init__(self, **kwargs):
        self.positions = 0
        self.layers = []

    def get_seq_length(self):
        return self.positions


class Model:
    def __init__(self, plan):
        self.config = SimpleNamespace(
            num_hidden_layers=16, hidden_size=2048, num_attention_heads=16,
            num_key_value_heads=16, num_experts=64, num_experts_per_tok=8,
            intermediate_size=1024, vocab_size=50304, max_position_embeddings=4096,
            _attn_implementation="sdpa", _experts_implementation="eager")
        self.parameter = Tensor(6919161856, device="cpu")
        self.calls = []
        self.transfers = []

    def parameters(self):
        return iter([self.parameter])

    def eval(self):
        return self

    def to(self, target):
        self.transfers.append(target)
        self.parameter.device.type = "cuda"
        return self

    def __call__(self, *, input_ids, past_key_values, use_cache, logits_to_keep):
        assert use_cache is True and logits_to_keep == 1
        self.calls.append((input_ids.shape, past_key_values, past_key_values.positions))
        past_key_values.positions += input_ids.shape[1]
        elements = input_ids.shape[0] * past_key_values.positions * 16 * 128
        past_key_values.layers = [
            SimpleNamespace(keys=Tensor(elements), values=Tensor(elements)) for _ in range(16)]
        return SimpleNamespace(logits=Logits(input_ids.shape[0]))


class Cuda:
    def __init__(self):
        self.fractions = []
        self.empties = 0

    def is_available(self): return True
    def device_count(self): return 1
    def init(self): pass
    def synchronize(self): pass
    def reset_peak_memory_stats(self): pass
    def mem_get_info(self, index=0): return (40 * m.GIB, 48 * m.GIB)
    def get_allocator_backend(self): return "native"
    def get_device_properties(self, index):
        return SimpleNamespace(uuid=SimpleNamespace(bytes=list(uuid.UUID(UUID[4:]).bytes)),
                               total_memory=48 * m.GIB)
    def set_per_process_memory_fraction(self, fraction, index): self.fractions.append((fraction, index))
    def memory_allocated(self): return 100
    def memory_reserved(self): return 200
    def max_memory_allocated(self): return 300
    def max_memory_reserved(self): return 400
    def empty_cache(self): self.empties += 1


def fake_torch():
    return SimpleNamespace(__version__="2.10.0+cu130", cuda=Cuda(), bfloat16="bf16", long="long",
                           tensor=lambda rows, **kwargs: Inputs(rows),
                           inference_mode=nullcontext, manual_seed=lambda value: None)


class MeasureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="olmoe-run-synthetic-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / "model"
        self.directory.mkdir()
        self.output = self.root / "M1-r1.json"
        self.plan = a.load_plan()
        self.runtime = {"classification": "synthetic runtime identity; no actual installed ML"}
        self.device = {"uuid": UUID, "driver_total_bytes": 48 * m.GIB,
                       "gpu_allocator_cap_bytes": 16 * m.GIB,
                       "gpu_workspace_allowance_bytes": m.GIB, "gpu_spare_bytes": 2 * m.GIB}

    def admission(self):
        return {"schema_version": "mr09-olmoe-run-admission/v1",
                "authorization_reference": "synthetic offline fixture, not actual permission",
                "valid_until_utc": "2099-01-01T00:00:00Z",
                "model_id": a.MODEL_ID, "revision": a.REVISION, "plan_sha256": a.PLAN_SHA256,
                "scripts_sha256": m.source_identity(), "runtime": copy.deepcopy(self.runtime),
                "cell": "M1", "repetition": 1, "output_file": "M1-r1.json",
                "device": copy.deepcopy(self.device)}

    def admit(self, value, **kwargs):
        return m.validate_admission(value, self.plan, m.cell_spec(self.plan, "M1"),
                                    kwargs.get("repetition", 1), self.runtime,
                                    kwargs.get("output", self.output), now=NOW)

    def test_exact_concrete_admission_preserves_all_input_bytes(self):
        value = self.admission()
        original = copy.deepcopy(value)
        self.assertEqual(self.admit(value), self.device)
        self.assertEqual(value, original)
        self.assertIsNone(self.plan["screens"]["gpu_process_cap_bytes"])

    def test_missing_extra_wrong_identity_runtime_and_script_fields_reject(self):
        mutations = [
            lambda v: v.pop("device"),
            lambda v: v.update(extra=True),
            lambda v: v.update(schema_version="other"),
            lambda v: v.update(model_id="dense model"),
            lambda v: v.update(revision="0" * 40),
            lambda v: v.update(plan_sha256="0" * 64),
            lambda v: v.update(cell="M2"),
            lambda v: v.update(output_file="different.json"),
            lambda v: v["runtime"].update(python="unbound"),
            lambda v: v["scripts_sha256"].update(mr09_measure="unbound"),
            lambda v: v.update(authorization_reference=" "),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                value = self.admission()
                mutate(value)
                with self.assertRaises(ValueError):
                    self.admit(value)

    def test_expiry_is_explicit_and_excludes_the_exact_endpoint(self):
        for expiry in ("2026-10-20T06:00:00Z", "2026-10-19T06:00:00Z", "2099-02-30T00:00:00Z",
                       "2099-01-01", "2099-01-01T00:00:00+00:00", None):
            with self.subTest(expiry=expiry):
                value = self.admission()
                value["valid_until_utc"] = expiry
                with self.assertRaises(ValueError):
                    self.admit(value)

    def test_repetition_has_no_boolean_or_float_alias(self):
        for repetition in (True, 1.0, 0, 4):
            with self.subTest(repetition=repetition):
                value = self.admission()
                value["repetition"] = repetition
                with self.assertRaises(ValueError):
                    self.admit(value, repetition=repetition)

    def test_device_shape_and_every_capacity_need_concrete_integer_inputs(self):
        for key in m.DEVICE_KEYS - {"uuid"}:
            for invalid in (None, True, 1.0, 0, -1, 2 ** 64):
                with self.subTest(key=key, invalid=invalid):
                    value = self.admission()
                    value["device"][key] = invalid
                    with self.assertRaises(ValueError):
                        self.admit(value)
        for uid in ("0", "GPU-short", UUID + "," + UUID, "MIG-" + UUID, None):
            value = self.admission()
            value["device"]["uuid"] = uid
            with self.subTest(uid=uid), self.assertRaises(ValueError):
                self.admit(value)
        value = self.admission()
        value["device"]["inferred_cap"] = True
        with self.assertRaises(ValueError):
            self.admit(value)

    def test_payload_floor_plus_workspace_and_spare_budget_are_independent(self):
        value = self.admission()
        value["device"]["gpu_allocator_cap_bytes"] = 13876072448 + m.GIB - 1
        with self.assertRaisesRegex(ValueError, "payload plus workspace"):
            self.admit(value)
        value = self.admission()
        value["device"]["gpu_spare_bytes"] = 48 * m.GIB
        with self.assertRaisesRegex(ValueError, "exceed the device"):
            self.admit(value)

    def test_full_fixed_cell_table_and_optional_unsupported_boundary(self):
        expected = {"M1": (256, 1, 288, 37748736),
                    "M2": (2048, 1, 2080, 272629760),
                    "M3": (2048, 2, 2080, 545259520)}
        for name, values in expected.items():
            cell = m.cell_spec(self.plan, name)
            self.assertEqual((cell["prompt_tokens"], cell["active_sequences"],
                              cell["terminal_cache_positions_per_sequence"],
                              cell["derived_bf16_kv_payload_bytes"]), values)
            self.assertEqual(cell["decode_forwards"], 32)
        for name in ("M4", "G1", "D1", "M5"):
            with self.subTest(name=name), self.assertRaises(NotImplementedError):
                m.cell_spec(self.plan, name)

    def test_environment_is_set_before_import_and_conflicts_are_not_overwritten(self):
        names = ("HF_DEACTIVATE_ASYNC_LOAD", "HF_HUB_OFFLINE", "CUDA_VISIBLE_DEVICES")
        with patch.dict(os.environ, {}, clear=True):
            m.prepare_environment(self.device)
            self.assertEqual([os.environ[n] for n in names], ["1", "1", UUID])
        for name in names:
            with self.subTest(name=name), patch.dict(os.environ, {name: "conflicting"}, clear=True):
                before = dict(os.environ)
                with self.assertRaises(ValueError):
                    m.prepare_environment(self.device)
                self.assertEqual(dict(os.environ), before)
        with patch.dict(sys.modules, {"torch": SimpleNamespace()}), self.assertRaisesRegex(ValueError, "fresh process"):
            m.prepare_environment(self.device)

    def test_runtime_version_rejection_precedes_distribution_or_ml_access(self):
        with patch.object(m.platform, "python_version", return_value="3.12.14"), \
                patch.object(m.importlib.metadata, "distribution") as distribution:
            with self.assertRaisesRegex(ValueError, "Python"):
                m.runtime_identity(self.plan)
            distribution.assert_not_called()

    def test_installed_source_bytes_are_checked_beside_manifest_identity(self):
        plan = copy.deepcopy(self.plan)
        package = self.root / "site"
        package.mkdir()
        records = {}
        for name in m.RUNTIME_NAMES:
            folder = package / f"{name}.dist-info"
            folder.mkdir()
            (folder / "RECORD").write_text("synthetic record\n")
            records[name] = SimpleNamespace(version=plan["loader"][name],
                                           files=[PurePosixPath(f"{name}.dist-info/RECORD")],
                                           locate_file=lambda path: package / path)
        source = package / "transformers/modeling_utils.py"
        source.parent.mkdir()
        source.write_bytes(b"synthetic source\n")
        plan["loader"]["source_files"] = [{"path": "src/transformers/modeling_utils.py",
                                           "bytes": source.stat().st_size,
                                           "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]
        with patch.object(m.platform, "python_version", return_value="3.12.11"), \
                patch.object(m.importlib.metadata, "distribution", side_effect=records.__getitem__):
            observed = m.runtime_identity(plan)
            self.assertEqual(observed["versions"], {name: plan["loader"][name] for name in m.RUNTIME_NAMES})
            self.assertEqual(observed["transformers_sources_sha256"],
                             {"src/transformers/modeling_utils.py": plan["loader"]["source_files"][0]["sha256"]})
            source.write_bytes(b"corrupted source\n")
            with self.assertRaisesRegex(ValueError, "loader source"):
                m.runtime_identity(plan)

    def test_driver_csv_uses_selected_uuid_and_exact_integer_mib(self):
        result = SimpleNamespace(stdout=f"{UUID}, 49152, 40960, 590.10\n")
        with patch.object(m.subprocess, "run", return_value=result) as command:
            got = m.driver_observation(self.device)
        self.assertEqual(got["driver_free_bytes"], 40 * m.GIB)
        self.assertIn("--id=" + UUID, command.call_args.args[0])
        for row in (f"{UUID}, 49152.0, 40960, 590\n", f"{UUID}, 49152, 99999, 590\n",
                    f"{UUID}, 49152, 40960, 590\n{UUID}, 49152, 40960, 590\n",
                    f"GPU-other, 49152, 40960, 590\n"):
            with self.subTest(row=row), patch.object(m.subprocess, "run", return_value=SimpleNamespace(stdout=row)):
                with self.assertRaises(ValueError):
                    m.driver_observation(self.device)

    def test_failed_preflight_retains_observed_numbers_and_distinct_guards(self):
        gpu = {"driver_free_bytes": 10 * m.GIB}
        with patch.object(m, "available_host_bytes", return_value=32 * m.GIB - 1), \
                patch.object(m.shutil, "disk_usage", return_value=SimpleNamespace(free=28 * m.GIB)), \
                patch.object(m, "driver_observation", return_value=gpu):
            result = m.preflight(self.plan, self.device, self.directory)
        self.assertEqual(result["available_physical_host_bytes"], 32 * m.GIB - 1)
        self.assertEqual(result["guards"], {"physical_host": False, "available_storage": True,
                                          "selected_device_free": False})

    def test_loader_options_are_local_bf16_sdpa_and_explicit_eager_without_device_map(self):
        expected = {"local_files_only": True, "use_safetensors": True, "trust_remote_code": False,
                    "dtype": "bf16", "attn_implementation": "sdpa", "experts_implementation": "eager"}
        self.assertEqual(m.loader_kwargs(fake_torch()), expected)

    def test_complete_loaded_geometry_payload_and_backend_are_enforced_before_transfer(self):
        for change in ("dtype", "placement", "geometry", "count", "backend"):
            model = Model(self.plan)
            if change == "dtype": model.parameter.dtype = "float32"
            if change == "placement": model.parameter.device.type = "cuda"
            if change == "geometry": model.config.num_experts = 8
            if change == "count": model.parameter.elements -= 1
            if change == "backend": model.config._experts_implementation = "grouped_mm"
            with self.subTest(change=change), self.assertRaises(ValueError):
                m.verify_loaded_model(model, fake_torch(), self.plan)
            self.assertEqual(model.transfers, [])

    def test_all_three_cells_use_fresh_post_warmup_cache_and_exact_terminal_accounting(self):
        for name, positions, active, payload in (
                ("M1", 288, 1, 37748736), ("M2", 2080, 1, 272629760), ("M3", 2080, 2, 545259520)):
            with self.subTest(cell=name):
                model, torch = Model(self.plan), fake_torch()
                phases = []
                tokenizer = SimpleNamespace(encode=lambda words, **kwargs: [1, 2, 3, 4, 5])
                result = m.exercise(model, tokenizer, torch, Cache, m.cell_spec(self.plan, name),
                                    lambda phase: phases.append(("begin", phase)),
                                    lambda phase, started: phases.append(("end", phase)))
                self.assertEqual(result["actual_tokens"]["cache_tokens_per_sequence"], positions)
                self.assertEqual(result["actual_tokens"]["active_sequences"], active)
                self.assertEqual(result["actual_tokens"]["decode_forwards_per_sequence"], 32)
                self.assertEqual(result["actual_tokens"]["greedy_tokens_produced_per_sequence"], 33)
                self.assertEqual(result["native_kv_steady_payload_bytes"], payload)
                self.assertEqual(len(model.calls), 35)  # two warmup, one prefill, 32 decode
                self.assertEqual(model.calls[0][0], (active, 64))
                self.assertEqual(model.calls[1][0], (active, 1))
                self.assertIs(model.calls[0][1], model.calls[1][1])
                self.assertIsNot(model.calls[1][1], model.calls[2][1])
                self.assertEqual(model.calls[2][2], 0)
                self.assertTrue(all(shape == (active, 1) for shape, _, _ in model.calls[3:]))
                self.assertEqual([phase for action, phase in phases if action == "begin"],
                                 ["warmup", "prefill", "decode", "steady_state"])
                self.assertEqual(torch.cuda.empties, 1)

    def test_invalid_tokenizer_or_cache_geometry_does_not_claim_completion(self):
        tokenizer = SimpleNamespace(encode=lambda *args, **kwargs: [])
        with self.assertRaisesRegex(ValueError, "tokenizer"):
            m.exercise(Model(self.plan), tokenizer, fake_torch(), Cache, m.cell_spec(self.plan, "M1"),
                       lambda phase: None, lambda *args: None)
        cache = Cache()
        cache.layers = [SimpleNamespace(keys=Tensor(1, dtype="float32"), values=Tensor(1))]
        with self.assertRaisesRegex(ValueError, "BF16"):
            m.cache_payload(cache, fake_torch())

    def test_full_synthetic_measurement_begins_cpu_interval_before_loader_and_retains_unknown_host_peak(self):
        torch, model = fake_torch(), Model(self.plan)
        result = {"phases": [], "status": "unexecuted"}
        loading_phases = []
        tokenizer = SimpleNamespace(encode=lambda *args, **kwargs: [1, 2, 3])

        def load_tokenizer(*args, **kwargs):
            loading_phases.append(("tokenizer", result["current_phase"], kwargs))
            return tokenizer

        def load_model(*args, **kwargs):
            loading_phases.append(("model", result["current_phase"], kwargs))
            return model

        transformers = SimpleNamespace(
            AutoTokenizer=SimpleNamespace(from_pretrained=load_tokenizer),
            AutoModelForCausalLM=SimpleNamespace(from_pretrained=load_model), DynamicCache=Cache)
        with patch.dict(sys.modules, {"torch": torch, "transformers": transformers}):
            m.measure(self.directory, self.plan, m.cell_spec(self.plan, "M1"), self.device, result)
        self.assertEqual([phase for _, phase, _ in loading_phases], ["cpu_loading", "cpu_loading"])
        self.assertEqual(loading_phases[0][2], {"local_files_only": True, "trust_remote_code": False})
        self.assertEqual(loading_phases[1][2], m.loader_kwargs(torch))
        self.assertEqual(model.transfers, ["cuda:0"])
        self.assertEqual([p["phase"] for p in result["phases"]],
                         ["baseline", "cpu_loading", "gpu_loading", "warmup", "prefill", "decode", "steady_state"])
        self.assertIsNone(result["host_peak_bytes"])
        self.assertIsNone(result["whole_process_gpu_peak_bytes"])
        self.assertTrue(all(p["host_peak_bytes"] is None for p in result["phases"]))
        self.assertEqual(result["status"], "measurement_completed_pending_evidence_review")
        self.assertEqual(torch.cuda.fractions, [(1 / 3, 0)])

    def test_unsupported_allocator_does_not_load_or_transfer_model(self):
        torch = fake_torch()
        torch.cuda.get_allocator_backend = lambda: "cudaMallocAsync"
        loader = Mock()
        transformers = SimpleNamespace(AutoTokenizer=loader, AutoModelForCausalLM=loader, DynamicCache=Cache)
        with patch.dict(sys.modules, {"torch": torch, "transformers": transformers}), \
                self.assertRaisesRegex(NotImplementedError, "native"):
            m.measure(self.directory, self.plan, m.cell_spec(self.plan, "M1"), self.device, {"phases": []})
        loader.from_pretrained.assert_not_called()

    def test_run_retains_failed_screen_and_does_not_import_model_or_repeat_output(self):
        admission = self.root / "admission.json"
        admission.write_text(json.dumps(self.admission()))
        observed = {"guards": {"physical_host": False, "available_storage": True, "selected_device_free": True},
                    "available_physical_host_bytes": 32 * m.GIB - 1}
        with patch.object(m, "runtime_identity", return_value=self.runtime), \
                patch.object(a, "verify", return_value={"classification": "synthetic artifact verification"}), \
                patch.object(m, "preflight", return_value=observed), \
                patch.object(m, "measure") as model, patch.object(m, "prepare_environment") as environment:
            result = m.run(self.directory, admission, self.output, "M1", 1)
            self.assertEqual(result["status"], "unexecuted")
            self.assertEqual(result["fresh_preflight"], observed)
            self.assertEqual(json.loads(self.output.read_text()), result)
            model.assert_not_called()
            environment.assert_not_called()
            with self.assertRaisesRegex(ValueError, "already exists"):
                m.run(self.directory, admission, self.output, "M1", 1)

    def test_existing_pending_attempt_blocks_before_artifact_or_model_access(self):
        admission = self.root / "admission.json"
        admission.write_text(json.dumps(self.admission()))
        pending = self.output.with_name(self.output.name + ".pending")
        pending.write_text("original interrupted attempt")
        with patch.object(m, "runtime_identity", return_value=self.runtime), \
                patch.object(a, "verify") as verify, patch.object(m, "measure") as model:
            with self.assertRaises(FileExistsError):
                m.run(self.directory, admission, self.output, "M1", 1)
            verify.assert_not_called()
            model.assert_not_called()
        self.assertEqual(pending.read_text(), "original interrupted attempt")
        self.assertFalse(self.output.exists())

    def test_real_cli_plan_optional_and_missing_admission_never_import_ml(self):
        probe = r'''
import importlib.abc, runpy, sys
class NoML(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in ("torch", "transformers"):
            raise AssertionError("ML import before concrete admission")
sys.meta_path.insert(0, NoML())
sys.path.insert(0, sys.argv[1])
sys.argv = ["mr09_olmoe_measure.py", *sys.argv[2:]]
runpy.run_module("mr09_olmoe_measure", run_name="__main__")
'''
        for arguments, code, status in (
                (["plan"], 0, "unexecuted"),
                (["run", "--cell", "M4"], 0, "unsupported"),
                (["run", "--cell", "G1"], 0, "unsupported"),
                (["run"], 1, "operation_error")):
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, "-c", probe, str(SCRIPTS), *arguments],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], status)


    def test_cuda_uuid_mismatch_rejects_before_model_loading_even_with_equal_capacity(self):
        torch = fake_torch()
        torch.cuda.get_device_properties = lambda index: SimpleNamespace(
            uuid=SimpleNamespace(bytes=list(uuid.UUID("00000000-0000-0000-0000-000000000002").bytes)))
        loader = Mock()
        transformers = SimpleNamespace(AutoTokenizer=loader, AutoModelForCausalLM=loader, DynamicCache=Cache)
        with patch.dict(sys.modules, {"torch": torch, "transformers": transformers}), self.assertRaisesRegex(ValueError, "UUID"):
            m.measure(self.directory, self.plan, m.cell_spec(self.plan, "M1"), self.device, {"phases": []})
        loader.from_pretrained.assert_not_called()
        self.assertEqual(torch.cuda.fractions, [])

    def test_driver_and_cuda_context_total_domains_are_retained_separately(self):
        torch, model = fake_torch(), Model(self.plan)
        context_total = 48 * m.GIB - 4096
        property_total = 48 * m.GIB + 1048576
        torch.cuda.mem_get_info = lambda index=0: (40 * m.GIB, context_total)
        torch.cuda.get_device_properties = lambda index: SimpleNamespace(
            uuid=SimpleNamespace(bytes=list(uuid.UUID(UUID[4:]).bytes)), total_memory=property_total)
        tokenizer = SimpleNamespace(encode=lambda *args, **kwargs: [1, 2])
        transformers = SimpleNamespace(
            AutoTokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: tokenizer),
            AutoModelForCausalLM=SimpleNamespace(from_pretrained=lambda *args, **kwargs: model), DynamicCache=Cache)
        result = {"phases": []}
        with patch.dict(sys.modules, {"torch": torch, "transformers": transformers}):
            m.measure(self.directory, self.plan, m.cell_spec(self.plan, "M1"), self.device, result)
        self.assertEqual(result["cuda_context_observation"]["total_bytes"], context_total)
        for phase in result["phases"]:
            self.assertEqual(phase["cuda_context_total_bytes"], context_total)
            self.assertEqual(phase["cuda_context_free_bytes"], 40 * m.GIB)
            self.assertNotIn("driver_total_bytes", phase)
            self.assertNotIn("driver_free_bytes", phase)
        self.assertEqual(result["cuda_device_uuid"], UUID)
        self.assertEqual(self.device["driver_total_bytes"], 48 * m.GIB)
        self.assertEqual(torch.cuda.fractions, [(16 * m.GIB / property_total, 0)])
        self.assertEqual(result["allocator"]["device_property_total_bytes"], property_total)
        self.assertLessEqual(result["allocator"]["effective_limit_bytes"], 16 * m.GIB)
        self.assertEqual(result["status"], "measurement_completed_pending_evidence_review")

    def test_admission_changed_during_hashing_keeps_original_parsed_digest_and_does_not_load(self):
        admission = self.root / "admission.json"
        raw = json.dumps(self.admission(), indent=2).encode()
        admission.write_bytes(raw)
        def verified(directory):
            admission.write_text("{}")
            return {"classification": "synthetic verification with concurrent control change"}
        with patch.object(m, "runtime_identity", return_value=self.runtime), \
                patch.object(a, "verify", side_effect=verified), \
                patch.object(m, "preflight", return_value={"guards": {"all": True}}), \
                patch.object(m, "measure") as model, patch.object(m, "prepare_environment") as environment:
            result = m.run(self.directory, admission, self.output, "M1", 1)
        self.assertEqual(result["admission_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertNotEqual(result["admission_sha256"], hashlib.sha256(admission.read_bytes()).hexdigest())
        self.assertEqual(result["status"], "unexecuted")
        self.assertEqual(result["failure"]["phase"], "admission_recheck")
        model.assert_not_called()
        environment.assert_not_called()

    def test_runtime_changed_during_hashing_is_rejected_before_environment_or_model(self):
        admission = self.root / "admission.json"
        admission.write_text(json.dumps(self.admission()))
        with patch.object(m, "runtime_identity", side_effect=[self.runtime, {"changed": True}]), \
                patch.object(a, "verify", return_value={"classification": "synthetic"}), \
                patch.object(m, "preflight", return_value={"guards": {"all": True}}), \
                patch.object(m, "measure") as model, patch.object(m, "prepare_environment") as environment:
            result = m.run(self.directory, admission, self.output, "M1", 1)
        self.assertEqual(result["status"], "unexecuted")
        self.assertEqual(result["failure"]["phase"], "admission_recheck")
        model.assert_not_called()
        environment.assert_not_called()

    def test_completed_observation_publication_failure_never_reports_unexecuted(self):
        admission = self.root / "admission.json"
        admission.write_text(json.dumps(self.admission()))
        def measured(directory, plan, cell, device, result):
            result.update(status="measurement_completed_pending_evidence_review",
                          current_phase="steady_state", synthetic_test_only=True)
        captured = io.StringIO()
        with patch.object(m, "runtime_identity", return_value=self.runtime), \
                patch.object(a, "verify", return_value={"classification": "synthetic"}), \
                patch.object(m, "preflight", return_value={"guards": {"all": True}}), \
                patch.object(m, "measure", side_effect=measured), \
                patch.object(m, "prepare_environment"), \
                patch("mr09_measure.os.link", side_effect=OSError("synthetic publication failure")), \
                redirect_stdout(captured):
            code = m.main(["run", "--model-dir", str(self.directory), "--admission", str(admission),
                           "--output", str(self.output)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(captured.getvalue())["status"], "operation_error")
        self.assertFalse(self.output.exists())
        self.assertTrue(self.output.with_name(self.output.name + ".pending").exists())
        retained = list(self.root.glob(".mr09-unpublished-*.json"))
        self.assertEqual(len(retained), 1)
        self.assertEqual(json.loads(retained[0].read_text())["status"],
                         "measurement_completed_pending_evidence_review")


    def test_native_allocator_fraction_never_exceeds_the_declared_integer_byte_cap(self):
        for cap, total in ((16 * m.GIB, 48 * m.GIB + 1048576),
                           (9007199254740993, 18014398509482001),
                           (9007199254740995, 18014398509482001),
                           (2 ** 63 - 3, 2 ** 64 - 1)):
            with self.subTest(cap=cap, total=total):
                fraction, effective = m.native_allocator_fraction(cap, total)
                # Literal native setter contract: C++ double product truncated to size_t.
                self.assertEqual(effective, int(fraction * float(total)))
                self.assertGreater(fraction, 0)
                self.assertLess(fraction, 1)
                self.assertGreater(effective, 0)
                self.assertLessEqual(effective, cap)
        for cap, total in ((True, 10), (1.0, 10), (0, 10), (10, 10), (11, 10)):
            with self.subTest(invalid=(cap, total)), self.assertRaises(ValueError):
                m.native_allocator_fraction(cap, total)


if __name__ == "__main__":
    unittest.main()
