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


def validate_http_url(value, label):
    """Check the original text and parsed URL without contacting its host."""
    require(isinstance(value, str) and value.strip(), f'{label}: requires nonempty text')
    require(not any(character.isspace() or ord(character) < 0x20 or
                    ord(character) == 0x7f for character in value),
            f'{label}: whitespace or control character in URL')
    try:
        url = urlsplit(value)
        # Parsing alone does not validate a nonnumeric or out-of-range port.
        _ = url.port
        hostname = url.hostname
    except ValueError as error:
        raise MarketValidationError(f'{label}: invalid HTTP(S) URL') from error
    require(url.scheme in ('http', 'https') and hostname,
            f'{label}: requires HTTP(S) with a hostname')
    require(url.username is None and url.password is None, f'credentials in {label}')


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


def validate_integrations(integrations, product_ids, source_ids):
    """Check the research shortlist; these records cannot approve product use."""
    require(isinstance(integrations, list) and integrations,
            'integrations: requires a nonempty list')
    products, ranks = set(), set()
    uses = {'automated_retrieval', 'internal_research', 'display', 'redistribution'}

    def text_field(record, field, label):
        value = record.get(field)
        require(isinstance(value, str) and value.strip(),
                f'{label}: requires nonempty {field}')
        return value

    def date_field(record, field, label):
        value = text_field(record, field, label)
        try:
            parsed = date.fromisoformat(value)
        except ValueError as error:
            raise MarketValidationError(f'{label}: invalid {field}') from error
        require(parsed.isoformat() == value, f'{label}: {field} must use YYYY-MM-DD')

    def text_list(record, field, label):
        values = record.get(field)
        require(isinstance(values, list) and values and
                all(isinstance(value, str) and value.strip() for value in values),
                f'{label}: requires nonempty text list {field}')
        require(len(set(values)) == len(values), f'{label}: duplicate {field}')
        return values

    for index, record in enumerate(integrations):
        label = f'integrations[{index}]'
        require(isinstance(record, dict), f'{label}: requires an object')
        product = text_field(record, 'product_id', label)
        require(product in product_ids, f'{label}: unknown product_id {product}')
        require(product not in products, f'{label}: duplicate product_id {product}')
        products.add(product)
        rank = record.get('investigation_rank')
        require(type(rank) is int and rank > 0,
                f'{label}: investigation_rank must be a positive integer')
        require(rank not in ranks, f'{label}: duplicate investigation_rank')
        ranks.add(rank)
        for field in ('access', 'rights', 'maintenance', 'next_action',
                      'review_owner', 'update_cadence', 'rights_evidence_grade'):
            text_field(record, field, label)
        require(record.get('status') == 'Not approved for integration',
                f'{label}: shortlist status must remain Not approved for integration')
        require(type(record.get('consumer_issue')) is int and record['consumer_issue'] > 0,
                f'{label}: consumer_issue must be a positive integer')
        for field in ('access_date', 'last_checked'):
            date_field(record, field, label)
        references = text_list(record, 'source_ids', label)
        require(set(references) <= source_ids, f'{label}: unknown source_ids')
        for url in text_list(record, 'terms_urls', label):
            validate_http_url(url, f'{label}: terms_urls')
        permissions = record.get('reuse_permitted')
        require(isinstance(permissions, dict) and set(permissions) == uses,
                f'{label}: reuse_permitted must cover exactly the four intended uses')
        for use, decision in permissions.items():
            use_label = f'{label}: reuse_permitted.{use}'
            require(isinstance(decision, dict), f'{use_label}: requires an object')
            require(decision.get('value') in ('yes', 'no', 'unclear', 'unknown'),
                    f'{use_label}: unsupported value')
            for field in ('conditions', 'basis'):
                text_field(decision, field, use_label)
        if 'project_use_decision' in record:
            exclusion = record['project_use_decision']
            exclusion_label = f'{label}: project_use_decision'
            require(isinstance(exclusion, dict), f'{exclusion_label}: requires an object')
            require(exclusion.get('disposition') == 'exclude_from_current_product_scope',
                    f'{exclusion_label}: only the recorded product exclusion is supported')
            for field in ('status', 'basis', 'reconsideration'):
                text_field(exclusion, field, exclusion_label)
            for field in ('automated_product_retrieval', 'commercial_display', 'redistribution'):
                require(exclusion.get(field) is False,
                        f'{exclusion_label}: exclusion requires {field} to be false')
        assessment = record.get('research_assessment')
        require(isinstance(assessment, dict), f'{label}: requires research_assessment')
        assessment_label = f'{label}: research_assessment'
        date_field(assessment, 'assessment_date', assessment_label)
        for field in ('scope', 'ranking_rationale', 'maintenance_basis',
                      'code_material_scope', 'data_material_scope', 'unresolved_decisions'):
            text_field(assessment, field, assessment_label)
        require(assessment.get('maintenance_evidence_class') == 'Estimate',
                f'{assessment_label}: maintenance_evidence_class must be Estimate')
    require(ranks == set(range(1, len(integrations) + 1)),
            'integrations: investigation_rank must form 1 through shortlist size')


