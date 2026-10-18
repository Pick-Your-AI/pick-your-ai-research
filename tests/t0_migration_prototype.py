"""Synthetic CD-7 projection experiment, not a contract reader or released adapter.

Inputs are already normalized, eligible fixture facts. Resolving evidence conflicts,
real catalog/selection references and field aliases remains next-version work.
Original v1 bytes are returned unchanged; proposed output lives in x_t0_* keys.
"""
from copy import deepcopy
import hashlib

SERVING_KINDS = {'model', 'embedding_model', 'vector_database', 'fine_tuned_model'}


def component_modes(components):
    by_id = {item['id']: item for item in components}
    if len(by_id) != len(components):
        raise ValueError('duplicate component identity')
    resolved = {}

    def resolve(key, visiting):
        if key in resolved:
            return resolved[key]
        if key in visiting or key not in by_id:
            return 'unknown'
        item = by_id[key]
        if item['kind'] not in SERVING_KINDS or not item.get('enabled', True):
            return None
        if item['kind'] == 'fine_tuned_model' and item.get('artifact_type') == 'adapter':
            base = item.get('base_id')
            # #81 inheritance is from a base model, not any serving component.
            # Keep synthetic model lineage traversal; real link/catalog agreement
            # remains CD-6 work, not something this projection establishes.
            base_item = by_id.get(base)
            result = (resolve(base, visiting | {key})
                      if base_item and base_item['kind'] in {'model', 'fine_tuned_model'}
                      else 'unknown')
            result = result or 'unknown'
        elif item['kind'] == 'fine_tuned_model' and item.get('artifact_type') != 'full':
            result = 'unknown'
        else:
            facts = item.get('deployment', {})
            operator, capacity = facts.get('runtime_operator'), facts.get('capacity')
            if operator == 'self':
                result = 'self_hosted'
            elif operator == 'provider' and capacity == 'shared':
                result = 'api'
            elif operator == 'provider' and capacity in {'reserved_throughput', 'dedicated_instances'}:
                result = 'managed'
            else:
                result = 'unknown'
        resolved[key] = result
        return result

    for key in by_id:
        resolve(key, set())
    modes = set(resolved.values())
    overall = 'unknown' if not modes or 'unknown' in modes else (
        next(iter(modes)) if len(modes) == 1 else 'hybrid')
    return resolved, overall


def project(original_bytes, extension):
    """Return untouched historical bytes and an explicitly synthetic sidecar.

    Workload precedence chooses a candidate, never silently resolves disagreement.
    Null in a fixture means absent evidence, not a proposed contract answer state.
    """
    facts = deepcopy(extension['x_t0_migration_inputs'])
    modes, overall = component_modes(facts.get('components', []))
    profile, conflicts = {}, {}
    sources = facts.get('workload_sources', {})
    for source in ('objectives', 'selection_settings', 'catalog_preset'):
        for field, value in sources.get(source, {}).items():
            if value is not None:
                profile.setdefault(field, value)
    for field, chosen in profile.items():
        observed = {name: values[field] for name, values in sources.items()
                    if field in values and values[field] is not None}
        if any(value != chosen for value in observed.values()):
            conflicts[field] = observed
    locks = facts.get('locks', {})
    missing = [kind for kind in ('catalog_snapshot', 'pricebook')
               if locks.get(kind + '_id') and not locks.get(kind + '_revision')]
    return original_bytes, {'x_t0_migration_projection': {
        'synthetic': True,
        'historical_sha256': hashlib.sha256(original_bytes).hexdigest(),
        'component_modes': modes,
        'overall_mode': overall,
        'workload_candidate': profile,
        'workload_conflicts': conflicts,
        'unreproducible_locks': missing,
    }}
