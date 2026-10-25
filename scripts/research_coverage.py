"""Reproduce bounded repository coverage counts, not evidence acceptance."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from validate_research import intake_json

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ('Exercised', 'Documented', 'Unsupported', 'Unknown')


def snapshot(root):
    inputs = {}

    def read(path):
        raw = (root / path).read_bytes()
        inputs[path] = hashlib.sha256(raw).hexdigest()
        return intake_json(raw.decode('utf-8'))

    kinds = read('contracts/v1/schemas/component-registry.json')['kinds']
    counts = dict.fromkeys(kinds, 0)
    for path in sorted((root / 'catalog/proposals').rglob('*.json')):
        item = read(path.relative_to(root).as_posix())
        if item['kind'] not in counts:
            raise ValueError(f'{path.name}: unknown catalog kind')
        counts[item['kind']] += 1

    pricebooks = rates = 0
    for path in sorted((root / 'pricing/proposals').rglob('*.json')):
        book = read(path.relative_to(root).as_posix())
        if not isinstance(book['rates'], list):
            raise ValueError(f'{path.name}: rates must be an array')
        pricebooks += 1
        rates += len(book['rates'])

    competitors = read('research/market/competitors.json')
    product_ids = [item['id'] for item in competitors]
    if len(set(product_ids)) != len(product_ids):
        raise ValueError('duplicate market product ID')
    features = read('research/market/features.json')
    feature_ids = features['definitions']
    expected = {(product, feature) for product in product_ids for feature in feature_ids}
    observed = set()
    totals = Counter(dict.fromkeys(STATUSES, 0))
    for cell in features['cells']:
        pair = (cell['product_id'], cell['feature'])
        if pair not in expected or pair in observed:
            raise ValueError(f'unknown or duplicate market cell: {pair}')
        status = cell['status']
        if status not in STATUSES:
            raise ValueError(f'unknown market status: {status!r}')
        observed.add(pair)
        totals[status] += 1
    if observed != expected:
        raise ValueError('missing market cells; coverage denominator is incomplete')

    return {
        'format': 'research-coverage-snapshot-v1',
        'scope': 'Local proposal files and recorded market cells only; not all AI resources.',
        'catalog': {
            'canonical_kind_count': len(kinds),
            'proposal_count': sum(counts.values()),
            'kinds_with_proposals': sum(value > 0 for value in counts.values()),
            'proposals_by_kind': counts,
        },
        'pricing': {'pricebook_count': pricebooks, 'rate_count': rates},
        'market': {
            'product_count': len(product_ids),
            'feature_count': len(feature_ids),
            'cell_count': len(observed),
            'cells_by_status': dict(totals),
        },
        'unmeasured': [
            'Global ecosystem denominator and deduplicated entity coverage',
            'Claim accuracy, independent measurements and current source freshness',
            'Receiving-owner review, per-use publication eligibility and website delivery',
        ],
        'input_sha256': dict(sorted(inputs.items())),
    }


def render(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', type=Path, help='fail if this snapshot differs from current inputs')
    args = parser.parse_args(argv)
    try:
        output = render(snapshot(ROOT))
        if args.check:
            if args.check.read_text(encoding='utf-8') != output:
                raise ValueError('coverage snapshot differs; regenerate and review input changes')
            print('Coverage snapshot matches local inputs; evidence acceptance is unmeasured.')
        else:
            print(output, end='')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'Coverage error: {exc}\n')


if __name__ == '__main__':
    main()
