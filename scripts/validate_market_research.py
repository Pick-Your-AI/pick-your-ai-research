"""Check market-note integrity, not truth, rights, benchmark quality or acceptance."""
import json
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
    return json.loads((BASE / name).read_text(encoding='utf-8'))


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
    pairs = set()
    for cell in matrix['cells']:
        pair = (cell['product_id'], cell['feature'])
        require(pair not in pairs, f'duplicate feature cell {pair}')
        pairs.add(pair)
        require(pair[0] in ids and pair[1] in matrix['definitions'], 'market integrity check failed')
        require(cell['status'] in matrix['status_semantics'], 'market integrity check failed')
        require(set(cell['evidence_ids']) <= source_ids, 'market integrity check failed')
        if cell['status'] != 'Unknown':
            require(cell['evidence_ids'] and cell['basis'] and cell['verification_method'], 'market integrity check failed')
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
