"""Check snapshot consistency and scoped handoff attribution, never evidence acceptance."""
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TIMESTAMP = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}'
    r'(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])')


class HandoffValidationError(ValueError):
    """A handoff audit consistency check failed."""


def require(condition, message):
    if not condition:
        raise HandoffValidationError(message)


def audit_instant(value, label):
    """Read an explicit, calendar-valid instant without losing precision.

    The audit profile uses ASCII dates and at most microsecond precision.
    Original timestamp strings remain untouched in the evidence records.
    """
    require(type(value) is str and TIMESTAMP.fullmatch(value) is not None,
            f'{label}: invalid timezone-aware audit timestamp')
    try:
        return datetime.fromisoformat(value).astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        raise HandoffValidationError(
            f'{label}: invalid timezone-aware audit timestamp') from error


def read_json(path):
    """Reject ambiguous object keys and non-finite numbers before audit indexing."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result,
                    f'{path.name}: duplicate JSON object key: {key!r}')
            result[key] = value
        return result

    def reject_constant(value):
        raise HandoffValidationError(f'{path.name}: non-finite JSON number: {value}')

    def finite_float(value):
        number = float(value)
        require(math.isfinite(number),
                f'{path.name}: JSON number exceeds finite numeric range')
        return number

    return json.loads(path.read_text(encoding='utf-8'),
                      object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def response_status(row):
    if row.get('owner_review') or any(
            response['role'] == 'receiving_owner'
            for response in row.get('responses', [])):
        return 'scoped_response_recorded'
    return 'author_integration_only' if row.get('responses') else 'not_yet_confirmed'


def validate_identity_numbers(ledger, readback, audit):
    """Check identity types before Python's bool/float equality can join them."""
    def number(value, label):
        require(type(value) is int and value > 0,
                f'{label}: expected a positive integer issue/PR number')

    for issue in readback['issues']:
        number(issue['number'], 'snapshot issue')
        if issue['parent'] is not None:
            number(issue['parent']['number'], 'native parent')
        for relationship in ('sub_issues', 'blocked_by'):
            for value in issue.get(relationship, []):
                number(value, relationship)
    for label, rows in (
            ('handoff', ledger),
            ('historical review', readback['historical_owner_reviews']),
            ('scoped response', readback['new_scoped_responses'])):
        for row in rows:
            number(row['market_issue'], label + ' producer')
            number(row['consumer_issue'], label + ' consumer')
    for pair in readback['declared_handoff_pairs']:
        for value in pair:
            number(value, 'declared handoff')
    for pr in readback['pull_requests']:
        number(pr['number'], 'snapshot pull request')
    for issue in audit['issues']:
        number(issue['number'], 'classified issue')
        for value in issue['related_prs']:
            number(value, 'related pull request')


def validate_response_text(response, label):
    """Require recorded text without normalizing it or certifying its truth."""
    for field in ('reviewer', 'url', 'scope', 'retained_unknowns_and_next_action',
                  'submitted_at', 'commit_basis'):
        value = response.get(field)
        require(isinstance(value, str) and value.strip(),
                f'{label}: {field} must be nonempty text')


def validate(ledger, readback, audit):
    validate_identity_numbers(ledger, readback, audit)
    for row in ledger:
        for response in row.get('responses', []):
            validate_response_text(response, 'ledger response')
    for response in readback['new_scoped_responses']:
        validate_response_text(response, 'readback response')
    cutoff = audit_instant(readback['snapshot_cutoff_utc'], 'readback cutoff')
    audit_instant(audit['snapshot_cutoff_utc'], 'audit cutoff')
    issues = {issue['number']: issue for issue in readback['issues']}
    require(len(issues) == len(readback['issues']), 'duplicate snapshot issue')
    classified_numbers = [issue['number'] for issue in audit['issues']]
    classified = set(classified_numbers)
    require(len(classified) == len(classified_numbers), 'duplicate classified issue')
    require(classified <= issues.keys(),
            'technical classification references an uncaptured issue')
    pairs = {(row['market_issue'], row['consumer_issue']) for row in ledger}
    require(len(pairs) == len(ledger), 'duplicate handoff pair')
    declared = set(map(tuple, readback['declared_handoff_pairs']))
    require(len(declared) == len(readback['declared_handoff_pairs']),
            'duplicate declared handoff pair')
    require(declared <= pairs, 'missing declared handoff')
    require(audit['snapshot_cutoff_utc'] == readback['snapshot_cutoff_utc'],
            'audit and readback cutoff differ')
    require(audit['base_commit'] == readback['base_commit'],
            'audit and readback base commit differ')
    for row in readback['historical_owner_reviews']:
        pair = (row['market_issue'], row['consumer_issue'])
        submitted = audit_instant(row['owner_review'].get('submitted_at'),
                                  f'{pair}: historical receipt')
        require(submitted <= cutoff, f'{pair}: post-cutoff receipt')
    historical = {(r['market_issue'], r['consumer_issue']): r['owner_review']
                  for r in readback['historical_owner_reviews']}
    require(len(historical) == len(readback['historical_owner_reviews']),
            'duplicate historical review pair')
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
            require(not {'market_issue', 'consumer_issue'} & response.keys(),
                    f'{pair}: response contains reserved pair keys')
            require(response['role'] in ('receiving_owner', 'author_integration'),
                    f'{pair}: unknown response role')
            if response['role'] == 'receiving_owner':
                require(response['reviewer'] in row['consumer_owner'],
                        f'{pair}: response is not from a receiving assignee')
            submitted = audit_instant(response.get('submitted_at'),
                                      f'{pair}: scoped receipt')
            require(submitted <= cutoff, f'{pair}: post-cutoff receipt')
            require('reviewed_commit' in response,
                    f'{pair}: reviewed SHA must be explicit or explicitly unknown')
            actual_responses.append({**response, 'market_issue': pair[0],
                                     'consumer_issue': pair[1]})
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
    for number, issue in issues.items():
        parent = issue['parent']
        require(parent is None or (parent['number'] in issues and
                number in issues[parent['number']]['sub_issues']),
                'native parent/sub-issue mismatch')
        require(all(child in issues and issues[child]['parent'] is not None and
                    issues[child]['parent']['number'] == number
                    for child in issue['sub_issues']),
                'native parent/sub-issue mismatch')
    captured_prs = {pr['number'] for pr in readback['pull_requests']}
    require(len(captured_prs) == len(readback['pull_requests']),
            'duplicate snapshot pull request')
    require(all(n in captured_prs for row in audit['issues'] for n in row['related_prs']),
            'technical classification references an uncaptured PR')
    return coverage


def main():
    base = ROOT / 'research' / 'market'
    load = lambda name: read_json(base / name)
    coverage = validate(load('handoffs.json'), load('handoff-audit-readback.json'),
                        load('audit.json'))
    print(f'Handoff audit integrity OK: {coverage["total_rows"]} rows; '
          f'{coverage["declared_pairs"]} declared pairs; human acceptance not certified')


if __name__ == '__main__':
    main()
