"""Audit-receipt regressions use synthetic in-memory or temporary-file fixtures."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_handoff_audit import HandoffValidationError, read_json, validate

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
                      'issues': [{'number': 48, 'related_prs': [44]}]}

    def test_synthetic_attribution_fixture_is_valid(self):
        self.check()

    def check(self):
        return validate(self.ledger, self.readback, self.audit)

    def test_committed_snapshot_is_consistent(self):
        load = lambda name: read_json(BASE / name)
        validate(load('handoffs.json'), load('handoff-audit-readback.json'), load('audit.json'))

    def identifier_locations(self):
        parent, child = self.readback['issues'][:2]
        parent['sub_issues'] = [child['number']]
        child['parent'] = {'number': parent['number']}
        child['blocked_by'] = [49]
        return {
            'snapshot issue': (parent, 'number'),
            'native parent': (child['parent'], 'number'),
            'native child': (parent['sub_issues'], 0),
            'native blocker': (child['blocked_by'], 0),
            'ledger producer': (self.ledger[0], 'market_issue'),
            'ledger consumer': (self.ledger[0], 'consumer_issue'),
            'declared producer': (self.readback['declared_handoff_pairs'][0], 0),
            'declared consumer': (self.readback['declared_handoff_pairs'][0], 1),
            'historical producer': (self.readback['historical_owner_reviews'][0], 'market_issue'),
            'historical consumer': (self.readback['historical_owner_reviews'][0], 'consumer_issue'),
            'response producer': (self.readback['new_scoped_responses'][0], 'market_issue'),
            'response consumer': (self.readback['new_scoped_responses'][0], 'consumer_issue'),
            'snapshot PR': (self.readback['pull_requests'][0], 'number'),
            'classified issue': (self.audit['issues'][0], 'number'),
            'related PR': (self.audit['issues'][0]['related_prs'], 0),
        }

    def test_positive_integer_identifiers_preserve_native_relationships(self):
        self.identifier_locations()
        self.check()

    def test_numeric_aliases_cannot_match_issue_or_pr_identities(self):
        for label, (container, key) in self.identifier_locations().items():
            original = container[key]
            with self.subTest(location=label):
                container[key] = float(original)
                try:
                    with self.assertRaisesRegex(HandoffValidationError, 'positive integer'):
                        self.check()
                finally:
                    container[key] = original

    def test_issue_identifiers_reject_other_json_types_and_nonpositive_integers(self):
        for value in (True, False, 0, -1, 1.5, '6', None, [], {}):
            with self.subTest(value=value):
                self.readback['issues'][0]['number'] = value
                with self.assertRaisesRegex(HandoffValidationError, 'positive integer'):
                    self.check()

    def raw_documents(self):
        return {name: json.dumps(value) for name, value in (
            ('handoffs.json', self.ledger),
            ('handoff-audit-readback.json', self.readback),
            ('audit.json', self.audit))}

    def run_cli(self, documents, optimized):
        # Copy the real standalone entry point so ROOT points at disposable
        # records; the repository's actual audit files are never modified.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / 'scripts' / 'validate_handoff_audit.py'
            script.parent.mkdir()
            shutil.copyfile(BASE.parents[1] / 'scripts' / script.name, script)
            market = root / 'research' / 'market'
            market.mkdir(parents=True)
            for name, text in documents.items():
                (market / name).write_text(text, encoding='utf-8')
            options = ['-O'] if optimized else []
            return subprocess.run([sys.executable, *options, str(script)],
                                  cwd=root, capture_output=True, text=True,
                                  timeout=30)

    def test_cli_accepts_valid_json_and_finite_optional_values(self):
        for extra in ('', '"synthetic_optional": [null, 0, 0.125, -1e308, 1e308], '):
            documents = {name: text.replace('{', '{' + extra, 1)
                         for name, text in self.raw_documents().items()}
            for optimized in (False, True):
                with self.subTest(extra=bool(extra), optimized=optimized):
                    result = self.run_cli(documents, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Handoff audit integrity OK', result.stdout)

    def test_cli_rejects_identifier_aliases_in_each_input(self):
        # Make 1 a real synthetic issue/PR identity so true would otherwise join
        # it. Keep every reference consistent before changing one input only.
        def remap(value):
            if isinstance(value, dict):
                return {key: remap(item) for key, item in value.items()}
            if isinstance(value, list):
                return [remap(item) for item in value]
            return 1 if type(value) is int and value in (6, 44) else value

        originals = {name: remap(json.loads(text)) for name, text in self.raw_documents().items()}
        for optimized in (False, True):
            valid = self.run_cli({name: json.dumps(value) for name, value in originals.items()}, optimized)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            for name, path in (
                    ('handoffs.json', (0, 'consumer_issue')),
                    ('handoff-audit-readback.json', ('issues', 0, 'number')),
                    ('audit.json', ('issues', 0, 'related_prs', 0))):
                for alias in (True, 1.0):
                    with self.subTest(input=name, alias=alias, optimized=optimized):
                        documents = deepcopy(originals)
                        container = documents[name]
                        for part in path[:-1]:
                            container = container[part]
                        container[path[-1]] = alias
                        result = self.run_cli({key: json.dumps(value) for key, value in documents.items()}, optimized)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn('positive integer', result.stderr)
                        self.assertNotIn('Handoff audit integrity OK', result.stdout)

    def test_cli_rejects_duplicate_object_keys_in_every_input(self):
        keys = {
            'handoffs.json': ('market_issue', 'reviewer'),
            'handoff-audit-readback.json': ('issues', 'reviewer'),
            'audit.json': ('snapshot_cutoff_utc', 'total_rows')}
        for name, duplicate_keys in keys.items():
            for key in duplicate_keys:
                for optimized in (False, True):
                    with self.subTest(name=name, key=key, optimized=optimized):
                        documents = self.raw_documents()
                        marker = json.dumps(key) + ':'
                        self.assertIn(marker, documents[name])
                        documents[name] = documents[name].replace(
                            marker, marker + ' null, ' + marker, 1)
                        result = self.run_cli(documents, optimized)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn('duplicate JSON object key', result.stderr)
                        self.assertIn(name, result.stderr)
                        self.assertNotIn('Handoff audit integrity OK', result.stdout)

    def test_cli_rejects_nonfinite_and_overflow_numbers_in_every_input(self):
        for name in self.raw_documents():
            for value in ('NaN', 'Infinity', '-Infinity', '1e999', '-1e999'):
                for optimized in (False, True):
                    with self.subTest(name=name, value=value, optimized=optimized):
                        documents = self.raw_documents()
                        documents[name] = documents[name].replace(
                            '{', '{"synthetic_extra": ' + value + ', ', 1)
                        result = self.run_cli(documents, optimized)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        expected = ('finite numeric range' if 'e999' in value
                                    else 'non-finite JSON number')
                        self.assertIn(expected, result.stderr)
                        self.assertIn(name, result.stderr)
                        self.assertNotIn('Handoff audit integrity OK', result.stdout)

    def test_duplicate_snapshot_issue_cannot_hide_conflicting_assignees(self):
        duplicate = deepcopy(self.readback['issues'][0])
        duplicate['assignees'] = ['synthetic-other-owner']
        self.readback['issues'].insert(0, duplicate)
        with self.assertRaisesRegex(HandoffValidationError, 'duplicate snapshot issue'):
            self.check()

    def test_duplicate_historical_pair_cannot_hide_conflicting_review(self):
        duplicate = deepcopy(self.readback['historical_owner_reviews'][0])
        duplicate['owner_review']['reviewer'] = 'synthetic-other-owner'
        self.readback['historical_owner_reviews'].insert(0, duplicate)
        with self.assertRaisesRegex(HandoffValidationError, 'duplicate historical review pair'):
            self.check()

    def test_duplicate_declared_pair_cannot_disappear_from_coverage(self):
        self.readback['declared_handoff_pairs'].append(
            deepcopy(self.readback['declared_handoff_pairs'][0]))
        with self.assertRaisesRegex(HandoffValidationError, 'duplicate declared handoff pair'):
            self.check()

    def test_duplicate_snapshot_pr_cannot_hide_conflicting_state(self):
        self.readback['pull_requests'][0]['state'] = 'open'
        duplicate = deepcopy(self.readback['pull_requests'][0])
        duplicate['state'] = 'closed'
        self.readback['pull_requests'].append(duplicate)
        with self.assertRaisesRegex(HandoffValidationError, 'duplicate snapshot pull request'):
            self.check()

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
