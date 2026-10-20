"""Synthetic fixed-M4 storage/identity controls; no ML imports or GPU allocations."""
from contextlib import redirect_stdout
import copy
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mr09_fixture_support import symlink_or_skip

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mr09_olmoe_quanto as q

QINT4 = object()
POINTERS = itertools.count(4096, 2 ** 26)


class Storage:
    def __init__(self, size, pointer=None, device_index=0):
        self.size = size
        self.pointer = next(POINTERS) if pointer is None and size else pointer or 0
        self.device = SimpleNamespace(type="cuda", index=device_index)

    def nbytes(self): return self.size
    def data_ptr(self): return self.pointer


class PlainTensor:
    def __init__(self, shape, dtype="bf16", *, storage=None, offset=0, device_index=0):
        self.shape = tuple(shape)
        self.dtype = dtype
        self.device = SimpleNamespace(type="cuda", index=device_index)
        self.layout = "strided"
        self.offset = offset
        self.storage = storage if storage is not None else Storage(math.prod(shape) * self.element_size())
        self.contiguous = True

    def numel(self): return math.prod(self.shape)
    def element_size(self): return 1 if self.dtype == "uint8" else 2
    def storage_offset(self): return self.offset
    def is_contiguous(self): return self.contiguous
    def untyped_storage(self): return self.storage


class NoWrapperOperations:
    def forbidden(self, *args, **kwargs):
        raise AssertionError("observer invoked a logical wrapper operation")
    numel = element_size = untyped_storage = dequantize = unpack = clone = cpu = to = forbidden


