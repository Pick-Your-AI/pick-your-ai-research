"""Exercise source recheck metadata through the actual isolated market CLI."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from tests import test_market_validation as market_fixtures


class MarketSourceRechecks(unittest.TestCase):
    def setUp(self):
        self.fixture = market_fixtures.MarketValidation()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    @staticmethod
    def legacy():
        return {
            'access_date': '2026-10-18', 'access_status': 'Synthetic access blocked',
            'version': 'Unknown; page was not retrieved', 'region': 'Unknown',
            'confidence': 'Synthetic confidence in access failure only',
            'limitations': 'No product behavior or source claim verified',
            'rights': 'Unknown; no permission established',
            'claim': 'Synthetic access attempt failed',
            'publisher': 'Synthetic publisher', 'evidence_class': 'Synthetic fixture',
            'url': 'https://example.com/synthetic',
        }

    @classmethod
    def grouped(cls):
        record = cls.legacy()
        claim = {key: record.pop(key) for key in
                 ('claim', 'publisher', 'evidence_class', 'url')}
        record.update(
            claims=[claim], method='Synthetic offline fixture; no retrieval',
            reviewed_urls=[{'url': claim['url'], 'publisher': claim['publisher'],
                            'access_status': 'Synthetic access blocked'}])
        return record

    def check_records(self, records, *, valid):
        data = deepcopy(self.fixture.data)
        data['sources.json'][0]['rechecks'] = records
        original = deepcopy(data)
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.fixture.run_validator(data, optimized)
                if valid:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Market integrity OK', result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('MarketValidationError', result.stderr)
                    self.assertIn('rechecks', result.stderr)
                    self.assertNotIn('Market integrity OK', result.stdout)
                # A validation failure must not rewrite a historical claim.
                self.assertEqual(json.loads((self.fixture.base / 'sources.json').read_text()),
                                 original['sources.json'])
        self.assertEqual(data, original)

    def test_absent_empty_and_both_retained_record_formats_pass(self):
        for optimized in (False, True):
            result = self.fixture.run_validator(self.fixture.data, optimized)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.check_records([], valid=True)
        legacy, grouped = self.legacy(), self.grouped()
        grouped['claims'].append({
            'claim': 'Another synthetic assertion with independently recorded URLs',
            'publisher': 'Different synthetic publisher',
            'evidence_class': 'Unknown; not promoted by validation',
            'source_urls': ['https://example.org/first', 'https://example.org/second'],
        })
        self.check_records([legacy, grouped], valid=True)

    def test_recheck_container_and_claim_shape_must_be_unambiguous(self):
        for records in (None, True, 1, '', {}, [None], [False], [[]]):
            with self.subTest(records=records):
                self.check_records(records, valid=False)
        missing = self.legacy()
        del missing['claim']
        mixed = self.grouped()
        mixed['claim'] = 'A second representation must not be silently ignored'
        self.check_records([missing], valid=False)
        self.check_records([mixed], valid=False)
        for claims in (None, True, 1, '', {}, [], [None], ['text'], [[]]):
            with self.subTest(claims=claims):
                record = self.grouped()
                record['claims'] = claims
                self.check_records([record], valid=False)

    def test_required_recheck_metadata_is_nonempty_text_in_both_formats(self):
        for factory in (self.legacy, self.grouped):
            for field in ('access_status', 'version', 'region', 'confidence',
                          'limitations', 'rights'):
                for missing in (False, True):
                    with self.subTest(format=factory.__name__, field=field, missing=missing):
                        record = factory()
                        if missing:
                            del record[field]
                        else:
                            record[field] = ' \t'
                        self.check_records([record], valid=False)
            for value in (None, True, 12, [], {}):
                record = factory()
                record['version'] = value
                self.check_records([record], valid=False)

    def test_recheck_dates_are_real_canonical_dates_not_freshness_approval(self):
        for factory in (self.legacy, self.grouped):
            for value in (None, True, 1, [], {}, '', '2026-02-30', '2026-10-18\n',
                          '20261018', '2026-W42-7', '2026-10-18T00:00:00Z',
                          '\u0662\u0660\u0662\u0666-10-18'):
                with self.subTest(format=factory.__name__, value=value):
                    record = factory()
                    record['access_date'] = value
                    self.check_records([record], valid=False)
            record = factory()
            del record['access_date']
            self.check_records([record], valid=False)
            for value in ('0001-01-01', '2024-02-29', '9999-12-31'):
                record = factory()
                record['access_date'] = value
                self.check_records([record], valid=True)

    def test_each_claim_requires_text_publisher_and_evidence_class(self):
        for factory in (self.legacy, self.grouped):
            for field in ('claim', 'publisher', 'evidence_class'):
                for mutation in ('missing', 'blank', 'boolean'):
                    with self.subTest(format=factory.__name__, field=field, mutation=mutation):
                        record = factory()
                        claim = record['claims'][0] if 'claims' in record else record
                        if mutation == 'missing':
                            del claim[field]
                        else:
                            claim[field] = '' if mutation == 'blank' else True
                        self.check_records([record], valid=False)
            for value in (None, 12, [], {}):
                record = factory()
                claim = record['claims'][0] if 'claims' in record else record
                claim['claim'] = value
                self.check_records([record], valid=False)

    def test_every_claim_and_reviewed_url_uses_the_existing_url_guard(self):
        invalid = ('https:///missing-host', 'file:///tmp/synthetic',
                   'https://example.com:bad/path', 'https://example.com:65536/path',
                   'https://@example.com/path', 'https://example.com/a b',
                   'https://exam\nple.com/path', 'https://example.com/path\x7f')
        for location in ('legacy', 'claim', 'source_urls', 'reviewed_urls'):
            for value in invalid:
                with self.subTest(location=location, value=value):
                    record = self.legacy() if location == 'legacy' else self.grouped()
                    if location == 'legacy':
                        record['url'] = value
                    elif location == 'claim':
                        record['claims'][0]['url'] = value
                    elif location == 'source_urls':
                        # A good url must not conceal a bad additional citation.
                        record['claims'][0]['source_urls'] = ['https://example.org/valid', value]
                    else:
                        record['reviewed_urls'][0]['url'] = value
                    self.check_records([record], valid=False)

    def test_claim_url_alternatives_validate_every_provided_representation(self):
        for factory in (self.legacy, self.grouped):
            record = factory()
            claim = record['claims'][0] if 'claims' in record else record
            del claim['url']
            self.check_records([record], valid=False)
            claim['source_urls'] = ['https://example.org/one', 'https://example.org/two']
            self.check_records([record], valid=True)
            for value in (None, True, '', {}, [], [None], [True], [[]]):
                with self.subTest(format=factory.__name__, source_urls=value):
                    claim['source_urls'] = value
                    self.check_records([record], valid=False)
            claim['source_urls'] = ['https://example.org/valid']
            claim['url'] = None
            self.check_records([record], valid=False)

    def test_grouped_records_keep_method_and_per_url_readback_metadata(self):
        for field in ('method', 'reviewed_urls'):
            record = self.grouped()
            del record[field]
            self.check_records([record], valid=False)
        for value in (None, False, 3, [], {}, ' \t'):
            record = self.grouped()
            record['method'] = value
            self.check_records([record], valid=False)
        for value in (None, False, 3, '', {}, [], [None], ['https://example.com/']):
            record = self.grouped()
            record['reviewed_urls'] = value
            self.check_records([record], valid=False)
        for field in ('url', 'publisher', 'access_status'):
            for mutation in ('missing', 'blank', 'boolean'):
                record = self.grouped()
                url = record['reviewed_urls'][0]
                if mutation == 'missing':
                    del url[field]
                else:
                    url[field] = '' if mutation == 'blank' else True
                self.check_records([record], valid=False)
        legacy = self.legacy()
        legacy['reviewed_urls'] = [{'url': 'https://example.com:invalid'}]
        self.check_records([legacy], valid=False)

    def test_all_committed_history_remains_valid_and_unchanged(self):
        # Exercise real retained structure; passing does not endorse its claims.
        source_path = Path(__file__).resolve().parents[1] / 'research/market/sources.json'
        original = source_path.read_bytes()
        sources = json.loads(original)
        self.check_records([deepcopy(record) for source in sources
                            for record in source.get('rechecks', [])], valid=True)
        self.assertEqual(source_path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
