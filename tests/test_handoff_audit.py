"""Regression checks for lost or overstated audit receipts; mutations stay in memory."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.validate_handoff_audit import HandoffValidationError, validate

BASE = Path(__file__).resolve().parents[1] / 'research' / 'market'


class HandoffAuditValidation(unittest.TestCase):
    def setUp(self):
        # Synthetic attribution fixture, independent of future owner decisions.
        cutoff = '2026-10-18T02:50:05Z'
        historical = {'reviewer': 'consumer', 'reviewed_commit': 'a' * 40}
        def response(role):
            return {'reviewer': 'consumer', 'role': role,
                    'url': 'https://example.com/synthetic-receipt/' + role,
                    'scope': 'Synthetic test-only scope',
                    'retained_unknowns_and_next_action': 'Synthetic follow-up',
                    'submitted_at': '2026-10-17T00:00:00Z',
                    'reviewed_commit': None, 'commit_basis': 'Explicitly unknown'}

        self.ledger = [
            {'market_issue': 48, 'consumer_issue': 6,
             'consumer_owner': ['consumer', 'coowner'],
             'receiving_review_status': 'scoped_response_recorded',
             'owner_review': historical},
            {'market_issue': 49, 'consumer_issue': 6,
             'consumer_owner': ['consumer', 'coowner'],
             'receiving_review_status': 'author_integration_only',
             'responses': [response('author_integration')]},
            {'market_issue': 59, 'consumer_issue': 6,
             'consumer_owner': ['consumer', 'coowner'],
             'receiving_review_status': 'scoped_response_recorded',
             'responses': [response('receiving_owner')],
             'current_audit_acceptance': 'Pending current artifact review'}]
        coverage = {'total_rows': 3, 'declared_pairs': 3,
                    'historical_owner_review_rows': 1, 'new_response_records': 2,
                    'receiving_review_status_counts':
                        {'scoped_response_recorded': 2, 'author_integration_only': 1},
                    'current_audit_acceptance_pending': 1}
        self.readback = {
            'issues': [{'number': n, 'assignees': ['consumer', 'coowner'],
                        'parent': None, 'sub_issues': []} for n in (6, 48, 49, 59)],
            'snapshot_cutoff_utc': cutoff, 'base_commit': 'b' * 40,
            'declared_handoff_pairs': [[48, 6], [49, 6], [59, 6]],
            'historical_owner_reviews': [{'market_issue': 48, 'consumer_issue': 6,
                                         'owner_review': deepcopy(historical)}],
            'new_scoped_responses': [
                {'market_issue': row['market_issue'], 'consumer_issue': 6,
                 **deepcopy(item)} for row in self.ledger
                for item in row.get('responses', [])],
            'handoff_coverage': coverage, 'pull_requests': [{'number': 44}]}
        self.audit = {'snapshot_cutoff_utc': cutoff, 'base_commit': 'b' * 40,
                      'handoff_coverage': deepcopy(coverage),
                      'issues': [{'related_prs': [44]}]}

    def test_synthetic_attribution_fixture_is_valid(self):
        self.check()

    def check(self):
        return validate(self.ledger, self.readback, self.audit)

    def test_committed_snapshot_is_consistent(self):
        load = lambda name: json.loads((BASE / name).read_text(encoding='utf-8'))
        validate(load('handoffs.json'), load('handoff-audit-readback.json'), load('audit.json'))

    def test_missing_declared_consumer_is_rejected(self):
        pair = tuple(self.readback['declared_handoff_pairs'][0])
        self.ledger = [r for r in self.ledger
                       if (r['market_issue'], r['consumer_issue']) != pair]
        with self.assertRaisesRegex(HandoffValidationError, 'missing declared'):
            self.check()

    def test_live_coowner_cannot_be_dropped(self):
        self.ledger[0]['consumer_owner'].pop()
        with self.assertRaisesRegex(HandoffValidationError, 'assignees differ'):
            self.check()

    def test_author_acknowledgement_is_not_receiving_review(self):
        row = next(r for r in self.ledger
                   if r['receiving_review_status'] == 'author_integration_only')
        row['receiving_review_status'] = 'scoped_response_recorded'
        with self.assertRaisesRegex(HandoffValidationError, 'promoted'):
            self.check()

    def test_historical_attribution_cannot_be_rewritten(self):
        row = next(r for r in self.ledger if 'owner_review' in r)
        row['owner_review']['reviewed_commit'] = '0' * 40
        with self.assertRaisesRegex(HandoffValidationError, 'historical review'):
            self.check()

    def test_receipt_cannot_be_transferred_to_another_producer(self):
        row = next(r for r in self.ledger if r.get('responses'))
        response = row['responses'].pop()
        target = next(r for r in self.ledger
                      if r['market_issue'] != row['market_issue'] and
                      r['consumer_issue'] == row['consumer_issue'])
        target.setdefault('responses', []).append(deepcopy(response))
        # Keep category metadata coherent to exercise the attribution guard itself.
        from scripts.validate_handoff_audit import response_status
        for r in (row, target):
            r['receiving_review_status'] = response_status(r)
        with self.assertRaisesRegex(HandoffValidationError, 'receipt moved'):
            self.check()

    def test_receipt_cannot_override_its_enclosing_pair(self):
        source, target = self.ledger[2], self.ledger[1]
        response = source['responses'].pop()
        response.update(market_issue=source['market_issue'],
                        consumer_issue=source['consumer_issue'])
        target['responses'].append(response)
        # Preserve coherent status counts so the embedded pair cannot hide a
        # transfer behind otherwise accurate coverage metadata.
        from collections import Counter
        from scripts.validate_handoff_audit import response_status
        for row in (source, target):
            row['receiving_review_status'] = response_status(row)
        counts = dict(Counter(response_status(row) for row in self.ledger))
        for snapshot in (self.readback, self.audit):
            snapshot['handoff_coverage']['receiving_review_status_counts'] = counts
        with self.assertRaisesRegex(HandoffValidationError, 'reserved pair keys'):
            self.check()

    def test_parent_cannot_list_a_child_without_its_reciprocal_parent(self):
        parent, child = self.readback['issues'][:2]
        parent['sub_issues'] = [child['number']]
        child['parent'] = {'number': parent['number']}
        self.check()
        child['parent'] = None
        with self.assertRaisesRegex(HandoffValidationError, 'parent/sub-issue mismatch'):
            self.check()

    def test_context_cannot_silently_become_current_audit_acceptance(self):
        row = next(r for r in self.ledger if r['market_issue'] == 59)
        row['current_audit_acceptance'] = 'Accepted'
        with self.assertRaisesRegex(HandoffValidationError, 'current audit acceptance'):
            self.check()

    def test_optimistic_summary_count_is_rejected(self):
        self.readback['handoff_coverage']['total_rows'] += 1
        self.audit['handoff_coverage'] = deepcopy(self.readback['handoff_coverage'])
        with self.assertRaisesRegex(HandoffValidationError, 'row total'):
            self.check()
