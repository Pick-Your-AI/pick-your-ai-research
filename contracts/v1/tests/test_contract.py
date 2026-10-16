"""Run: python -m unittest discover -s tests -v (requires jsonschema>=4.20)."""
import copy
import json
import re
import sys
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import yaml
from referencing import Registry, Resource
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
from evaluate import Evaluator, UNKNOWN

def data(name): return json.loads((ROOT/'examples'/name).read_text())
def schema(name):return json.loads((ROOT/'schemas'/name).read_text())

SCHEMAS={p.name:json.loads(p.read_text()) for p in (ROOT/'schemas').glob('*.schema.json')}
REGISTRY=Registry().with_resources((s['$id'],Resource.from_contents(s)) for s in SCHEMAS.values())
FORMAT=FormatChecker()
SAMPLES={
  'catalog-snapshot.schema.json':'catalog.json',
  'build.schema.json':'build.json',
  'dependency-graph.schema.json':'dependency-graph.json',
  'ruleset.schema.json':'ruleset.json',
  'evaluation-report.schema.json':'evaluation-report.json',
  'pricebook.schema.json':'pricebook.json',
  'cost-estimate.schema.json':'cost-estimate.json',
  'event.schema.json':'event.json',
  'resource-estimate.schema.json':'resource-estimate.json',
  'quality-evaluation-run.schema.json':'quality-evaluation-run.json',
  'deployment-manifest.schema.json':'deployment-manifest.json'
}
REFERENCE_FIELDS={
 ('model','provider_ref'):'model_provider',
 ('embedding_model','provider_ref'):'model_provider',
 ('compute_profile','hosting_ref'):'hosting_platform',
 ('compute_profile','accelerator_ref'):'accelerator',
 ('hosting_platform','accelerator_refs'):'accelerator',
 ('storage','hosting_ref'):'hosting_platform',
 ('knowledge_base','data_source_refs'):'data_source',
 ('vector_database','hosting_ref'):'hosting_platform',
 ('mcp_server','tool_refs'):'tool',
 ('integration','associated_tool_refs'):'tool',
 ('training_compute','compute_profile_ref'):'compute_profile',
 ('training_compute','storage_ref'):'storage',
 ('training_dataset','data_source_refs'):'data_source',
 ('fine_tuned_model','base_model_ref'):'model',
 ('fine_tuned_model','training_framework_ref'):'training_framework',
 ('fine_tuned_model','training_dataset_ref'):'training_dataset',
 ('evaluation_suite','dataset_refs'):'training_dataset',
 ('deployment_target','hosting_ref'):'hosting_platform',
}

