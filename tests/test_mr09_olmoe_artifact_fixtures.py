"""Synthetic capability checks through the actual artifact test methods.

Only the fixture helper's platform binding is modeled; no Windows execution,
publisher artifact, network, ML runtime or GPU is involved.
"""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mr09_fixture_support as fixtures
import test_mr09_olmoe_artifacts as originals


class FixtureResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.successful_subtests = []
        self.successful_methods = []

    def addSubTest(self, test, subtest, error):
        if error is None:
            self.successful_subtests.append(subtest.id())
        super().addSubTest(test, subtest, error)

    def addSuccess(self, test):
        self.successful_methods.append(test.id())
        super().addSuccess(test)


class ArtifactFixtureCapabilities(unittest.TestCase):
    PREFIX = "test_mr09_olmoe_artifacts.ArtifactTests."
    LINK_METHODS = (
        "test_nonregular_artifact_is_rejected_without_following_symlink",
        "test_symlink_component_and_repository_destinations_are_rejected",
    )
    REGULAR_METHODS = (
        "test_metadata_observation_keeps_unknown_prior_sha_separate",
        "test_prior_metadata_sha_is_also_enforced",
        "test_exact_length_and_identity_controls_reject_without_rewriting",
    )

    def test_optional_links_keep_integrity_and_repository_controls_attended(self):
        cases = (("nt", 1314), ("nt", 5), ("nt", 87), ("nt", None), ("posix", 1314))
        for platform, winerror in cases:
            with self.subTest(platform=platform, winerror=winerror):
                error = OSError("synthetic artifact-fixture capability error")
                if winerror is not None:
                    error.winerror = winerror
                names = [self.PREFIX + name for name in self.LINK_METHODS + self.REGULAR_METHODS]
                suite = unittest.defaultTestLoader.loadTestsFromNames(names)
                result = FixtureResult()
                # Do not change the shared os.name used by pathlib/tempfile.
                with (patch.object(fixtures, "os", SimpleNamespace(name=platform)),
                      patch.object(Path, "symlink_to", side_effect=error) as creation,
                      patch.object(originals.a, "verify_file", wraps=originals.a.verify_file) as verify,
                      patch.object(originals.a, "external_directory",
                                   wraps=originals.a.external_directory) as directory):
                    suite.run(result)
                self.assertEqual(result.testsRun, 5)
                self.assertEqual(creation.call_count, 2)
                self.assertEqual(result.failures, [])
                self.assertEqual(verify.call_count, 5)
                directory.assert_called_once_with(originals.SCRIPTS.parent / "weights", create=True)
                self.assertEqual(
                    [name for name in result.successful_methods if name in names[2:]], names[2:])
                for kind in ("file", "repository"):
                    self.assertEqual(sum(f"kind='{kind}'" in name
                                         for name in result.successful_subtests), 1)
                if platform == "nt" and winerror == 1314:
                    self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
                    self.assertEqual(len(result.skipped), 2)
                    self.assertTrue(all("winerror 1314" in reason
                                        and "fixture='symlink'" in test.id()
                                        for test, reason in result.skipped))
                else:
                    self.assertFalse(result.wasSuccessful())
                    self.assertEqual(len(result.errors), 2)
                    self.assertEqual(result.skipped, [])
                    self.assertTrue(all("fixture='symlink'" in test.id()
                                        and "synthetic artifact-fixture capability error" in detail
                                        for test, detail in result.errors))


if __name__ == "__main__":
    unittest.main()
