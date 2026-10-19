"""Model fixture capability errors; these controls do not execute Windows."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import mr09_fixture_support as fixtures


class FixtureResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.successful_subtests = []

    def addSubTest(self, test, subtest, error):
        if error is None:
            self.successful_subtests.append(subtest.id())
        super().addSubTest(test, subtest, error)


class SymlinkFixtureCapabilities(unittest.TestCase):
    METHODS = (
        "test_mr09_preflight.PreflightOutputPreservationTests."
        "test_preserve_mode_rejects_every_occupied_path_before_capacity_queries",
        "test_mr09_preflight.PreflightOutputPreservationTests."
        "test_preserve_mode_rejects_paths_arriving_during_capacity_queries",
        "test_mr09_native_qualify.NativeOutputPublicationTests."
        "test_existing_result_or_preflight_paths_reject_before_any_launch",
        "test_mr09_native_qualify.NativeOutputPublicationTests."
        "test_preflight_paths_arriving_after_launcher_admission_stop_before_child",
        "test_mr09_native_qualify.NativeOutputPublicationTests."
        "test_result_arriving_during_child_preserves_both_observations_and_stops_telemetry",
        "test_mr09_measure.MeasurementOutputPreservationTests."
        "test_existing_output_rejects_both_actions_without_changing_observations",
        "test_mr09_granite31.SupplementalOutputPreservation."
        "test_existing_result_entries_stop_preflight_and_both_actions_without_mutation",
        "test_mr09_granite31.SupplementalOutputPreservation."
        "test_result_arriving_during_preflight_or_either_action_is_preserved",
    )

    def exercise_original_methods(self, platform, error):
        suite = unittest.defaultTestLoader.loadTestsFromNames(self.METHODS)
        result = FixtureResult()
        # Replace only the helper's binding, never the shared os.name used by
        # pathlib and tempfile. All non-link fixtures use the real local OS.
        with (patch.object(fixtures, "os", SimpleNamespace(name=platform)),
              patch.object(Path, "symlink_to", side_effect=error) as creation):
            suite.run(result)
        self.assertEqual(result.testsRun, 8)
        self.assertEqual(creation.call_count, 34)
        self.assertEqual(len(result.successful_subtests), 34)
        self.assertTrue(all("kind='file'" in item or "kind='directory'" in item
                            for item in result.successful_subtests))
        return result

    def test_windows_privilege_error_skips_only_unavailable_link_subcases(self):
        error = OSError("synthetic missing symbolic-link privilege")
        error.winerror = 1314
        result = self.exercise_original_methods("nt", error)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
        self.assertEqual(len(result.skipped), 34)
        self.assertTrue(all("winerror 1314" in reason for _, reason in result.skipped))

    def test_other_fixture_errors_remain_errors_in_original_methods(self):
        for platform, winerror in (("nt", 87), ("posix", 1314), ("nt", None)):
            with self.subTest(platform=platform, winerror=winerror):
                error = OSError("synthetic unrelated fixture error")
                if winerror is not None:
                    error.winerror = winerror
                result = self.exercise_original_methods(platform, error)
                self.assertFalse(result.wasSuccessful())
                self.assertEqual(len(result.errors), 34)
                self.assertEqual(result.failures, [])
                self.assertEqual(result.skipped, [])
                self.assertTrue(all("synthetic unrelated fixture error" in traceback
                                    for _, traceback in result.errors))

    def test_unrelated_creation_exceptions_are_reraised_unchanged(self):
        cases = (("nt", 5), ("nt", 87), ("nt", None), ("posix", 1314))
        for platform, winerror in cases:
            with self.subTest(platform=platform, winerror=winerror):
                error = OSError("synthetic original error")
                if winerror is not None:
                    error.winerror = winerror
                link, target = Mock(), object()
                link.symlink_to.side_effect = error
                with patch.object(fixtures, "os", SimpleNamespace(name=platform)):
                    with self.assertRaises(OSError) as raised:
                        fixtures.symlink_or_skip(link, target)
                self.assertIs(raised.exception, error)
                link.symlink_to.assert_called_once_with(target)


if __name__ == "__main__":
    unittest.main()