class TestSchema(unittest.TestCase):
    def setUp(self):
        self.catalog=data('catalog.json'); self.build=data('build.json'); self.rules=data('ruleset.json')

    def test_all_schemas_valid_draft2020(self):
        for name,s in SCHEMAS.items():
            with self.subTest(name=name):Draft202012Validator.check_schema(s)

    def test_example_files_conform_to_json_schemas(self):
        for sch,sample in SAMPLES.items():
            with self.subTest(schema=sch,example=sample):
                validator=Draft202012Validator(SCHEMAS[sch],registry=REGISTRY,format_checker=FORMAT)
                validator.validate(data(sample))

    def test_registry_same_kinds_tier_and_selection_settings(self):
        registry=schema('component-registry.json')['kinds']
        cat_schema=schema('catalog-item.schema.json')
        selection_schema=schema('selection.schema.json')
        self.assertEqual(set(registry),set(self.build_selection_kinds()))
        self.assertEqual(set(registry),{key.removeprefix('spec_') for key in cat_schema['$defs']})
        self.assertEqual(set(registry),{key.removeprefix('settings_') for key in selection_schema['$defs']})
        self.assertEqual(set(registry),set(i['kind'] for i in self.catalog['items']))
        self.assertEqual(len(registry),29)
        for item in self.catalog['items']:
            self.assertEqual(item['tier'],registry[item['kind']]['tier'])

    def build_selection_kinds(self):return [s['kind'] for s in self.build['selections']]

    def test_graph_and_rules_reference_registered_kinds(self):
        kinds=set(schema('component-registry.json')['kinds'])
        graph=data('dependency-graph.json')
        self.assertGreaterEqual(len(graph['edges']),50)
        self.assertGreaterEqual(len(self.rules['rules']),30)
        for edge in graph['edges']:
            self.assertIn(edge['dependent_kind'],kinds)
            self.assertIn(edge['depends_on_kind'],kinds)
            self.assertNotEqual(edge['dependent_kind'],edge['depends_on_kind'])
        for rule in self.rules['rules']:
            self.assertTrue(set(rule['affected_kinds'])<=kinds)

    def test_catalog_references_are_existing_and_correct_kind(self):
        catalog={item['id']:item for item in self.catalog['items']}
        for entry in self.catalog['items']:
            for (kind, field), target_kind in REFERENCE_FIELDS.items():
                if kind!=entry['kind'] or field not in entry['spec']:continue
                field_value=entry['spec'][field]
                refs=field_value if isinstance(field_value,list) else [field_value]
                for rid in refs:
                    with self.subTest(item=entry['id'],field=field,reference=rid):
                        self.assertIn(rid,catalog)
                        self.assertEqual(catalog[rid]['kind'],target_kind)

    def test_build_id_lock_and_relationships(self):
        selections={s['id']:s for s in self.build['selections']}
        catalog={c['id']:c for c in self.catalog['items']}
        self.assertEqual(self.build['locks']['catalog_snapshot_id'],self.catalog['id'])
        self.assertEqual(self.build['locks']['ruleset_id'],self.rules['id'])
        self.assertEqual(self.build['locks']['ruleset_version'],self.rules['version'])
        self.assertEqual(len(selections),len(self.build['selections']))
        self.assertEqual(len({(s['kind'],s['role']) for s in selections.values()}),len(selections))
        kinds=schema('component-registry.json')['kinds']
        for kind,metadata in kinds.items():
            selected=[s for s in selections.values() if s['kind']==kind and s['enabled']]
            if metadata['cardinality']=='one':self.assertLessEqual(len(selected),1)
            if metadata['activation']=='always' and metadata['cardinality']=='one':self.assertEqual(len(selected),1)
        for s in selections.values():
            self.assertIn(s['catalog_item_id'],catalog)
            self.assertEqual(s['catalog_item_version'],catalog[s['catalog_item_id']]['version'])
            self.assertEqual(s['kind'],catalog[s['catalog_item_id']]['kind'])
        ids=[l['id'] for l in self.build['links']]
        self.assertEqual(len(ids),len(set(ids)))
        for link in self.build['links']:
            self.assertIn(link['from_selection_id'],selections)
            self.assertIn(link['to_selection_id'],selections)

    def test_pricebook_and_quote_reconcile(self):
        pricebook=data('pricebook.json'); quote=data('cost-estimate.json')
        self.assertEqual(quote['pricebook_id'],pricebook['id'])
        self.assertEqual(quote['build_id'],self.build['id'])
        self.assertEqual(quote['build_revision'],self.build['revision'])
        selected={s['id']:s for s in self.build['selections'] if s['enabled']}
        catalog={c['id']:c for c in self.catalog['items']}
        rates={p['id']:p for p in pricebook['rates']}
        total=Decimal(0)
        billed=set()
        for li in quote['line_items']:
            self.assertIn(li['selection_id'],selected)
            self.assertIn(li['price_rate_id'],rates)
            rate=rates[li['price_rate_id']]
            self.assertEqual(rate['catalog_item_id'],selected[li['selection_id']]['catalog_item_id'])
            self.assertEqual(rate['catalog_item_version'],selected[li['selection_id']]['catalog_item_version'])
            self.assertEqual(rate['meter'],li['meter'])
            self.assertEqual(rate['unit_price'],li['unit_price'])
            self.assertEqual(li['unit_price']['currency'],quote['currency'])
            computed=Decimal(li['unit_price']['amount'])*Decimal(li['quantity'])
            self.assertEqual(Decimal(li['amount']['amount']),computed)
            total+=computed
            billed.add(li['selection_id'])
        self.assertEqual(total,Decimal(quote['subtotal']['amount']))
        self.assertEqual(total+Decimal(quote['tax']['amount']),Decimal(quote['total']['amount']))
        metered={s['id'] for s in selected.values() if catalog[s['catalog_item_id']]['billing_class']=='metered'}
        unknown={s['id'] for s in selected.values() if catalog[s['catalog_item_id']]['billing_class']=='unknown'}
        if quote['coverage']=='complete':
            self.assertTrue(metered<=billed)
            self.assertFalse(unknown)
            self.assertEqual(quote['unpriced_selection_ids'],[])

    def test_cross_tier_fixture_evaluates(self):
        report=Evaluator(self.build,self.catalog,self.rules,cost_estimate=data('cost-estimate.json'),resource_estimate=data('resource-estimate.json')).evaluate()
        self.assertEqual(report['result'],'valid')
        self.assertEqual(report['deployment_readiness'],'needs_review') # no automated production approval
        self.assertEqual(report['summary'],data('evaluation-report.json')['summary'])
        self.assertEqual(report['summary']['failed'],0)

    def test_dimension_mismatch_blocks(self):
        broken=copy.deepcopy(self.build)
        next(s for s in broken['selections'] if s['kind']=='vector_database')['settings']['index_dimension']=1024
        report=Evaluator(broken,self.catalog,self.rules,cost_estimate=data('cost-estimate.json'),resource_estimate=data('resource-estimate.json')).evaluate()
        self.assertIn('rule.embedding.dimension',[f['rule_id'] for f in report['findings'] if f['outcome']=='fail'])
        self.assertEqual(report['deployment_readiness'],'blocked')

    def test_provider_mismatch_blocks(self):
        broken=copy.deepcopy(self.catalog)
        next(x for x in broken['items'] if x['kind']=='model')['spec']['provider_ref']='cat.model_provider.someone_else'
        report=Evaluator(self.build,broken,self.rules,cost_estimate=data('cost-estimate.json'),resource_estimate=data('resource-estimate.json')).evaluate()
        self.assertIn('rule.model.provider.match',[f['rule_id'] for f in report['findings'] if f['outcome']=='fail'])

    def test_unestimated_vram_is_unknown_and_blocks(self):
        report=Evaluator(self.build,self.catalog,self.rules,cost_estimate=data('cost-estimate.json')).evaluate()
        f=next(f for f in report['findings'] if f['rule_id']=='rule.vram.estimate.fit')
        self.assertEqual(f['outcome'],'unknown')
        self.assertEqual(report['result'],'indeterminate')
        self.assertEqual(report['deployment_readiness'],'blocked')

    def test_stale_cost_estimate_is_unknown_not_pass(self):
        quote=data('cost-estimate.json');quote['build_revision']=999
        report=Evaluator(self.build,self.catalog,self.rules,cost_estimate=quote,resource_estimate=data('resource-estimate.json')).evaluate()
        self.assertEqual(next(f for f in report['findings'] if f['rule_id']=='rule.budget.monthly.cap')['outcome'],'unknown')
        self.assertEqual(report['deployment_readiness'],'blocked')

    def test_untrusted_resource_estimate_does_not_pass(self):
        evidence=data('resource-estimate.json');evidence['estimates'][0]['confidence']='unverified'
        report=Evaluator(self.build,self.catalog,self.rules,cost_estimate=data('cost-estimate.json'),resource_estimate=evidence).evaluate()
        self.assertEqual(next(f for f in report['findings'] if f['rule_id']=='rule.vram.estimate.fit')['outcome'],'unknown')

    def test_secret_reference_required_and_cleartext_rejected(self):
        model=next(s for s in self.build['selections'] if s['kind']=='model')
        model['settings']['credential_ref']='sk-this-is-not-a-secret-ref'
        validator=Draft202012Validator(schema('build.schema.json'),registry=REGISTRY,format_checker=FORMAT)
        self.assertFalse(validator.is_valid(self.build))

    def test_catalog_disallows_unknown_spec_field(self):
        model=next(x for x in self.catalog['items'] if x['kind']=='model')
        model['spec']['fantasy_option']=True
        validator=Draft202012Validator(schema('catalog-snapshot.schema.json'),registry=REGISTRY,format_checker=FORMAT)
        self.assertFalse(validator.is_valid(self.catalog))


    def test_baseline_contracts_are_valid_and_match_fixtures(self):
        graph=data('dependency-graph.json')
        rules=self.rules
        g=json.loads((ROOT/'baseline/core-dependency-graph.json').read_text())
        r=json.loads((ROOT/'baseline/core-ruleset.json').read_text())
        for filename,payload in [('dependency-graph.schema.json',g),('ruleset.schema.json',r)]:
            Draft202012Validator(SCHEMAS[filename],registry=REGISTRY,format_checker=FORMAT).validate(payload)
        self.assertEqual(g['edges'],graph['edges'])
        self.assertEqual(r['rules'],rules['rules'])
        self.assertEqual(self.build['locks']['dependency_graph_id'],g['id'])
        self.assertEqual(self.build['locks']['dependency_graph_revision'],g['revision'])

    def test_api_schema_refs_resolve_locally(self):
        spec=yaml.safe_load((ROOT/'api/openapi.yaml').read_text())
        self.assertEqual(spec['openapi'],'3.1.0')
        for path,operations in spec['paths'].items():
            for verb,operation in operations.items():
                if verb not in ('get','post','put','patch','delete'):continue
                self.assertTrue(operation['operationId'])
        def walk(node):
            if isinstance(node,dict):
                if isinstance(node.get('$ref'),str) and node['$ref'].startswith('../schemas/'):
                    self.assertTrue((ROOT/'api'/node['$ref']).exists(),node['$ref'])
                for v in node.values():walk(v)
            elif isinstance(node,list):
                for v in node:walk(v)
        walk(spec)

    def test_optional_cost_policy_and_deployment_branches_skip(self):
        build=copy.deepcopy(self.build)
        for selected in build['selections']:
            if selected['kind'] in ('cost_policy','deployment_target'):selected['enabled']=False
        report=Evaluator(build,self.catalog,self.rules,cost_estimate=data('cost-estimate.json'),resource_estimate=data('resource-estimate.json')).evaluate()
        for rid in ['rule.budget.monthly.cap','rule.production.gates']:
            self.assertEqual(next(f for f in report['findings'] if f['rule_id']==rid)['outcome'],'skipped')

    def test_multi_gpu_aggregate_does_not_hide_per_device_memory_failure(self):
        build=copy.deepcopy(self.build)
        catalog=copy.deepcopy(self.catalog)
        acc=next(s for s in build['selections'] if s['kind']=='accelerator')
        acc['settings']['device_count']=2
        next(s for s in build['selections'] if s['kind']=='inference_engine')['settings']['tensor_parallel_size']=2
        next(c for c in catalog['items'] if c['kind']=='compute_profile')['spec']['accelerator_count']=2
        next(c for c in catalog['items'] if c['kind']=='accelerator')['spec']['vram_gb']=16
        report=Evaluator(build,catalog,self.rules,cost_estimate=data('cost-estimate.json'),resource_estimate=data('resource-estimate.json')).evaluate()
        results={f['rule_id']:f['outcome'] for f in report['findings']}
        self.assertEqual(results['rule.vram.estimate.fit'],'pass')  # pooled quantity appears sufficient
        self.assertEqual(results['rule.vram.per.device.fit'],'fail') # per-device bound correctly fails

    def test_deployment_manifest_evidence_ids_match(self):
        m=data('deployment-manifest.json')
        self.assertEqual(m['build_id'],self.build['id'])
        self.assertEqual(m['build_revision'],self.build['revision'])
        self.assertEqual(m['quality_run_id'],data('quality-evaluation-run.json')['id'])
        self.assertEqual(m['compatibility_report_id'],data('evaluation-report.json')['id'])
        self.assertEqual(m['cost_estimate_id'],data('cost-estimate.json')['id'])
        self.assertEqual(m['resource_estimate_id'],data('resource-estimate.json')['id'])
        self.assertEqual(m['status'],'proposed')
        self.assertEqual(m['approvals'][0]['decision'],'pending')

    def test_no_sensitive_values_in_emitted_test_fixtures(self):
        for filename in SAMPLES.values():
            txt=(ROOT/'examples'/filename).read_text()
            self.assertNotRegex(txt,r'"(?:password|api_key|access_token|private_key|secret_value)"\s*:')


if __name__=='__main__':unittest.main()
