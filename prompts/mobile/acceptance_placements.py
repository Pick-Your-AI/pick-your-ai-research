"""Check the finite accepted placement register without fetching external evidence.

The pinned GitHub receipts require independent source review. This reader checks
their declared identities, the exact permitted destinations and preserved local
snapshot; it cannot authenticate a remote review, merge or artifact hash.
"""
import hashlib
import json
import math
from pathlib import Path
import re

ANDROID = 'Pick-Your-AI/pick-your-ai-android'
WEBSITE = 'Pick-Your-AI/pickyour.ai'
BASE = f'https://github.com/{ANDROID}'
DIRECTORY = 'docs/delivery/android/work-packages/'
# All 258 captured issue records at research 79960b7, before the destination-only
# amendments. Canonical JSON uses sorted keys, compact separators and UTF-8.
HISTORICAL_ISSUES_SHA256 = '259d9240b7c74b86397591eb12696a5a757768f4d991cbc87e287cd39756f478'

# Expanding a placement requires a separately reviewed source change here and in
# the register. An arbitrary well-formed PR, commit or issue is not an exception.
# Values: decision issue, delivering PR, receiving review, merge, tree, ADR, paths.
SUPPORTED = {
    'android-adr-0001': (
        34, 279, 5562386507,
        'e86e8bd7645234e12b9887f1e6a0148a2d52073e',
        'e58ad5606da914885010b9d467a02402b3c8a1d3',
        'docs/decisions/0001-android-23-acceptance-record.md', {23: '14.01.md'}),
    'android-adr-0002': (
        34, 297, 5562661670,
        '93bebf787a091fe4858c1c70fd07cabefe17170f',
        '4ae6ba843c8e0cf8c68382a5176ed3c18b189a58',
        'docs/decisions/0002-android-foundation-records.md',
        {20: '01.01.md', 24: '01.02.md', 34: '01.03.md'}),
    'android-adr-0003': (
        25, 322, 5563048963,
        '68e52dd9c79cefe97af65e8fd1e86e4b72d2c42c',
        'ae9393a72f914377f5b1fde7f49b4a37ad4d2244',
        'docs/decisions/0003-android-25-acceptance-record.md', {25: '01.05.md'}),
    'android-adr-0004': (
        47, 318, 5563081505,
        'b6935a8ee7843831f90b0219c8794071557c71d4',
        'f76db41ebebad4570952dcb2ff83c9ba6ef04955',
        'docs/decisions/0004-android-47-acceptance-record.md', {47: '01.06.md'}),
    'android-adr-0005': (
        35, 347, 5563464371,
        '4c753bd69f3857d9b15051be86078948e61074ac',
        '617417c922bde926d052d9c2b4ba3920d0377751',
        'docs/decisions/0005-android-35-acceptance-record.md', {35: '01.04.md'}),
}


def require(condition, message):
    if not condition:
        raise ValueError(f'Acceptance placements: {message}')


def _object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key {key!r}')
        result[key] = value
    return result


def _constant(token):
    raise ValueError(f'Acceptance placements: non-finite JSON number {token}')


def _float(token):
    value = float(token)
    require(math.isfinite(value), 'numeric overflow')
    return value


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=_object, parse_constant=_constant,
                      parse_float=_float)


def _shape(value, keys, context):
    require(type(value) is dict and set(value) == set(keys.split()),
            f'{context}: unexpected or missing fields')


def _hex(value, length, context):
    require(type(value) is str and
            re.fullmatch(r'[0-9a-f]{' + str(length) + '}', value) is not None,
            f'{context}: expected lowercase {length}-digit digest')


def _artifact(value, path, commit, context):
    _shape(value, 'path url sha256', context)
    require(value['path'] == path, f'{context}: wrong path')
    require(value['url'] == f'{BASE}/blob/{commit}/{path}',
            f'{context}: URL must identify the exact accepted commit and path')
    _hex(value['sha256'], 64, context)


