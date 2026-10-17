import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/wr6-sequence-accounting.json'


def resident_envelope(case):
    """Recompute W-R6 request-to-sequence accounting (workload-use-case.md).

    Demand D = R * E needs known requests and expansion in a matching admission
    scope; resident S = min(D, A), or D when admission is unknown.
    """
    if not case['scope_matches'] or case['requests'] is None or case['expansion'] is None:
        return None, None
    demand = case['requests'] * case['expansion']
    admission = case['admission']
    return demand, demand if admission is None else min(demand, admission)


class WR6SequenceAccounting(unittest.TestCase):
    def test_fixture_is_synthetic(self):
        self.assertTrue(json.loads(FIXTURE.read_text())['synthetic'])

    def test_cases_match_the_documented_rule(self):
        for case in json.loads(FIXTURE.read_text())['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual(resident_envelope(case),
                                 (case['expected_demand'], case['expected_resident']))


if __name__ == '__main__':
    unittest.main()
