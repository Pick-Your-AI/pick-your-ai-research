#!/usr/bin/env python3
"""Validate a closed, local T1 identity assessment; never retrieve sources."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
T1 = 'research/T1-model-selection/'
DIRECTORY = T1 + 'identity-crosswalk/'
NOTES = tuple(T1 + name + '-models.md' for name in (
    'language', 'perception', 'retrieval', 'generative-media', 'audio', 'specialized'))
INPUTS = (T1 + 'model-research-inventory.json', T1 + 'model-research-sources.json', *NOTES)
SHA = re.compile(r'[a-f0-9]{64}')
HF = re.compile(r'https://huggingface.co/([^/]+/[^/]+)/blob/([a-f0-9]{40})/([^?#]+)')
TYPE_ASSESSMENT = {
    'model_bundle': 'bundle_requires_constituents',
    'model_pipeline': 'pipeline_requires_constituents',
    'architecture_recipe': 'recipe_requires_trained_artifact',
    'model_family_unpinned': 'family_requires_selection',
    'model_service_unpinned': 'service_requires_release_binding',
    'ui_model_family': 'ui_family_requires_selection',
    'artifact_family_unpinned': 'artifact_family_requires_selection',
}
ROW_KEYS = {'row_index', 'row_sha256', 'candidate', 'recorded_type', 'source_ids',
            'note_refs', 'verification', 'assessment', 'identity_refs',
            'known_unknowns', 'next_action'}
FOLLOW_UP = {
    'candidate_requires_identity_review': ('identity_unresolved', 'review_identity'),
    'recorded_repository_locator': ('checkpoint_unresolved', 'select_checkpoint'),
    'recorded_api_selector': ('offering_unresolved', 'bind_offering'),
    'recorded_snapshot_name': ('snapshot_route_unresolved', 'bind_snapshot'),
    'bundle_requires_constituents': ('composition_unresolved', 'resolve_constituents'),
    'pipeline_requires_constituents': ('composition_unresolved', 'resolve_constituents'),
    'recipe_requires_trained_artifact': ('trained_artifact_unresolved', 'select_fitted_artifact'),
    'family_requires_selection': ('family_unresolved', 'select_family_member'),
    'service_requires_release_binding': ('service_release_unresolved', 'bind_service_release'),
    'ui_family_requires_selection': ('ui_identity_unresolved', 'select_ui_identity'),
    'artifact_family_requires_selection': ('checkpoint_unresolved', 'select_checkpoint'),
}


class InvalidCrosswalk(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidCrosswalk(message)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def constant(_):
        raise InvalidCrosswalk('non-finite JSON number')
    def finite(token):
        value = float(token)
        require(math.isfinite(value), 'non-finite JSON number')
        return value
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def record_digest(record):
    return digest(json.dumps(record, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode('utf-8'))


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return (isinstance(value, list) and bool(value) and all(text(v) for v in value)
            and len(set(value)) == len(value))


def repository_refs(record, sources):
    result = []
    for sid in record['source_ids']:
        for index, url in enumerate(sources[sid]['urls']):
            match = HF.fullmatch(url)
            if match and match[1] == record['model']:
                result.append({'state': 'recorded_repository_locator', 'source_id': sid,
                               'url_index': index, 'repository': match[1],
                               'document_revision': match[2], 'document_path': match[3]})
    return result


def assessment(record, locators):
    if record['artifact_type'] != 'model':
        return TYPE_ASSESSMENT.get(record['artifact_type'])
    if record['source_ids'] in (['B16'], ['B32']):
        return 'recorded_api_selector'
    if record['source_ids'] == ['R26']:
        return 'recorded_snapshot_name'
    return 'recorded_repository_locator' if locators else 'candidate_requires_identity_review'


def validate(root=ROOT):
    root = Path(root)
    manifest = strict_json((root / DIRECTORY / 'manifest.json').read_text(encoding='utf-8'))
    require(isinstance(manifest, dict) and set(manifest) == {
        'format', 'status', 'basis_commit', 'assessed_on', 'scope', 'row_count', 'inputs'},
        'manifest keys differ from version 1')
    require(manifest['format'] == 't1-identity-crosswalk-v1', 'unsupported format')
    require(manifest['status'] == 'partial-research-not-catalog', 'research status changed')
    require(manifest['basis_commit'] == 'd58106750bb76f72c270653993edf808f29c49bb',
            'different cohort baseline requires a reviewed successor')
    require(manifest['assessed_on'] == '2026-11-19' and text(manifest['scope']),
            'version 1 assessment metadata changed')
    require(type(manifest['row_count']) is int and manifest['row_count'] == 248,
            'version 1 cohort must retain all 248 rows')
    require(isinstance(manifest['inputs'], dict) and set(manifest['inputs']) == set(INPUTS),
            'manifest must bind exactly the eight declared inputs')
    documents = {}
    for relative in INPUTS:
        expected = manifest['inputs'][relative]
        require(isinstance(expected, str) and SHA.fullmatch(expected), 'invalid input hash')
        path = root / relative
        require(not any(parent.is_symlink() for parent in (path, *path.parents)),
                'input symlinks are not accepted')
        raw = path.read_bytes()
        require(digest(raw) == expected, 'input bytes changed: ' + relative)
        documents[relative] = raw.decode('utf-8')
    inventory = strict_json(documents[INPUTS[0]])['records']
    source_rows = strict_json(documents[INPUTS[1]])['sources']
    sources = {row['id']: row for row in source_rows}
    require(len(sources) == len(source_rows), 'source identifiers are not unique')
    raw_rows = (root / DIRECTORY / 'rows.jsonl').read_text(encoding='utf-8')
    require(raw_rows.endswith('\n'), 'JSONL must end with a newline')
    rows = [strict_json(line) for line in raw_rows.splitlines()]
    require(len(rows) == len(inventory) == manifest['row_count'], 'cohort row count differs')
    seen = set()
    for index, (row, record) in enumerate(zip(rows, inventory)):
        label = 'row ' + str(index)
        keys = ROW_KEYS | ({'disposition_note'} if record['artifact_type'] != 'model' else set())
        require(isinstance(row, dict) and set(row) == keys, label + ': invalid keys')
        require(type(row['row_index']) is int and row['row_index'] == index,
                label + ': row identity/order differs')
        require(row['row_sha256'] == record_digest(record), label + ': record hash differs')
        require(row['row_sha256'] not in seen, label + ': duplicate record')
        seen.add(row['row_sha256'])
        require(row['candidate'] == record['model'] and row['recorded_type'] == record['artifact_type']
                and row['source_ids'] == record['source_ids'], label + ': inventory binding differs')
        require(all(sid in sources for sid in row['source_ids']), label + ': unresolved source')
        refs = [{'path': path, 'line': number} for path in NOTES
                for number, line in enumerate(documents[path].splitlines(), 1)
                if line.startswith('| ' + record['model'] + ' (')]
        require(refs and row['note_refs'] == refs, label + ': claim-note references differ')
        require(all(type(ref['line']) is int for ref in row['note_refs']),
                label + ': note line must be an integer')
        require(row['verification'] == 'local_derivation_only', label + ': verification upgraded')
        locators = repository_refs(record, sources)
        require(row['assessment'] == assessment(record, locators) and row['assessment'] is not None,
                label + ': unsupported assessment')
        require((row['known_unknowns'], row['next_action']) == FOLLOW_UP[row['assessment']],
                label + ': unresolved fields or next action differ from version 1 vocabulary')
        if 'disposition_note' in row:
            require(text(row['disposition_note']), label + ': specific disposition is required')
        identities = row['identity_refs']
        require(isinstance(identities, list) and all(isinstance(v, dict) for v in identities),
                label + ': identity references must be objects')
        actual_locators = [v for v in identities if v.get('state') == 'recorded_repository_locator']
        require(actual_locators == locators, label + ': source-document locator differs')
        for identity in identities:
            state = identity.get('state')
            if state == 'recorded_repository_locator':
                require(type(identity['url_index']) is int, label + ': URL index must be integer')
            elif state == 'recorded_component_labels':
                require(set(identity) == {'state', 'labels', 'source_ids'}
                        and strings(identity['labels']) and identity['source_ids'] == row['source_ids']
                        and row['recorded_type'] in {'model_bundle', 'model_pipeline'},
                        label + ': invalid component-label reference')
            elif state in {'recorded_api_selector', 'recorded_snapshot_name'}:
                require(set(identity) == {'state', 'value', 'source_ids'}
                        and state == row['assessment'] and identity['value'] == row['candidate']
                        and identity['source_ids'] == row['source_ids'],
                        label + ': invalid recorded selector reference')
            else:
                raise InvalidCrosswalk(label + ': unsupported identity state')
        if row['assessment'] in {'recorded_api_selector', 'recorded_snapshot_name'}:
            require(len(identities) == 1 and identities[0]['state'] == row['assessment'],
                    label + ': missing selector/snapshot reference')
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        count = validate(args.root)
    except (ValueError, OSError, KeyError, TypeError, UnicodeError) as exc:
        print('T1 identity crosswalk invalid: ' + str(exc), file=sys.stderr)
        return 1
    print(f'T1 identity crosswalk: {count} committed candidate rows; local integrity only.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
