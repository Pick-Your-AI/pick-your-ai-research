"""Run mobile migration regressions in the normal research validation suite."""
import importlib.util
import sys
from pathlib import Path


def load_tests(loader, tests, pattern):
    mobile = Path(__file__).resolve().parents[1] / "prompts/mobile"
    # The standalone test module imports its adjacent migration utility.
    sys.path.insert(0, str(mobile))
    try:
        spec = importlib.util.spec_from_file_location(
            "mobile_reference_regressions", mobile / "test_migrate_references.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return loader.loadTestsFromModule(module)
    finally:
        sys.path.remove(str(mobile))
