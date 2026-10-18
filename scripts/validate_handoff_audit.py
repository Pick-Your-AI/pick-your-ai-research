"""Check snapshot consistency and scoped handoff attribution, never evidence acceptance."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HandoffValidationError(ValueError):
    """A handoff audit consistency check failed."""


def require(condition, message):
    if not condition:
        raise HandoffValidationError(message)


def response_status(row):
    if row.get('owner_review') or any(
            response['role'] == 'receiving_owner'
            for response in row.get('responses', [])):
        return 'scoped_response_recorded'
    return 'author_integration_only' if row.get('responses') else 'not_yet_confirmed'


def validate(ledger, readback, audit):
    issues = {issue['number']: issue for issue in readback['issues']}
    pairs = {(row['market_issue'], row['consumer_issue']) for row in ledger}
    require(len(pairs) == len(ledger), 'duplicate handoff pair')
    declared = set(map(tuple, readback['declared_handoff_pairs']))
    require(declared <= pairs, 'missing declared handoff')
    require(audit['snapshot_cutoff_utc'] == readback['snapshot_cutoff_utc'],
            'audit and readback cutoff differ')
    require(audit['base_commit'] == readback['base_commit'],
            'audit and readback base commit differ')
    historical = {(r['market_issue'], r['consumer_issue']): r['owner_review']
                  for r in readback['historical_owner_reviews']}
    observed_history = {(r['market_issue'], r['consumer_issue']): r['owner_review']
                        for r in ledger if 'owner_review' in r}
    require(observed_history == historical, 'historical review changed or dropped')
    actual_responses = []
    for row in ledger:
        pair = (row['market_issue'], row['consumer_issue'])
        require(set(pair) <= issues.keys(), 'handoff issue absent from snapshot')
        require(set(row['consumer_owner']) == set(issues[pair[1]]['assignees']),
                f'{pair}: receiving assignees differ from snapshot')
        require(row['receiving_review_status'] == response_status(row),
                f'{pair}: author-only or absent response promoted to receiving review')
        for response in row.get('responses', []):
            require(response['role'] in ('receiving_owner', 'author_integration'),
                    f'{pair}: unknown response role')
            if response['role'] == 'receiving_owner':
                require(response['reviewer'] in row['consumer_owner'],
                        f'{pair}: response is not from a receiving assignee')
            require(response['url'] and response['scope'] and
                    response['retained_unknowns_and_next_action'] and
                    response['submitted_at'] <= readback['snapshot_cutoff_utc'],
                    f'{pair}: incomplete or post-cutoff receipt')
            require('reviewed_commit' in response and response['commit_basis'],
                    f'{pair}: reviewed SHA must be explicit or explicitly unknown')
            actual_responses.append({'market_issue': pair[0], 'consumer_issue': pair[1],
                                     **response})
    key = lambda r: (r['market_issue'], r['consumer_issue'], r['url'])
    require(sorted(actual_responses, key=key) ==
            sorted(readback['new_scoped_responses'], key=key),
            'receipt moved, changed or dropped from its recorded producer/consumer scope')
    coverage = readback['handoff_coverage']
    require(audit['handoff_coverage'] == coverage, 'audit coverage differs')
    require(coverage['total_rows'] == len(ledger), 'incorrect handoff row total')
    require(coverage['declared_pairs'] == len(declared), 'incorrect declared pair total')
    require(coverage['historical_owner_review_rows'] == len(historical),
            'incorrect historical receipt count')
    require(coverage['new_response_records'] == len(actual_responses),
            'incorrect new response count')
    require(coverage['receiving_review_status_counts'] ==
            dict(Counter(response_status(row) for row in ledger)),
            'incorrect response coverage counts')
    pending = sum(row['market_issue'] == 59 and
                  row.get('current_audit_acceptance', '').startswith('Pending')
                  for row in ledger)
    require(coverage['current_audit_acceptance_pending'] == pending,
            'context response incorrectly counted as current audit acceptance')
    require(all(issues[n]['parent'] is None or
                n in issues[issues[n]['parent']['number']]['sub_issues']
                for n in issues), 'native parent/sub-issue mismatch')
    captured_prs = {pr['number'] for pr in readback['pull_requests']}
    require(all(n in captured_prs for row in audit['issues'] for n in row['related_prs']),
            'technical classification references an uncaptured PR')
    return coverage


def main():
    base = ROOT / 'research' / 'market'
    load = lambda name: json.loads((base / name).read_text(encoding='utf-8'))
    coverage = validate(load('handoffs.json'), load('handoff-audit-readback.json'),
                        load('audit.json'))
    print(f'Handoff audit integrity OK: {coverage["total_rows"]} rows; '
          f'{coverage["declared_pairs"]} declared pairs; human acceptance not certified')


if __name__ == '__main__':
    main()
