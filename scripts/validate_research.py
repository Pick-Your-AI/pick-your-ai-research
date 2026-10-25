"""Validate research intake; does not certify claims or publish runtime artifacts."""
import json
import math
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlsplit

import idna
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'contracts/v1'
SCHEMAS = {p.name: json.loads(p.read_text(encoding='utf-8')) for p in (CONTRACT / 'schemas').glob('*.schema.json')}
REGISTRY = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in SCHEMAS.values())
KINDS = json.loads((CONTRACT / 'schemas/component-registry.json').read_text(encoding='utf-8'))['kinds']
REFERENCES = {
    ('model', 'provider_ref'): 'model_provider',
    ('embedding_model', 'provider_ref'): 'model_provider',
    ('compute_profile', 'hosting_ref'): 'hosting_platform',
    ('compute_profile', 'accelerator_ref'): 'accelerator',
    ('hosting_platform', 'accelerator_refs'): 'accelerator',
    ('storage', 'hosting_ref'): 'hosting_platform',
    ('knowledge_base', 'data_source_refs'): 'data_source',
    ('vector_database', 'hosting_ref'): 'hosting_platform',
    ('mcp_server', 'tool_refs'): 'tool',
    ('integration', 'associated_tool_refs'): 'tool',
    ('training_compute', 'compute_profile_ref'): 'compute_profile',
    ('training_compute', 'storage_ref'): 'storage',
    ('training_dataset', 'data_source_refs'): 'data_source',
    ('fine_tuned_model', 'base_model_ref'): 'model',
    ('fine_tuned_model', 'training_framework_ref'): 'training_framework',
    ('fine_tuned_model', 'training_dataset_ref'): 'training_dataset',
    ('evaluation_suite', 'dataset_refs'): 'training_dataset',
    ('deployment_target', 'hosting_ref'): 'hosting_platform',
}


