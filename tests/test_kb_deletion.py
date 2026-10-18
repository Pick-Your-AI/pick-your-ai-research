"""Synthetic fixtures only: these are not deletion or authorization evidence."""
import unittest

from kb_deletion_prototype import Receipt, State, evaluate


class DeletionLineageCases(unittest.TestCase):
    def test_no_event_is_skipped_with_fixed_severity(self):
        result = evaluate(False, None, ())
        self.assertEqual((result.outcome, result.severity), ("skipped", "error"))

    def test_unknown_event_cannot_pass(self):
        self.assertEqual(evaluate(None, True, ()).outcome, "unknown")

    def test_all_current_serving_destinations_accounted_for(self):
        rows = (Receipt("chunks", State.TOMBSTONED, True),
                Receipt("index", State.EXCLUDED, True))
        self.assertEqual(evaluate(True, True, rows).outcome, "pass")

    def test_separate_backup_does_not_claim_erasure(self):
        row = Receipt("backup", State.BACKUP, True)
        result = evaluate(True, True, (row,))
        self.assertEqual(result.outcome, "pass")
        self.assertEqual(row.state, State.BACKUP)
        self.assertEqual(result.reason, "serving_scope_accounted_for")

    def test_empty_scope_requires_positive_completeness_evidence(self):
        for complete in (False, None):
            self.assertEqual(evaluate(True, complete, ()).outcome, "unknown")
        self.assertEqual(evaluate(True, True, ()).outcome, "pass")

    def test_untracked_memory_copy_prevents_pass(self):
        rows = (Receipt("index", State.TOMBSTONED, True),)
        self.assertEqual(evaluate(True, False, rows).outcome, "unknown")

    def test_current_stale_copy_dominates_unrelated_unknowns(self):
        rows = (Receipt("index", State.SERVING, True), Receipt("memory", State.UNKNOWN))
        for complete in (True, False, None):
            self.assertEqual(evaluate(True, complete, rows).outcome, "fail")

    def test_unique_stale_copy_dominates_unrelated_identity_gaps(self):
        stale = Receipt("index", State.SERVING, True)
        for unknowns in ((Receipt("", State.UNKNOWN),),
                         (Receipt("other", State.UNKNOWN), Receipt("other", State.UNKNOWN))):
            self.assertEqual(evaluate(True, None, (stale, *unknowns)).outcome, "fail")

    def test_old_or_unbound_receipts_do_not_prove_current_state(self):
        for state in State:
            for match in (False, None):
                with self.subTest(state=state, match=match):
                    self.assertEqual(evaluate(True, True, (Receipt("edge", state, match),)).outcome,
                                     "unknown")

    def test_unknown_current_destination_is_unknown(self):
        self.assertEqual(evaluate(True, True, (Receipt("edge", State.UNKNOWN, True),)).outcome,
                         "unknown")

    def test_duplicate_or_missing_edge_identity_is_ambiguous(self):
        for rows in ((Receipt("", State.TOMBSTONED, True),),
                     (Receipt("same", State.TOMBSTONED, True), Receipt("same", State.SERVING, True))):
            self.assertEqual(evaluate(True, True, rows).reason, "ambiguous_lineage_identity")


if __name__ == "__main__":
    unittest.main()
