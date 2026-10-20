"""Offline model-path privacy fixtures; no GPU observations or model downloads."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from mr09_fixture_support import symlink_or_skip


ROOT = Path(__file__).resolve().parents[1]
INSTRUMENTS = {}
for name in ("mr09_measure", "mr09_granite31_measure"):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    INSTRUMENTS[name] = module


class ModelPathSanitization(unittest.TestCase):
    def test_absolute_alias_and_canonical_paths_are_removed_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            actual = root / "canonical"
            actual.mkdir()
            alias = root / "private-operator-alias"
            symlink_or_skip(alias, actual)
            canonical_model = actual / "model"
            canonical_model.mkdir()
            model = alias / "model"
            self.assertTrue(alias.is_symlink())
            self.assertEqual(model.resolve(), canonical_model)
            for name, module in INSTRUMENTS.items():
                with self.subTest(instrument=name):
                    original = {
                        "model_id": module.MODEL_ID,
                        "revision": module.REVISION,
                        "failure": f"load {model}; resolved {canonical_model}",
                        "nested": [str(model), {"canonical": str(canonical_model),
                                                "artifact": (model / "config.json").as_posix()}],
                        "measurement": {"bytes": 123, "seconds": 0.25, "valid": True,
                                        "missing": None, "literal": "model execution"},
                        "packages": {"synthetic-model-runtime": "1.2.3"},
                    }
                    before = copy.deepcopy(original)
                    expected = copy.deepcopy(original)
                    expected["failure"] = "load $MODEL_DIR; resolved $MODEL_DIR"
                    expected["nested"] = ["$MODEL_DIR", {"canonical": "$MODEL_DIR",
                                                         "artifact": "$MODEL_DIR/config.json"}]
                    result = module.sanitized(original, SimpleNamespace(model_dir=model))
                    self.assertEqual(result, expected)
                    self.assertEqual(original, before)
                    self.assertNotIn("private-operator-alias", json.dumps(result))
                    self.assertNotIn(str(root), json.dumps(result))

    def test_nested_alias_is_removed_before_its_canonical_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            canonical = Path(directory).resolve() / "model"
            canonical.mkdir()
            alias = canonical / "private-alias"
            symlink_or_skip(alias, canonical)
            self.assertTrue(alias.is_symlink())
            self.assertEqual(alias.resolve(), canonical)
            for name, module in INSTRUMENTS.items():
                with self.subTest(instrument=name):
                    value = [str(alias), (alias / "config.json").as_posix(), str(canonical)]
                    self.assertEqual(module.sanitized(value, SimpleNamespace(model_dir=alias)),
                                     ["$MODEL_DIR", "$MODEL_DIR/config.json", "$MODEL_DIR"])

    def test_relative_model_name_does_not_rewrite_plain_metadata(self):
        model = Path("model")
        for name, module in INSTRUMENTS.items():
            with self.subTest(instrument=name):
                value = {"description": "model execution", "model_id": "publisher/model",
                         "relative_name": "model", "absolute": str(model.absolute()),
                         "canonical": str(model.resolve()), "tokens": 256}
                expected = {**value, "absolute": "$MODEL_DIR", "canonical": "$MODEL_DIR"}
                self.assertEqual(module.sanitized(value, SimpleNamespace(model_dir=model)), expected)


if __name__ == "__main__":
    unittest.main()