def schema_errors(payload, schema):
    validator = Draft202012Validator(schema, registry=REGISTRY, format_checker=FormatChecker())
    return [f"/{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(payload)]


def intake_json(text, *, exact_numbers=False):
    """Decode unambiguous JSON, optionally preserving proposal numeric values."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON object key: {key!r}')
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f'non-finite JSON number: {value}')

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('JSON number exceeds finite numeric range')
        if not exact_numbers:
            return number
        # Zero has an exact value even when its exponent exceeds Decimal's range.
        mantissa = value.lower().split('e', 1)[0]
        if not any(digit in '123456789' for digit in mantissa):
            return 0
        try:
            exact = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError('JSON number exceeds exact decimal range') from exc
        if not exact.is_finite():
            raise ValueError('JSON number exceeds exact decimal range')
        # Inspect digits rather than rounding through the active Decimal context.
        parts = exact.as_tuple()
        if parts.exponent >= 0 or not any(parts.digits[parts.exponent:]):
            return int(exact)
        return exact

    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def locator_parts(uri):
    """Check original locator syntax without normalizing away malformed input."""
    if not isinstance(uri, str) or not uri or any(
            char.isspace() or ord(char) < 0x20 or ord(char) == 0x7f for char in uri):
        raise ValueError('locator needs nonempty text without whitespace or control characters')
    value = urlsplit(uri)
    # urlsplit defers nonnumeric and out-of-range port validation to this property.
    _ = value.port
    if value.username is not None or value.password is not None:
        raise ValueError('locator must not contain user information')
    return value


def public_source(uri):
    try:
        value = locator_parts(uri)
        host = value.hostname or ''
        if (value.scheme not in {'http', 'https'} or not host
                or value.username is not None or value.password is not None
                or '%' in host or '\\' in host):
            return False
        if value.netloc.startswith('['):
            # IPv6 literals are addresses, not IDNA domain labels.
            address = ip_address(host)
            if address.version != 6:
                return False
        else:
            # The standard-library IDNA2003 codec misses newer compatibility
            # mappings that browsers apply before interpreting a host as an IP.
            host = idna.encode(host, uts46=True, std3_rules=True).decode('ascii').removesuffix('.')
            reserved = host in {'example.com', 'example.org', 'example.net', 'localhost'} or any(
                host.endswith(s) for s in ('.example', '.invalid', '.test', '.localhost', '.example.com', '.example.org', '.example.net'))
            if reserved:
                return False
            try:
                address = ip_address(host)
            except ValueError:
                # Require canonical IP syntax instead of guessing radix/parts.
                return re.fullmatch(r'(?:0[xX][0-9a-fA-F]*|[0-9]+)(?:\.(?:0[xX][0-9a-fA-F]*|[0-9]+))*', host) is None
        address = getattr(address, 'ipv4_mapped', None) or address
        return address.is_global and not (address.is_multicast or address.is_reserved
                                          or getattr(address, 'is_site_local', False))
    except (ValueError, TypeError):
        return False


def price_instant(value):
    """Return an exact ordering key for the supported intake timestamp profile."""
    match = re.fullmatch(
        r'([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]'
        r'([0-9]{2}):([0-9]{2}):([0-9]{2})'
        r'(?:\.([0-9]+))?([Zz]|[+-][0-9]{2}:[0-9]{2})', value)
    if match is None:
        raise ValueError('unsupported timestamp representation')
    year, month, day, hour, minute, second = map(int, match.groups()[:6])
    # Validate calendar/time fields without sending fractional digits through
    # datetime's microsecond precision or converting to a bounded UTC datetime.
    ordinal = datetime(year, month, day, hour, minute, second).toordinal()
    fraction, zone = match.groups()[6:]
    offset = 0
    if zone not in {'Z', 'z'}:
        offset_hour, offset_minute = int(zone[1:3]), int(zone[4:6])
        if offset_hour > 23 or offset_minute > 59:
            raise ValueError('unsupported timestamp offset')
        offset = (offset_hour * 60 + offset_minute) * 60
        if zone[0] == '-':
            offset = -offset
    seconds = ordinal * 86400 + hour * 3600 + minute * 60 + second - offset
    # Trailing-zero removal makes equal fractions identical. Lexical comparison
    # of the remaining ASCII digits preserves every supplied fractional digit.
    return seconds, (fraction or '').rstrip('0')


def intake_errors(catalog, pricebooks):
    errors = []
    items = {}
    for item in catalog:
        problems = schema_errors(item, SCHEMAS['catalog-item.schema.json'])
        if problems:
            errors.extend(problems)
            continue
        ident = item['id']
        if ident in items:
            errors.append(f'{ident}: duplicate catalog ID; intake requires one version per ID')
        items[ident] = item
        if item['tier'] != KINDS[item['kind']]['tier']:
            errors.append(f'{ident}: tier does not match canonical kind')
        if 'fixture' in ident.lower():
            errors.append(f'{ident}: reserved synthetic fixture ID')
        if any(not public_source(p.get('source_uri')) for p in item['provenance']):
            errors.append(f'{ident}: each provenance entry needs a real public source URL')
    for ident, item in items.items():
        for (kind, field), expected_kind in REFERENCES.items():
            if item['kind'] != kind or field not in item['spec']:
                continue
            values = item['spec'][field]
            for target in values if isinstance(values, list) else [values]:
                if target not in items or items[target]['kind'] != expected_kind:
                    errors.append(f'{ident}/{field}: unresolved or wrong-kind reference {target}')
    books = set()
    for book in pricebooks:
        problems = schema_errors(book, SCHEMAS['pricebook.schema.json'])
        if problems:
            errors.extend(problems)
            continue
        key = (book['id'], book['revision'])
        if key in books:
            errors.append(f'{key}: duplicate pricebook revision')
        books.add(key)
        rate_ids = set()
        for rate in book['rates']:
            ident = rate['id']
            if ident in rate_ids:
                errors.append(f'{ident}: duplicate rate ID within pricebook')
            rate_ids.add(ident)
            if 'fixture' in ident.lower() or 'fixture' in book['id'].lower():
                errors.append(f'{ident}: reserved synthetic fixture ID')
            target = items.get(rate['catalog_item_id'])
            if target is None or target['version'] != rate['catalog_item_version']:
                errors.append(f'{ident}: catalog ID/version does not resolve')
            if not public_source(rate['provenance'].get('source_uri')):
                errors.append(f'{ident}: rate needs a real public source URL')
            instants = {}
            for field in ('valid_from', 'valid_until'):
                if field in rate:
                    try:
                        instants[field] = price_instant(rate[field])
                    except ValueError:
                        errors.append(f'{ident}: {field} needs an ASCII timestamp with year '
                                      '0001-9999, seconds 00-59, and Z or a numeric offset '
                                      'for intake ordering')
            if ('valid_from' in instants and 'valid_until' in instants
                    and instants['valid_until'] <= instants['valid_from']):
                errors.append(f'{ident}: valid_until must follow valid_from')
    return errors


def model_inventory_errors(root):
    """Check the existing T1 notes and source links, without certifying claims."""
    directory = root / 'research/T1-model-selection'
    # Minimal submission trees need not include the separate T1 notes collection.
    if not directory.exists():
        return []
    errors = []
    documents = {}
    for name in ('inventory', 'sources'):
        path = directory / f'model-research-{name}.json'
        try:
            document = intake_json(path.read_text(encoding='utf-8'))
            if not isinstance(document, dict):
                raise ValueError('expected an object')
            documents[name] = document
        except (ValueError, OSError) as exc:
            errors.append(f'{path}: {exc}')

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def fields(record, names, label):
        for name in names:
            if not text(record.get(name)):
                errors.append(f'{label}/{name}: needs nonempty text')

    def date(value, label):
        try:
            if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
                raise ValueError('expected YYYY-MM-DD')
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            errors.append(f'{label}: needs a real YYYY-MM-DD date')

    def strings(value, label):
        if not isinstance(value, list) or not value or any(not text(v) for v in value):
            errors.append(f'{label}: needs a nonempty array of nonempty text')
            return []
        if len(set(value)) != len(value):
            errors.append(f'{label}: repeated entry')
        return value

    def rows(document, key, label):
        value = document.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f'{label}/{key}: needs a nonempty array')
            return []
        result = []
        for index, record in enumerate(value):
            row_label = f'{label}/{key}/{index}'
            if not isinstance(record, dict):
                errors.append(f'{row_label}: expected an object')
            else:
                result.append((record, row_label))
        return result

    source_ids = set()
    if 'sources' in documents:
        source_doc = documents['sources']
        fields(source_doc, ('format', 'status', 'policy'), 'model sources')
        if source_doc.get('format') != 'research-source-register':
            errors.append('model sources/format: expected research-source-register')
        for source, label in rows(source_doc, 'sources', 'model sources'):
            fields(source, ('id', 'publisher', 'evidence_grade', 'observer_group', 'verification'), label)
            ident = source.get('id')
            if text(ident):
                if ident in source_ids:
                    errors.append(f'{label}/id: duplicate source ID {ident}')
                source_ids.add(ident)
            date(source.get('accessed_on'), f'{label}/accessed_on')
            for url in strings(source.get('urls'), f'{label}/urls'):
                try:
                    parts = locator_parts(url)
                    if parts.scheme not in {'http', 'https'} or not parts.hostname:
                        raise ValueError('expected HTTP(S) URL with hostname')
                except ValueError as exc:
                    errors.append(f'{label}/urls: {exc}')
    if 'inventory' in documents:
        inventory = documents['inventory']
        fields(inventory, ('format', 'status', 'scope'), 'model inventory')
        if inventory.get('format') != 'research-notes-not-catalog':
            errors.append('model inventory/format: expected research-notes-not-catalog')
        date(inventory.get('accessed_on'), 'model inventory/accessed_on')
        for record, label in rows(inventory, 'records', 'model inventory'):
            fields(record, ('model', 'publisher', 'input_output', 'access', 'license_evidence',
                            'selection_caveat', 'artifact_type'), label)
            strings(record.get('task_families'), f'{label}/task_families')
            for ident in strings(record.get('source_ids'), f'{label}/source_ids'):
                if 'sources' in documents and ident not in source_ids:
                    errors.append(f'{label}/source_ids: unresolved source ID {ident}')
    return errors


def validate_tree(root=ROOT):
    errors = []
    def load_tree(relative):
        values = []
        for path in sorted((root / relative).rglob('*.json')):
            try:
                values.append(intake_json(path.read_text(encoding='utf-8'), exact_numbers=True))
            except (ValueError, OSError) as exc:
                errors.append(f'{path}: {exc}')
        return values
    catalog = load_tree('catalog/proposals')
    prices = load_tree('pricing/proposals')
    errors.extend(intake_errors(catalog, prices))
    manifest_schema = json.loads((ROOT / 'schemas/evidence-manifest.schema.json').read_text(encoding='utf-8'))
    artifact_ids = set()
    for manifest in load_tree('evidence'):
        problems = schema_errors(manifest, manifest_schema)
        if problems:
            errors.extend(problems)
            continue
        if manifest['id'] in artifact_ids:
            errors.append(f"{manifest['id']}: duplicate evidence artifact ID")
        artifact_ids.add(manifest['id'])
        try:
            uri = locator_parts(manifest['uri'])
            valid = uri.scheme in {'https', 's3', 'gs'} and uri.hostname and not (uri.query or uri.fragment)
        except ValueError:
            valid = False
        if not valid:
            errors.append(f"{manifest['id']}: use a stable https/s3/gs locator without credentials, query, or fragment")
    errors.extend(model_inventory_errors(root))
    return errors, len(catalog), len(prices)


def main():
    errors, count, prices = validate_tree()
    if errors:
        for error in errors:
            print(f'INVALID: {error}')
        raise SystemExit(1)
    print(f'Validated {count} catalog proposals and {prices} pricebooks plus external evidence metadata. Evidence review is still required.')


if __name__ == '__main__':
    main()