class Packed(NoWrapperOperations):
    def __init__(self, groups):
        self._bits = 4
        self.shape = (groups, 64)
        self.dtype = "uint8"
        self.device = SimpleNamespace(type="cuda", index=0)
        self._data = PlainTensor(((groups + 1) // 2, 64), "uint8")


class Weight(NoWrapperOperations):
    def __init__(self, prefix=2048):
        self.shape = (1, 16, prefix, 128)
        self.dtype = "bf16"  # This is logical dtype, deliberately not packed bytes.
        self.device = SimpleNamespace(type="cuda", index=0)
        self._qtype, self._axis, self._group_size = QINT4, 0, 64
        groups = math.prod(self.shape) // 64
        self._data = Packed(groups)
        self._scale = PlainTensor((groups, 1))
        self._shift = PlainTensor((groups, 1))


class Layer:
    def __init__(self, **profile):
        for key, value in profile.items():
            if key != "backend": setattr(self, key, value)
        self.qtype = QINT4
        self.cumulative_length = 0
        self.is_initialized = False

    def append(self, count):
        self.cumulative_length += count
        if not self.is_initialized:
            self.is_initialized = True
            self.prefix = count
            self._quantized_keys, self._quantized_values = Weight(count), Weight(count)
        residual = self.cumulative_length - self.prefix
        shape = (0,) if residual == 0 else (1, 16, residual, 128)
        self.keys, self.values = PlainTensor(shape), PlainTensor(shape)


class Cache:
    def __init__(self, config=None, **profile):
        self.arguments = {"config": config, **profile}
        self.layers = [Layer(**profile) for _ in range(16)]
        self.offloading = False

    def append(self, count):
        for layer in self.layers: layer.append(count)

    def get_seq_length(self): return self.layers[0].cumulative_length


def backend(): return q.Backend(Cache, Layer, Weight, Packed, QINT4)


def tensor_api():
    return SimpleNamespace(Tensor=PlainTensor, bfloat16="bf16", uint8="uint8", strided="strided")


def observed_cache(terminal=False):
    value = q.new_cache(backend(), SimpleNamespace(synthetic=True))
    value.append(2048)
    if terminal:
        for _ in range(32): value.append(1)
    return value


class QuantoTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="olmoe-quanto-synthetic-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def observe(self, cache, terminal=False):
        return q.observe_cache(cache, tensor_api(), backend(),
                               "post_decode" if terminal else "prefill", 2080 if terminal else 2048)

    def test_fixed_factory_supplies_every_selected_option_and_original_config(self):
        config = object()
        cache = q.new_cache(backend(), config)
        self.assertIs(cache.arguments["config"], config)
        self.assertEqual({k: v for k, v in cache.arguments.items() if k != "config"},
                         {"backend": "quanto", "nbits": 4, "axis_key": 0, "axis_value": 0,
                          "q_group_size": 64, "residual_length": 128})
        self.assertEqual(len(cache.layers), 16)
        self.assertTrue(all(not layer.is_initialized for layer in cache.layers))

    def test_prefill_counts_actual_full_leaf_allocations_and_empty_residual(self):
        cache = observed_cache()
        sample = self.observe(cache)
        self.assertEqual(sample["component_bytes"],
                         {"packed_data": 67108864, "scales": 4194304, "shifts": 4194304, "residual": 0})
        self.assertEqual(sample["total_unique_backing_bytes"], 75497472)
        self.assertEqual(sample["residual_shape"], [0])
        self.assertEqual(sample["unique_backing_storages"],
                         {"packed_data": 32, "scales": 32, "shifts": 32, "residual": 0})
        self.assertEqual(sample["plain_tensor_references"], dict.fromkeys(("packed_data", "scales", "shifts", "residual"), 32))
        self.assertEqual(sample["validated_layers"], 16)
        self.assertEqual(sample["validated_key_value_tensors"], 32)

    def test_terminal_keeps_prefix_and_thirty_two_token_residual_separate(self):
        sample = self.observe(observed_cache(True), True)
        self.assertEqual(sample["cache_tokens_per_sequence"], 2080)
        self.assertEqual(sample["quantized_prefix_shape"], [1, 16, 2048, 128])
        self.assertEqual(sample["residual_shape"], [1, 16, 32, 128])
        self.assertEqual(sample["component_bytes"]["residual"], 4194304)
        self.assertEqual(sample["total_unique_backing_bytes"], 79691776)

    def test_larger_backing_and_offset_are_counted_without_logical_size_substitution(self):
        cache = observed_cache()
        tensor = cache.layers[0]._quantized_keys._data._data
        tensor.storage = Storage(2 ** 21 + 8192)
        tensor.offset = 64
        sample = self.observe(cache)
        self.assertEqual(sample["component_bytes"]["packed_data"], 67108864 + 8192)
        self.assertEqual(sample["total_unique_backing_bytes"], 75497472 + 8192)

    def test_aliases_deduplicate_across_keys_values_and_layers_for_each_sample(self):
        cache = observed_cache()
        shared = cache.layers[0]._quantized_keys._data._data.storage
        cache.layers[0]._quantized_values._data._data.storage = shared
        cache.layers[15]._quantized_values._data._data.storage = shared
        first, second = self.observe(cache), self.observe(cache)
        self.assertEqual(first, second)  # The next sample resets its complete identity set.
        self.assertEqual(first["component_bytes"]["packed_data"], 30 * 2 ** 21)
        self.assertEqual(first["unique_backing_storages"]["packed_data"], 30)
        self.assertEqual(first["plain_tensor_references"]["packed_data"], 32)

    def test_cross_component_nonempty_alias_is_unsupported_not_first_category_assignment(self):
        cache = observed_cache()
        cache.layers[15]._quantized_values._shift.storage = cache.layers[0]._quantized_keys._scale.storage
        with self.assertRaisesRegex(q.CacheLayoutError, "across cache components"):
            self.observe(cache)

    def test_same_address_with_inconsistent_extent_is_rejected(self):
        cache = observed_cache()
        original = cache.layers[0]._quantized_keys._data._data.storage
        cache.layers[1]._quantized_values._data._data.storage = Storage(original.size + 64, original.pointer)
        with self.assertRaisesRegex(q.CacheLayoutError, "inconsistent backing extent"):
            self.observe(cache)

    def test_zero_logical_residual_with_retained_backing_is_still_counted(self):
        cache = observed_cache()
        cache.layers[0].keys.storage = Storage(4096)
        sample = self.observe(cache)
        self.assertEqual(sample["component_bytes"]["residual"], 4096)
        self.assertEqual(sample["unique_backing_storages"]["residual"], 1)

    def test_all_layers_and_both_key_value_geometries_are_required(self):
        changes = [lambda c: c.layers.pop(),
                   lambda c: c.layers.append(c.layers[0]),
                   lambda c: setattr(c.layers[15], "cumulative_length", 2047),
                   lambda c: setattr(c.layers[15], "cumulative_length", True),
                   lambda c: setattr(c.layers[15], "is_initialized", False),
                   lambda c: setattr(c.layers[15]._quantized_values, "shape", (1, 16, 2047, 128)),
                   lambda c: setattr(c.layers[15], "values", PlainTensor((1, 16, 1, 128))),
                   lambda c: setattr(c, "offloading", True)]
        for index, mutate in enumerate(changes):
            with self.subTest(index=index):
                cache = observed_cache()
                mutate(cache)
                with self.assertRaises(q.CacheLayoutError): self.observe(cache)

    def test_every_profile_field_and_wrapper_kind_fail_without_fallback(self):
        class WeightSubclass(Weight): pass
        changes = [lambda c: setattr(c.layers[0], "nbits", 2),
                   lambda c: setattr(c.layers[15], "axis_value", -1),
                   lambda c: setattr(c.layers[15], "axis_key", False),
                   lambda c: setattr(c.layers[15], "q_group_size", 128),
                   lambda c: setattr(c.layers[15], "residual_length", 64),
                   lambda c: setattr(c.layers[15], "qtype", object()),
                   lambda c: setattr(c.layers[15], "_quantized_values", WeightSubclass()),
                   lambda c: setattr(c.layers[15]._quantized_values, "_axis", -1),
                   lambda c: setattr(c.layers[15]._quantized_values, "_group_size", 128),
                   lambda c: setattr(c.layers[15]._quantized_values._data, "_bits", 2),
                   lambda c: setattr(c.layers[15]._quantized_values._data, "shape", (1, 16, 2048, 128))]
        for index, mutate in enumerate(changes):
            with self.subTest(index=index):
                cache = observed_cache()
                mutate(cache)
                with self.assertRaises(q.CacheLayoutError): self.observe(cache)

    def test_missing_layout_never_becomes_a_zero_sample(self):
        for attribute in ("_data", "_scale", "_shift"):
            cache = observed_cache()
            delattr(cache.layers[15]._quantized_values, attribute)
            history = []
            with self.subTest(attribute=attribute), self.assertRaises(q.CacheLayoutError):
                q.retain_observation(history, cache, tensor_api(), backend(), "prefill", 2048, 2 ** 30)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["status"], "unsupported")
            self.assertNotIn("component_bytes", history[0])
            self.assertNotIn("total_unique_backing_bytes", history[0])

    def test_plain_leaf_dtype_device_layout_and_extent_must_all_match(self):
        class TensorSubclass(PlainTensor): pass
        changes = [lambda t: setattr(t, "dtype", "float32"),
                   lambda t: setattr(t.device, "index", 1),
                   lambda t: setattr(t.device, "type", "cpu"),
                   lambda t: setattr(t, "layout", "sparse"),
                   lambda t: setattr(t, "contiguous", False),
                   lambda t: setattr(t.storage, "size", 1),
                   lambda t: setattr(t.storage, "pointer", 0),
                   lambda t: setattr(t, "offset", -1),
                   lambda t: setattr(t.storage.device, "index", 1)]
        for index, mutate in enumerate(changes):
            with self.subTest(index=index):
                cache = observed_cache()
                mutate(cache.layers[15]._quantized_values._scale)
                with self.assertRaises(q.CacheLayoutError): self.observe(cache)
        cache = observed_cache()
        cache.layers[15]._quantized_values._scale = TensorSubclass((65536, 1))
        with self.assertRaisesRegex(q.CacheLayoutError, "ordinary tensor"):
            self.observe(cache)

    def test_phase_and_length_are_the_exact_two_supported_observation_points(self):
        for phase, positions in (("warmup", 65), ("prefill", 2080), ("post_decode", 2081),
                                 ("prefill", 2048.0), ("prefill", True)):
            with self.subTest(phase=phase, positions=positions), self.assertRaises(q.CacheLayoutError):
                q.observe_cache(observed_cache(), tensor_api(), backend(), phase, positions)

    def test_sample_contains_no_pointer_estimate_error_or_logical_bf16_payload(self):
        cache = observed_cache(True)
        sample = self.observe(cache, True)
        text = json.dumps(sample)
        self.assertNotIn(str(cache.layers[0]._quantized_keys._data._data.storage.pointer), text)
        for forbidden in ("pointer", "estimated_bytes", '"errors"', "native_kv", "bf16_payload"):
            self.assertNotIn(forbidden, text)

    def test_allowance_boundary_is_inclusive_and_failure_retains_exact_observation(self):
        cache = observed_cache()
        history = []
        q.retain_observation(history, cache, tensor_api(), backend(), "prefill", 2048, 75497472)
        self.assertTrue(history[0]["within_allowance"])
        failed = []
        with self.assertRaises(q.CacheAllowanceExceeded):
            q.retain_observation(failed, cache, tensor_api(), backend(), "prefill", 2048, 75497471)
        self.assertEqual(failed[0]["total_unique_backing_bytes"], 75497472)
        self.assertEqual(failed[0]["reviewed_allowance_bytes"], 75497471)
        self.assertFalse(failed[0]["within_allowance"])
        self.assertNotIn("estimated_bytes", failed[0])

    def test_later_unsupported_layout_preserves_the_prior_complete_sample(self):
        cache = observed_cache()
        history = []
        q.retain_observation(history, cache, tensor_api(), backend(), "prefill", 2048, 2 ** 30)
        original = copy.deepcopy(history[0])
        for _ in range(32): cache.append(1)
        cache.layers[15].values = None
        with self.assertRaises(q.CacheLayoutError):
            q.retain_observation(history, cache, tensor_api(), backend(), "post_decode", 2080, 2 ** 30)
        self.assertEqual(history[0], original)
        self.assertEqual(history[1]["status"], "unsupported")
        self.assertNotIn("total_unique_backing_bytes", history[1])

    def installed_fixture(self):
        site = self.root / "site"
        site.mkdir()
        record = site / "optimum_quanto-0.2.7.dist-info/RECORD"
        record.parent.mkdir()
        record.write_bytes(b"synthetic RECORD only; no real package\n")
        sources = []
        for name in ("transformers/cache_utils.py", "optimum/quanto/tensor/packed.py"):
            path = site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = ("synthetic source for " + name + "\n").encode()
            path.write_bytes(raw)
            sources.append((name, len(raw), hashlib.sha256(raw).hexdigest()))
        quanto = SimpleNamespace(version="0.2.7", files=[PurePosixPath(record.relative_to(site))],
                                 locate_file=lambda name: site / name)
        transformers = SimpleNamespace(locate_file=lambda name: site / name)
        distributions = {"optimum-quanto": quanto, "transformers": transformers}
        return site, record, sources, distributions

    def test_optional_metadata_and_pinned_source_bytes_are_bound_without_ml(self):
        site, record, sources, distributions = self.installed_fixture()
        with patch.object(q, "SOURCE_FILES", tuple(sources)), \
                patch.object(q.importlib.metadata, "distribution", side_effect=distributions.__getitem__):
            result = q.runtime_identity()
            self.assertEqual(result["version"], "0.2.7")
            self.assertEqual(result["distribution_record_sha256"], hashlib.sha256(record.read_bytes()).hexdigest())
            self.assertEqual(result["source_files_sha256"], {name: digest for name, _, digest in sources})
            path = site / sources[-1][0]
            path.write_bytes(b"X" * sources[-1][1])
            with self.assertRaisesRegex(ValueError, "pinned upstream"):
                q.runtime_identity()

    def test_wrong_optional_version_or_missing_record_rejects_before_source_access(self):
        _, _, sources, distributions = self.installed_fixture()
        with patch.object(q, "SOURCE_FILES", tuple(sources)), \
                patch.object(q.importlib.metadata, "distribution", side_effect=distributions.__getitem__), \
                patch.object(q, "_source_digest") as read:
            distributions["optimum-quanto"].version = "0.2.8"
            with self.assertRaisesRegex(ValueError, "0.2.7"): q.runtime_identity()
            read.assert_not_called()
            distributions["optimum-quanto"].version = "0.2.7"
            distributions["optimum-quanto"].files = []
            with self.assertRaisesRegex(ValueError, "RECORD"): q.runtime_identity()
            read.assert_not_called()

    def test_source_reader_rejects_symlink_length_and_same_length_corruption(self):
        target = self.root / "source.py"
        target.write_bytes(b"source\n")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        self.assertEqual(q._source_digest(target, 7, digest), digest)
        with self.assertRaisesRegex(ValueError, "length/type"):
            q._source_digest(target, 8, digest)
        target.write_bytes(b"broken\n")
        with self.assertRaisesRegex(ValueError, "pinned upstream"):
            q._source_digest(target, 7, digest)
        with self.subTest(fixture="symlink"):
            link = self.root / "link.py"
            symlink_or_skip(link, target)
            with self.assertRaisesRegex(ValueError, "length/type"):
                q._source_digest(link, 7, digest)

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"), "POSIX FIFO boundary")
    def test_actual_fifo_substitution_is_nonblocking_and_rejected_before_read(self):
        source = self.root / "source.py"
        source.write_bytes(b"source\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        original_open = q.os.open
        def swap(path, flags, *args, **kwargs):
            self.assertTrue(flags & os.O_NONBLOCK, "regular-file open must not block on a substituted FIFO")
            source.unlink()
            os.mkfifo(source)
            return original_open(path, flags, *args, **kwargs)
        with patch.object(q.os, "open", side_effect=swap), \
                self.assertRaisesRegex(ValueError, "changed before read"):
            q._source_digest(source, 7, digest)

    def test_fixed_cell_rejects_changes_without_replacing_historical_nulls(self):
        original = copy.deepcopy(q.CELL)
        q.validate_cell(original)
        self.assertEqual(original, q.CELL)
        for key, value in (("prompt_tokens", 4096), ("active_sequences", 2), ("decode_forwards", 31),
                           ("derived_weights_plus_kv_floor_bytes", 1), ("status", "complete")):
            changed = copy.deepcopy(original)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): q.validate_cell(changed)

    def test_real_m4_plan_and_missing_admission_do_not_import_any_ml_package(self):
        probe = r'''
import importlib.abc, runpy, sys
class NoML(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in ("torch", "transformers", "optimum"):
            raise AssertionError("ML import before concrete admission")
sys.meta_path.insert(0, NoML())
sys.path.insert(0, sys.argv[1])
sys.argv = ["mr09_olmoe_measure.py", *sys.argv[2:]]
runpy.run_module("mr09_olmoe_measure", run_name="__main__")
'''
        for arguments, code, status in ((["plan", "--cell", "M4"], 0, "unexecuted"),
                                        (["run", "--cell", "M4"], 1, "operation_error")):
            with self.subTest(arguments=arguments):
                process = subprocess.run([sys.executable, "-c", probe, str(SCRIPTS), *arguments],
                                         capture_output=True, text=True, timeout=30)
                self.assertEqual(process.returncode, code, process.stderr)
                value = json.loads(process.stdout)
                self.assertEqual(value["status"], status)
                if arguments[0] == "plan":
                    self.assertEqual(value["admission_version"], "mr09-olmoe-run-admission/v2")
                    self.assertIn("gpu_cache_allowance_bytes", value["device_fields"])
                    self.assertEqual(value["optional_backend"], {"optimum-quanto": "0.2.7"})
                    self.assertEqual(value["cells"][-1]["derived_weights_plus_kv_floor_bytes"], None)


if __name__ == "__main__":
    unittest.main()