def validate_placements(register, records, index):
    """Validate all accepted amendments and return their number of issue records."""
    _shape(register, 'schema_version source_snapshot amendments', 'register')
    require(type(register['schema_version']) is int and
            register['schema_version'] == 1, 'unsupported register version')
    snapshot = register['source_snapshot']
    _shape(snapshot, 'repository commit tree ledger_path ledger_sha256 ledger_schema_version',
           'source snapshot')
    require(snapshot['repository'] == ANDROID and
            snapshot['ledger_path'] == 'docs/delivery/criterion-evidence.json',
            'wrong source ledger')
    require(type(snapshot['ledger_schema_version']) is int and
            snapshot['ledger_schema_version'] == 6, 'unsupported source ledger version')
    _hex(snapshot['commit'], 40, 'snapshot commit')
    _hex(snapshot['tree'], 40, 'snapshot tree')
    _hex(snapshot['ledger_sha256'], 64, 'snapshot ledger')

    amendments = register['amendments']
    require(type(amendments) is list, 'amendments must be a list')
    seen, placements = set(), {}
    for amendment in amendments:
        _shape(amendment, 'id decision_issue source_repository accepted_commit accepted_tree '
               'pull_request review_url decision_record placements', 'amendment')
        identity = amendment['id']
        require(type(identity) is str and identity in SUPPORTED,
                'unsupported amendment')
        require(identity not in seen, 'duplicate amendment')
        seen.add(identity)
        decision, pr, review, commit, tree, adr_path, paths = SUPPORTED[identity]
        require(amendment['decision_issue'] == f'{ANDROID}#{decision}',
                'wrong placement decision issue')
        require(amendment['source_repository'] == ANDROID, 'wrong source repository')
        require(type(amendment['pull_request']) is int and
                amendment['pull_request'] == pr, 'wrong delivering PR')
        require(amendment['accepted_commit'] == commit and
                amendment['accepted_tree'] == tree, 'wrong accepted Git identity')
        require(amendment['review_url'] == f'{BASE}/pull/{pr}#pullrequestreview-{review}',
                'wrong receiving review')
        _artifact(amendment['decision_record'], adr_path, commit, 'ADR')
        require(type(amendment['placements']) is list, 'placements must be a list')
        expected = {f'{ANDROID}#{number}': DIRECTORY + name
                    for number, name in paths.items()}
        found = set()
        for placement in amendment['placements']:
            _shape(placement, 'issue previous_repository previous_boundary_sha256 '
                   'repository path url sha256', 'placement')
            issue = placement['issue']
            require(type(issue) is str and issue in expected,
                    'issue is outside this ADR scope')
            require(issue not in found and issue not in placements,
                    'duplicate or overlapping placement')
            found.add(issue)
            require(placement['previous_repository'] == WEBSITE and
                    placement['repository'] == ANDROID, 'wrong placement repositories')
            _artifact({k: placement[k] for k in ('path', 'url', 'sha256')},
                      expected[issue], commit, 'receiving record')
            _hex(placement['previous_boundary_sha256'], 64, 'historical boundary')
            placements[issue] = (identity, placement)
        require(found == set(expected), 'missing ADR receiving record')
    require(seen == set(SUPPORTED), 'missing accepted amendment')

    require(type(records) is list and type(index) is str, 'invalid coverage/index')
    found, historical = set(), []
    for record in records:
        require(type(record) is dict, 'invalid coverage record')
        number = record.get('number')
        require(type(number) is int and number > 0, 'coverage issue must be an integer')
        issue = record.get('issue')
        require(type(issue) is str and issue == f"{record.get('repository')}#{number}",
                'coverage issue identity mismatch')
        require(issue not in found, 'duplicate coverage issue')
        found.add(issue)
        original = dict(record)
        path = record.get('acceptance_path')
        if issue in placements:
            identity, placement = placements[issue]
            require(record.get('platform') == 'android', 'wrong placement platform')
            require(record.get('acceptance_placement_amendment') == identity,
                    'missing or incorrect coverage amendment')
            require(record.get('acceptance_repository') == ANDROID and
                    path == placement['path'] and record.get('acceptance_output') == path,
                    'coverage destination mismatch')
            boundary = record.get('delivery_review_boundary')
            require(type(boundary) is str and
                    hashlib.sha256(boundary.encode()).hexdigest() ==
                    placement['previous_boundary_sha256'], 'historical boundary changed')
            require(f'`{WEBSITE}`' in boundary and f'`{path}`' in boundary,
                    'historical website coordinate missing')
            original['acceptance_repository'] = WEBSITE
            del original['acceptance_placement_amendment']
            cell = f'[`{path}`]({placement["url"]}) in `{ANDROID}`'
        else:
            require('acceptance_placement_amendment' not in record,
                    'unregistered coverage amendment')
            if path:
                require(record.get('acceptance_repository') == WEBSITE,
                        'unregistered repository relocation')
                cell = f'`{path}`'
            else:
                require(record.get('platform') == 'apple' and
                        record.get('acceptance_repository') is None,
                        'an empty path cannot authorize a relocation')
                cell = None
        if cell is not None:
            anchor = f'id="issue-{record.get("platform")}-{number}"'
            rows = [line for line in index.splitlines() if anchor in line]
            require(len(rows) == 1 and rows[0].count(anchor) == 1,
                    'missing or duplicate index row')
            cells = rows[0].split('|')
            require(len(cells) == 6 and cells[3].strip() == cell,
                    'index destination must match its exact registered or historical path')
        historical.append(original)
    require(set(placements) <= found, 'missing registered coverage record')
    digest = hashlib.sha256(json.dumps(historical, sort_keys=True, ensure_ascii=False,
                                      separators=(',', ':')).encode()).hexdigest()
    require(digest == HISTORICAL_ISSUES_SHA256,
            'captured issue fields or ordering changed beyond the accepted placements')
    return len(placements)
