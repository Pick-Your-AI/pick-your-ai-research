"""Check market-note integrity, not truth, rights, benchmark quality or acceptance."""
import json
import math
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research' / 'market'


class MarketValidationError(ValueError):
    """A market integrity predicate failed, including under optimized Python."""


def require(condition, message):
    if not condition:
        raise MarketValidationError(message)


def read(name):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'{name}: duplicate JSON object key: {key!r}')
            result[key] = value
        return result

    def reject_constant(value):
        raise MarketValidationError(f'{name}: non-finite JSON number: {value}')

    def finite_float(value):
        number = float(value)
        require(math.isfinite(number), f'{name}: JSON number exceeds finite numeric range')
        return number

    return json.loads((BASE / name).read_text(encoding='utf-8'),
                      object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def validate():
    competitors, sources, matrix, backlog = (read(n) for n in
        ('competitors.json', 'sources.json', 'features.json', 'research-backlog.json'))
    ids = {c['id'] for c in competitors}
    require(len(ids) == len(competitors), 'duplicate competitor IDs')
    source_ids = {s['id'] for s in sources}
    require(len(source_ids) == len(sources), 'duplicate source IDs')
    for source in sources:
        url = urlsplit(source['url'])
        require(url.scheme in ('http', 'https') and url.netloc, 'market integrity check failed')
        require(not url.username and (not url.password), 'credentials in source URL')
        require(source['access_date'] and source['access_status'], 'market integrity check failed')
    for competitor in competitors:
        require(set(competitor['source_ids']) <= source_ids, 'market integrity check failed')
        require(competitor['last_verification'] and competitor['limitations'], 'market integrity check failed')
    capability_tests = matrix.get('capability_tests')
    require(isinstance(capability_tests, dict), 'capability_tests must be an object')
    require(set(capability_tests) == set(matrix['definitions']),
            'capability tests must cover exactly the feature definitions')
    for feature, test in capability_tests.items():
        require(isinstance(test, dict), f'{feature}: capability test must be an object')
        for field in ('scenario', 'pass_observable', 'failure_policy'):
            value = test.get(field)
            require(isinstance(value, str) and value.strip(),
                    f'{feature}: capability test requires nonempty {field}')
        conditions = test.get('required_conditions')
        require(isinstance(conditions, list) and conditions and
                all(isinstance(value, str) and value.strip() for value in conditions),
                f'{feature}: capability test requires nonempty required_conditions')
    pairs = set()
    for cell in matrix['cells']:
        pair = (cell['product_id'], cell['feature'])
        require(pair not in pairs, f'duplicate feature cell {pair}')
        pairs.add(pair)
        require(pair[0] in ids and pair[1] in matrix['definitions'], 'market integrity check failed')
        require(cell['status'] in matrix['status_semantics'], 'market integrity check failed')
        require(set(cell['evidence_ids']) <= source_ids, 'market integrity check failed')
        if cell['status'] != 'Unknown':
            require(cell['evidence_ids'], 'market integrity check failed')
            for field in ('basis', 'verification_method', 'evidence_grade', 'evidence_url',
                          'access_date', 'confidence', 'limitations', 'audit_scope'):
                value = cell.get(field)
                require(isinstance(value, str) and value.strip(),
                        f'{pair}: supported cell requires nonempty {field}')
            try:
                claim_url = urlsplit(cell['evidence_url'])
                # urlsplit defers malformed/out-of-range port checks to this property.
                _ = claim_url.port
                valid_url = (claim_url.scheme in ('http', 'https') and claim_url.hostname and
                             claim_url.username is None and claim_url.password is None and
                             not any(character.isspace() for character in cell['evidence_url']))
            except ValueError as error:
                raise MarketValidationError(f'{pair}: invalid evidence_url') from error
            require(valid_url, f'{pair}: evidence_url requires credential-free HTTP(S)')
            try:
                access_date = date.fromisoformat(cell['access_date'])
            except ValueError as error:
                raise MarketValidationError(f'{pair}: invalid access_date') from error
            require(access_date.isoformat() == cell['access_date'],
                    f'{pair}: access_date must use YYYY-MM-DD')
    require(len(pairs) == len(ids) * len(matrix['definitions']), 'incomplete matrix')
    numbers = {item['number'] for item in backlog}
    require(len(numbers) == len(backlog), 'duplicate backlog issue')
    parents = {}
    for item in backlog:
        for key in ('question', 'owner', 'workstream', 'priority', 'readiness', 'status',
                    'deliverable', 'steps', 'priority_rationale', 'next_action'):
            require(item.get(key), (item['number'], key))
        require((BASE / item['deliverable']).exists(), item['deliverable'])
        scores = item['scores']
        require(len(scores) == 6 and all((v is None or 1 <= v <= 5 for v in scores)), 'market integrity check failed')
        expected = None if None in scores else round(sum(a*b for a,b in zip(scores, (.25,.20,.20,.15,.1,.1))), 2)
        require(item['score'] == expected, 'incorrect priority arithmetic')
        if item.get('parent_number'):
            require(item['parent_number'] in numbers, 'market integrity check failed')
            parents[item['number']] = item['parent_number']
        if item['status'] == 'Done':
            completion = item.get('completion_evidence', {})
            require(all((completion.get(k) for k in ('accepted_commit', 'review_url', 'handoff_acceptance'))), 'Done requires recorded acceptance evidence')
    for start in parents:
        seen = set()
        current = start
        while current in parents:
            require(current not in seen, 'cyclic parent links')
            seen.add(current)
            current = parents[current]
    print(f'Market integrity OK: {len(ids)} entities, {len(pairs)} cells, {len(backlog)} issues')


if __name__ == '__main__':
    validate()