def validate():
    competitors, sources, matrix, backlog = (read(n) for n in
        ('competitors.json', 'sources.json', 'features.json', 'research-backlog.json'))
    ids = {c['id'] for c in competitors}
    require(len(ids) == len(competitors), 'duplicate competitor IDs')
    source_ids = {s['id'] for s in sources}
    require(len(source_ids) == len(sources), 'duplicate source IDs')
    validate_integrations(read('integrations.json'), ids, source_ids)
    for index, source in enumerate(sources):
        validate_http_url(source.get('url'), 'source URL')
        label = f'sources[{index}]'
        for field in ('access_date', 'access_status'):
            value = source.get(field)
            require(isinstance(value, str) and value.strip(),
                    f'{label}: requires nonempty {field}')
        try:
            accessed = date.fromisoformat(source['access_date'])
        except ValueError as error:
            raise MarketValidationError(f'{label}: invalid access_date') from error
        require(accessed.isoformat() == source['access_date'],
                f'{label}: access_date must use YYYY-MM-DD')
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
            validate_http_url(cell['evidence_url'], f'{pair}: evidence_url')
            try:
                access_date = date.fromisoformat(cell['access_date'])
            except ValueError as error:
                raise MarketValidationError(f'{pair}: invalid access_date') from error
            require(access_date.isoformat() == cell['access_date'],
                    f'{pair}: access_date must use YYYY-MM-DD')
    require(len(pairs) == len(ids) * len(matrix['definitions']), 'incomplete matrix')
    for index, item in enumerate(backlog):
        for field in ('number', 'parent_number'):
            value = item.get(field)
            require((field == 'parent_number' and value is None) or
                    (type(value) is int and value > 0),
                    f'backlog[{index}]: {field} must be a positive JSON integer'
                    + (' or absent/null' if field == 'parent_number' else ''))
    numbers = {item['number'] for item in backlog}
    require(len(numbers) == len(backlog), 'duplicate backlog issue')
    parents = {}
    for item in backlog:
        for key in ('question', 'owner', 'workstream', 'priority', 'readiness', 'status',
                    'deliverable', 'steps', 'priority_rationale', 'next_action'):
            require(item.get(key), (item['number'], key))
        require((BASE / item['deliverable']).exists(), item['deliverable'])
        scores = item['scores']
        require(isinstance(scores, list) and len(scores) == 6 and
                all(v is None or (type(v) is int and 1 <= v <= 5) for v in scores),
                'backlog scores must be six ordinal JSON integers from 1 to 5 or null')
        expected = None if None in scores else round(sum(a*b for a,b in zip(scores, (.25,.20,.20,.15,.1,.1))), 2)
        actual = item['score']
        require((actual is None if expected is None else
                 type(actual) in (int, float) and actual == expected),
                'incorrect priority arithmetic')
        if item.get('parent_number') is not None:
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
