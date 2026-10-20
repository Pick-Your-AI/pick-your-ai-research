"""Offline synthetic controls; no publisher artifact, ML runtime or GPU is used."""
import copy
from contextlib import redirect_stdout
from email.message import Message
import hashlib
import io
import json
import os
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mr09_olmoe_artifacts as a


def metadata_spec(name, data, *, prior=True):
    return {"file": name, "bytes": len(data),
            "publisher_git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
            "observed_sha256": hashlib.sha256(data).hexdigest() if prior else None}


class Response(io.BytesIO):
    def __init__(self, data, *, status=200, lengths=None, encoding=None):
        super().__init__(data)
        self.status = status
        self.headers = Message()
        for length in (lengths or []):
            self.headers["Content-Length"] = length
        if encoding is not None:
            self.headers["Content-Encoding"] = encoding


class Opener:
    def __init__(self, responses, on_open=None):
        self.responses = iter(responses)
        self.calls = []
        self.on_open = on_open

    def open(self, request, timeout):
        self.calls.append((request.full_url, dict(request.header_items()), timeout))
        if self.on_open:
            self.on_open()
        return next(self.responses)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="olmoe-artifact-synthetic-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.model = self.root / "model"
        self.model.mkdir()
        self.data = b'{"synthetic":"metadata"}\n'
        self.spec = metadata_spec("tokenizer.json", self.data, prior=False)

    def test_accepted_plan_and_exact_nine_file_allowlist_are_unchanged(self):
        plan = a.load_plan()
        self.assertEqual([x["file"] for x in a.inventory(plan)], list(a.FILES))
        self.assertEqual(sum(x["bytes"] for x in a.inventory(plan)), 13841132070)
        self.assertEqual(plan["screens"]["gpu_process_cap_bytes"], None)
        self.assertEqual(plan["screens"]["future_runner_sha256"], None)
        self.assertEqual([c["status"] for c in plan["cells"]], ["unexecuted"] * 4)

    def test_mutated_plan_is_rejected_before_network_or_storage(self):
        path = self.root / "altered.json"
        original = a.PLAN_PATH.read_bytes()
        path.write_bytes(original + b" ")
        with patch.object(a, "PLAN_PATH", path), self.assertRaisesRegex(ValueError, "bytes changed"):
            a.load_plan()
        self.assertEqual(list(self.model.iterdir()), [])

    def test_metadata_observation_keeps_unknown_prior_sha_separate(self):
        path = self.model / self.spec["file"]
        path.write_bytes(self.data)
        result = a.verify_file(path, self.spec)
        self.assertIsNone(result["prior_observed_sha256"])
        self.assertEqual(result["local_sha256"], hashlib.sha256(self.data).hexdigest())
        self.assertEqual(result["verification_basis"], "publisher_git_blob_and_length")

    def test_weight_payload_uses_lfs_sha_not_pointer_git_blob(self):
        path = self.model / a.FILES[0]
        path.write_bytes(self.data)
        spec = {"file": path.name, "bytes": len(self.data),
                "publisher_sha256": hashlib.sha256(self.data).hexdigest(),
                "publisher_pointer_git_blob": "0" * 40}
        result = a.verify_file(path, spec)
        self.assertEqual(result["verification_basis"], "publisher_lfs_sha256_and_length")
        self.assertNotEqual(hashlib.sha1(self.data).hexdigest(), spec["publisher_pointer_git_blob"])

    def test_prior_metadata_sha_is_also_enforced(self):
        path = self.model / "tokenizer.json"
        path.write_bytes(self.data)
        spec = {**self.spec, "observed_sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "previous metadata"):
            a.verify_file(path, spec)

    def test_exact_length_and_identity_controls_reject_without_rewriting(self):
        path = self.model / "tokenizer.json"
        for data in (self.data[:-1], self.data + b"x", b"x" * len(self.data)):
            with self.subTest(data=data):
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    a.verify_file(path, self.spec)
                self.assertEqual(path.read_bytes(), data)

    def test_nonregular_artifact_is_rejected_without_following_symlink(self):
        real = self.root / "original"
        real.write_bytes(self.data)
        link = self.model / "tokenizer.json"
        link.symlink_to(real)
        with self.assertRaisesRegex(ValueError, "regular artifact"):
            a.verify_file(link, self.spec)
        self.assertEqual(real.read_bytes(), self.data)

    def test_symlink_component_and_repository_destinations_are_rejected(self):
        alias = self.root / "alias"
        alias.symlink_to(self.model, target_is_directory=True)
        for path in (alias, alias / "nested", SCRIPTS.parent / "weights"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                a.external_directory(path, create=True)
        self.assertFalse((SCRIPTS.parent / "weights").exists())

    def test_complete_transfer_publishes_only_verified_bytes_without_extra_copy(self):
        opener = Opener([Response(self.data, lengths=[str(len(self.data))])])
        result = a._download_one(self.model, self.spec, opener)
        final = self.model / "tokenizer.json"
        self.assertEqual(final.read_bytes(), self.data)
        self.assertEqual(final.stat().st_nlink, 1)
        self.assertEqual([p.name for p in self.model.iterdir()], ["tokenizer.json"])
        self.assertEqual(result["local_sha256"], hashlib.sha256(self.data).hexdigest())
        self.assertEqual(opener.calls[0][0],
                         f"https://huggingface.co/{a.MODEL_ID}/resolve/{a.REVISION}/tokenizer.json")
        self.assertEqual(opener.calls[0][1]["Accept-encoding"], "identity")

    def test_short_extra_corrupt_encoded_partial_or_ambiguous_response_never_publishes(self):
        responses = [
            Response(self.data[:-1]), Response(self.data + b"x"),
            Response(b"x" * len(self.data)),
            Response(self.data, encoding="gzip"), Response(self.data, status=206),
            Response(self.data, lengths=["0"]),
            Response(self.data, lengths=[str(len(self.data)), str(len(self.data))]),
        ]
        for index, response in enumerate(responses):
            with self.subTest(index=index):
                directory = self.root / str(index)
                directory.mkdir()
                with self.assertRaises(ValueError):
                    a._download_one(directory, self.spec, Opener([response]))
                self.assertFalse((directory / "tokenizer.json").exists())
                self.assertEqual(len(list(directory.iterdir())), 1)
                with self.assertRaisesRegex(ValueError, "retained attempt"):
                    a._check_names(directory)

    def test_competing_final_file_wins_and_verified_private_partial_is_retained(self):
        final = self.model / "tokenizer.json"
        opener = Opener([Response(self.data)], on_open=lambda: final.write_bytes(b"other publisher"))
        with self.assertRaises(FileExistsError):
            a._download_one(self.model, self.spec, opener)
        self.assertEqual(final.read_bytes(), b"other publisher")
        partials = list(self.model.glob(".mr09-olmoe-partial-*"))
        self.assertEqual(len(partials), 1)
        self.assertEqual(partials[0].read_bytes(), self.data)

    def synthetic_inventory(self):
        payloads = [f'{{"synthetic-file":{i}}}\n'.encode() for i in range(9)]
        specs = [metadata_spec(name, data, prior=name != "tokenizer.json")
                 for name, data in zip(a.FILES, payloads)]
        return specs, payloads

    def test_serial_full_acquisition_then_verified_reuse_uses_same_fixed_order(self):
        specs, payloads = self.synthetic_inventory()
        opener = Opener([Response(data) for data in payloads])
        capacity = SimpleNamespace(free=30064771072)
        with patch.object(a, "inventory", return_value=specs), \
                patch.object(a.shutil, "disk_usage", return_value=capacity), \
                patch.object(a.urllib.request, "build_opener", return_value=opener):
            result = a.acquire(self.model, "synthetic acquisition reference, not real authority")
            reused = a.acquire(self.model, "synthetic reuse reference")
        self.assertEqual(len(opener.calls), 9)
        self.assertEqual([url.rsplit("/", 1)[1] for url, _, _ in opener.calls], list(a.FILES))
        self.assertEqual(result["reused_files"], [])
        self.assertEqual(reused["reused_files"], sorted(a.FILES))
        self.assertEqual(result["artifacts"], reused["artifacts"])
        self.assertFalse(result["hub_cache_used"])
        self.assertFalse((self.model / a.LOCK).exists())

    def test_all_prior_files_are_validated_before_first_transport(self):
        specs, payloads = self.synthetic_inventory()
        (self.model / a.FILES[-1]).write_bytes(b"corrupt")
        with patch.object(a, "inventory", return_value=specs), \
                patch.object(a.urllib.request, "build_opener") as network:
            with self.assertRaises(ValueError):
                a.acquire(self.model, "synthetic")
        network.assert_not_called()
        self.assertEqual((self.model / a.FILES[-1]).read_bytes(), b"corrupt")
        self.assertFalse((self.model / a.LOCK).exists())

    def test_storage_threshold_and_missing_reference_precede_transfer(self):
        for reference, free in (("", 40000000000), ("synthetic", 30064771071)):
            with self.subTest(reference=reference), \
                    patch.object(a.shutil, "disk_usage", return_value=SimpleNamespace(free=free)), \
                    patch.object(a.urllib.request, "build_opener") as network:
                with self.assertRaises(ValueError):
                    a.acquire(self.model, reference)
                network.assert_not_called()
                self.assertEqual(list(self.model.iterdir()), [])

    def test_failed_reservation_is_retained_and_prevents_retry(self):
        lock = self.root / "attempt.json"
        with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
            with a.reservation(lock, {"id": 1}):
                raise RuntimeError("synthetic failure")
        original = lock.read_bytes()
        with self.assertRaises(FileExistsError):
            with a.reservation(lock, {"id": 2}):
                self.fail("an existing attempt must win")
        self.assertEqual(lock.read_bytes(), original)

    def test_changed_reservation_cannot_be_deleted_as_ours(self):
        lock = self.root / "attempt.json"
        with self.assertRaisesRegex(ValueError, "reservation changed"):
            with a.reservation(lock, {"id": 1}):
                lock.write_text('{"id":2}\n')
        self.assertEqual(json.loads(lock.read_text()), {"id": 2})

    def test_control_reader_rejects_ambiguous_or_oversized_json(self):
        path = self.root / "control.json"
        for data in (b'{"a":1,"a":2}', b'{"a":1.0}', b'{"a":NaN}', b"[]", b"x" * (a.CHUNK + 1)):
            with self.subTest(prefix=data[:30]):
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    a.strict_json(path)

    def test_output_collision_and_model_directory_receipt_are_rejected(self):
        output = self.root / "result.json"
        output.write_bytes(b"original")
        with self.assertRaisesRegex(ValueError, "already exists"):
            a.fresh_output(output, self.model)
        with self.assertRaisesRegex(ValueError, "outside"):
            a.fresh_output(self.model / "result.json", self.model)
        self.assertEqual(output.read_bytes(), b"original")

    def test_plaintext_publisher_redirect_is_rejected_before_following(self):
        request = a.urllib.request.Request("https://huggingface.co/fixed")
        with self.assertRaisesRegex(ValueError, "non-HTTPS"):
            a.HTTPSRedirects().redirect_request(request, None, 302, "Found", Message(), "http://example.org/file")

    def test_real_plan_cli_does_not_import_ml_or_open_transport(self):
        probe = r"""
import importlib.abc, runpy, sys, urllib.request
class NoML(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in ("torch", "transformers"):
            raise AssertionError("unexpected ML import")
sys.meta_path.insert(0, NoML())
sys.path.insert(0, sys.argv[1])
urllib.request.build_opener = lambda *args: (_ for _ in ()).throw(AssertionError("network"))
sys.argv = ["mr09_olmoe_artifacts.py", "plan"]
runpy.run_module("mr09_olmoe_artifacts", run_name="__main__")
"""
        result = subprocess.run([sys.executable, "-c", probe, str(SCRIPTS)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "unexecuted")


    def test_control_digest_binds_the_exact_parsed_bytes_not_a_second_file_read(self):
        path = self.root / "control.json"
        raw = b'{ "synthetic" : true }\n'
        path.write_bytes(raw)
        parsed, digest = a.read_control(path)
        path.write_bytes(b'{"synthetic":false}\n')
        self.assertEqual(parsed, {"synthetic": True})
        self.assertEqual(digest, hashlib.sha256(raw).hexdigest())
        self.assertNotEqual(digest, a.sha256_file(path))

    def assert_fifo_swap_is_rejected(self, operation):
        path = self.model / "swapped.json"
        path.write_bytes(self.data)
        probe = r"""
import json, os, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import mr09_olmoe_artifacts as a
path, operation, spec = Path(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])
def read():
    return a.read_control(path) if operation == "control" else a.verify_file(path, spec)
assert read(), "ordinary regular-file control must succeed"
original_open = os.open
swapped = False
def replace_at_open(name, flags, *args, **kwargs):
    global swapped
    if Path(name) == path and not swapped:
        path.unlink()
        os.mkfifo(path)
        swapped = True
        print("regular control passed; FIFO substituted", flush=True)
    return original_open(name, flags, *args, **kwargs)
with patch.object(a.os, "open", side_effect=replace_at_open):
    try:
        read()
    except ValueError:
        assert swapped
        print("FIFO rejected without waiting for a writer", flush=True)
    else:
        raise AssertionError("substituted FIFO must not be admitted")
"""
        try:
            result = subprocess.run(
                [sys.executable, "-c", probe, str(SCRIPTS), str(path), operation,
                 json.dumps({**self.spec, "file": path.name})],
                capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired as error:
            self.fail(f"{operation} reader blocked on the substituted FIFO: {error.stdout!r}")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "regular control passed; FIFO substituted",
            "FIFO rejected without waiting for a writer",
        ])
        self.assertTrue(stat.S_ISFIFO(path.lstat().st_mode))

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"), "named pipes unavailable")
    def test_control_swap_to_fifo_is_bounded_before_read(self):
        self.assert_fifo_swap_is_rejected("control")

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"), "named pipes unavailable")
    def test_artifact_swap_to_fifo_is_bounded_before_read(self):
        self.assert_fifo_swap_is_rejected("artifact")

    def test_artifact_publication_error_preserves_completed_observation_without_false_admission_failure(self):
        observation = {"status": "artifacts_verified_model_unexecuted",
                       "artifacts": [], "classification": "synthetic publication control"}
        output = self.root / "observation.json"
        stdout = io.StringIO()
        with patch.object(a, "verify", return_value=observation), \
                patch.object(a.os, "link", side_effect=OSError("synthetic publication failure")), \
                redirect_stdout(stdout):
            code = a.main(["verify", "--model-dir", str(self.model), "--output", str(output)])
        self.assertEqual(code, 1)
        envelope = json.loads(stdout.getvalue())
        self.assertEqual(envelope["status"], "operation_error")
        self.assertIn("operation failed", envelope["reason"])
        self.assertNotIn("admission failed", envelope["reason"])
        self.assertFalse(output.exists())
        retained = list(self.root.glob(".mr09-unpublished-*.json"))
        self.assertEqual(len(retained), 1)
        self.assertEqual(json.loads(retained[0].read_text()), observation)


if __name__ == "__main__":
    unittest.main()
