"""Check market-note integrity, not truth, rights, benchmark quality or acceptance."""
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research' / 'market'


def read(name):
    return json.loads((BASE / name).read_text(encoding='utf-8'))


def validate():
    competitors, sources, matrix, backlog = (read(n) for n in
        ('competitors.json', 'sources.json', 'features.json', 'research-backlog.json'))
    ids = {c['id'] for c in competitors}
    assert len(ids) == len(competitors), 'duplicate competitor IDs'
    source_ids = {s['id'] for s in sources}
    assert len(source_ids) == len(sources), 'duplicate source IDs'
    for source in sources:
        url = urlsplit(source['url'])
        assert url.scheme in ('http', 'https') and url.netloc
        assert not url.username and not url.password, 'credentials in source URL'
        assert source['access_date'] and source['access_status']
    for competitor in competitors:
        assert set(competitor['source_ids']) <= source_ids
        assert competitor['last_verification'] and competitor['limitations']
    pairs = set()
    for cell in matrix['cells']:
        pair = (cell['product_id'], cell['feature'])
        assert pair not in pairs, f'duplicate feature cell {pair}'
        pairs.add(pair)
        assert pair[0] in ids and pair[1] in matrix['definitions']
        assert cell['status'] in matrix['status_semantics']
        assert set(cell['evidence_ids']) <= source_ids
        if cell['status'] != 'Unknown':
            assert cell['evidence_ids'] and cell['basis'] and cell['verification_method']
    assert len(pairs) == len(ids) * len(matrix['definitions']), 'incomplete matrix'
    numbers = {item['number'] for item in backlog}
    assert len(numbers) == len(backlog), 'duplicate backlog issue'
    parents = {}
    for item in backlog:
        for key in ('question', 'owner', 'workstream', 'priority', 'readiness', 'status',
                    'deliverable', 'steps', 'priority_rationale', 'next_action'):
            assert item.get(key), (item['number'], key)
        assert (BASE / item['deliverable']).exists(), item['deliverable']
        scores = item['scores']
        assert len(scores) == 6 and all(v is None or 1 <= v <= 5 for v in scores)
        expected = None if None in scores else round(sum(a*b for a,b in zip(scores, (.25,.20,.20,.15,.1,.1))), 2)
        assert item['score'] == expected, 'incorrect priority arithmetic'
        if item.get('parent_number'):
            assert item['parent_number'] in numbers
            parents[item['number']] = item['parent_number']
        assert item['status'] != 'Done', 'initial draft must not claim acceptance'
    for start in parents:
        seen = set()
        current = start
        while current in parents:
            assert current not in seen, 'cyclic parent links'
            seen.add(current)
            current = parents[current]
    print(f'Market integrity OK: {len(ids)} entities, {len(pairs)} cells, {len(backlog)} issues')


if __name__ == '__main__':
    validate()
