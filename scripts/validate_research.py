"""Validate research intake; does not certify claims or publish runtime artifacts."""
import json
import math
import re
from datetime import datetime
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlsplit

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


def intake_json(text):
    """Decode an unambiguous JSON submission without non-finite numbers."""
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
        return number

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
        # Normalize Unicode hostname forms before reserved-domain/IP checks.
        host = (value.hostname or '').encode('idna').decode('ascii').removesuffix('.')
        reserved = host in {'example.com', 'example.org', 'example.net', 'localhost'} or any(
            host.endswith(s) for s in ('.example', '.invalid', '.test', '.localhost', '.example.com', '.example.org', '.example.net'))
        if (value.scheme not in {'http', 'https'} or not host or reserved
                or value.username is not None or value.password is not None or '%' in host):
            return False
        try:
            address = ip_address(host)
        except ValueError:
            # Legacy numeric hosts can be interpreted as local IPs by a browser.
            # Require a canonical IP literal rather than guessing its radix/parts.
            return re.fullmatch(r'(?:0[xX][0-9a-fA-F]*|[0-9]+)(?:\.(?:0[xX][0-9a-fA-F]*|[0-9]+))*', host) is None
        address = getattr(address, 'ipv4_mapped', None) or address
        return address.is_global and not (address.is_multicast or address.is_reserved
                                          or getattr(address, 'is_site_local', False))
    except (ValueError, TypeError):
        return False


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
            if rate.get('valid_until') and datetime.fromisoformat(rate['valid_until'].upper().replace('Z', '+00:00')) <= datetime.fromisoformat(rate['valid_from'].upper().replace('Z', '+00:00')):
                errors.append(f'{ident}: valid_until must follow valid_from')
    return errors


def validate_tree(root=ROOT):
    errors = []
    def load_tree(relative):
        values = []
        for path in sorted((root / relative).rglob('*.json')):
            try:
                values.append(intake_json(path.read_text(encoding='utf-8')))
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
