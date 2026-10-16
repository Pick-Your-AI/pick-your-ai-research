"""Build versioned JSON Schemas from the component type registry. No third-party packages needed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'schemas'
VERSION = '1.0.0'
BASE = 'https://schemas.ai-builder.example/v1/'


def emit(filename, obj):
    (SCHEMAS / filename).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def prop(t, **kw):
    return {'type':t, **kw}


def s(**kw): return prop('string', **kw)
def i(**kw): return prop('integer', **kw)
def n(**kw): return prop('number', **kw)
def b(**kw): return prop('boolean', **kw)
def arr(item, **kw): return prop('array', items=item, **kw)
def enum(*values): return s(enum=list(values))
def ref(kind=None):
    return s(pattern=r'^[a-z][a-z0-9._:-]{2,119}$', description=('Reference to catalog kind '+kind if kind else 'Catalog item ID'))
def secret(): return s(pattern=r'^secret://[A-Za-z0-9/_:.-]+$', description='Opaque secret manager reference, never the credential')
def decimal(): return s(pattern=r'^(0|[1-9][0-9]*)(\.[0-9]{1,12})?$', description='Non-negative base-10 decimal encoded as a string')
def fieldset(fields, required=()):
    return {'type':'object', 'additionalProperties':False, 'properties': fields, 'required': list(required)}

def extension_fields():
    return {'extensions': {'type':'object', 'description':'Namespaced vendor or project extension fields only.', 'patternProperties': {'^x_[a-z][a-z0-9_]*$': {}}, 'additionalProperties':False}}

cat = {}
def put(kind, tier, fields, required=(), cardinality='many', activation='optional', notes=''):
    if kind in cat: raise ValueError(kind)
    cat[kind] = {'tier':tier,'cardinality':cardinality,'activation':activation,'notes':notes,'catalog':fieldset(fields, required)}

put('workload','T0', dict(workload_type=enum('chat','completion','rag','agentic','embedding','fine_tuning','batch','multimodal'), modalities=arr(enum('text','image','audio','video','structured'),minItems=1,uniqueItems=True), concurrency=i(minimum=1), requests_per_day=i(minimum=0), avg_input_tokens=i(minimum=0), avg_output_tokens=i(minimum=0), latency_budget_ms=i(minimum=1), uptime_target_pct=n(minimum=0,maximum=100), data_classification=enum('public','internal','confidential','restricted')), ('workload_type','modalities'), 'one','always','Workload requirements drive all downstream choices.')
put('deployment_mode','T0', dict(mode=enum('api','managed','self_hosted','hybrid'), allowed_regions=arr(s())), ('mode',),'one','always','Mode activates API vs self-hosted branches.')
put('model_provider','T1', dict(api_base_url=s(format='uri'), supports_fine_tuning=b(), supported_regions=arr(s()), supported_auth=arr(enum('api_key','oauth2','service_account','none'))), (), 'many','always','Model publisher or API serving provider, not necessarily host.')
put('model','T1', dict(provider_ref=ref('model_provider'), model_type=enum('generative','multimodal','reranker','embedding'), modalities_in=arr(enum('text','image','audio','video','structured'),minItems=1,uniqueItems=True), modalities_out=arr(enum('text','image','audio','video','structured'),minItems=1,uniqueItems=True), context_window_tokens=i(minimum=1), max_output_tokens=i(minimum=1), supports_tool_calling=b(), supports_json_schema=b(), supports_fine_tuning=b(), access_modes=arr(enum('api','weights'),minItems=1,uniqueItems=True), weight_access=enum('open','restricted','none'), model_formats=arr(enum('safetensors','gguf','onnx','pytorch','api_only','other'),minItems=1,uniqueItems=True), supported_precisions=arr(enum('fp32','tf32','bf16','fp16','fp8','int8','int4'),uniqueItems=True), min_weights_vram_gb=n(minimum=0), license_ref=s()), ('provider_ref','model_type','modalities_in','modalities_out','context_window_tokens','max_output_tokens','access_modes','model_formats'), 'many','always','A base generative or auxiliary model.')
put('context_policy','T1', dict(max_allowed_tokens=i(minimum=1), supported_truncation=arr(enum('reject','truncate_oldest','summarize','sliding_window'),uniqueItems=True)), (), 'one','always','User-selected context and output reservations.')
put('hosting_platform','T2', dict(hosting_type=enum('cloud','on_prem','edge','colocation','managed_api'), regions=arr(s()), accelerator_refs=arr(ref('accelerator'),uniqueItems=True), supports_private_networking=b()), ('hosting_type',),'many','non_api','Infrastructure platform offered or owned.')
put('accelerator','T2', dict(accelerator_type=enum('gpu','tpu','npu','cpu'), vendor=s(minLength=1), model_name=s(minLength=1), vram_gb=n(minimum=0), backends=arr(enum('cuda','rocm','oneapi','metal','tpu','cpu','other'),minItems=1,uniqueItems=True), precisions=arr(enum('fp32','tf32','bf16','fp16','fp8','int8','int4'),minItems=1,uniqueItems=True), rated_power_w=n(minimum=0), interconnect=enum('pcie','nvlink','ethernet','proprietary','none')), ('accelerator_type','vendor','model_name','vram_gb','backends','precisions'),'many','self_hosted','Compute device capabilities, not an instance reservation.')
put('compute_profile','T2', dict(hosting_ref=ref('hosting_platform'), accelerator_ref=ref('accelerator'), accelerator_count=i(minimum=0), cpu_cores=i(minimum=1), ram_gb=n(minimum=0), disk_gb=n(minimum=0), region=s(minLength=1), network_gbps=n(minimum=0)), ('hosting_ref','cpu_cores','ram_gb','region'),'many','self_hosted','Provisionable host/instance SKU.')
put('inference_engine','T2', dict(backends=arr(enum('cuda','rocm','oneapi','metal','tpu','cpu','other'),minItems=1,uniqueItems=True), model_formats=arr(enum('safetensors','gguf','onnx','pytorch','api_only','other'),minItems=1,uniqueItems=True), supported_precisions=arr(enum('fp32','tf32','bf16','fp16','fp8','int8','int4'),minItems=1,uniqueItems=True), supports_tool_calling=b(), supports_multi_gpu=b(), max_batch_size=i(minimum=1)), ('backends','model_formats','supported_precisions'),'many','self_hosted','Local or customer-managed model serving runtime.')
put('storage','T2', dict(storage_type=enum('object','block','file','relational','in_memory'), hosting_ref=ref('hosting_platform'), region=s(), encryption_at_rest=b(), max_capacity_gb=n(minimum=0)), ('storage_type',),'many','optional','Storage can back knowledge, vector DB, agent memory, and model artifacts.')
put('data_source','T3', dict(source_type=enum('file','url','database','api','connector','event_stream'), modalities=arr(enum('text','image','audio','video','structured'),minItems=1,uniqueItems=True), classification=enum('public','internal','confidential','restricted'), refresh_supported=b(), access_controlled=b()), ('source_type','modalities','classification'),'many','optional','Source metadata; raw document content is not part of catalog.')
put('knowledge_base','T3', dict(data_source_refs=arr(ref('data_source'),minItems=1,uniqueItems=True), supported_modalities=arr(enum('text','image','audio','video','structured'),uniqueItems=True), supports_acl=b(), supports_incremental_sync=b()), ('data_source_refs',),'many','optional','Logical curated corpus; sources may span connectors.')
put('embedding_model','T3', dict(provider_ref=ref('model_provider'), embedding_dimensions=i(minimum=1), max_input_tokens=i(minimum=1), similarity_metrics=arr(enum('cosine','dot','euclidean'),minItems=1,uniqueItems=True), supported_modalities=arr(enum('text','image','audio','video','structured'),minItems=1,uniqueItems=True), access_modes=arr(enum('api','weights'),minItems=1,uniqueItems=True)), ('provider_ref','embedding_dimensions','max_input_tokens','similarity_metrics','supported_modalities','access_modes'),'many','optional','Produces vectors for retrieval and long-term memory.')
put('vector_database','T3', dict(supported_metrics=arr(enum('cosine','dot','euclidean'),minItems=1,uniqueItems=True), max_dimensions=i(minimum=1), supports_hybrid_search=b(), supports_acl=b(), regions=arr(s()), hosting_ref=ref('hosting_platform')), ('supported_metrics',),'many','optional','A vector index is configured per selection with a fixed dimension.')
put('rag_pipeline','T3', dict(retrieval_mode=enum('dense','sparse','hybrid','keyword'), supports_rerank=b(), supported_chunking=arr(enum('fixed','semantic','recursive','none'),uniqueItems=True)), ('retrieval_mode',),'many','optional','Pipeline binds base model, knowledge, embedding, and retrieval storage.')
put('agent_framework','T4', dict(programming_languages=arr(enum('python','typescript','javascript','go','rust','java','other'),minItems=1,uniqueItems=True), supports_mcp=b(), supports_memory=b(), supports_multi_agent=b(), supports_tool_execution=b()), ('programming_languages',),'many','optional','Framework orchestration capabilities.')
put('tool','T4', dict(protocol=enum('http','grpc','cli','embedded','mcp'), side_effect=enum('read_only','mutating'), auth_methods=arr(enum('none','api_key','oauth2','service_account','mTLS'),uniqueItems=True), required_scopes=arr(s()), is_networked=b()), ('protocol','side_effect'),'many','optional','Callable capability; mutating actions require policy review.')
put('mcp_server','T4', dict(transport=enum('stdio','streamable_http','sse'), tool_refs=arr(ref('tool'),uniqueItems=True), auth_methods=arr(enum('none','api_key','oauth2','mTLS'),uniqueItems=True), trust_level=enum('internal','trusted_external','untrusted_external')), ('transport',),'many','optional','MCP tool provider, subject to authorization and transport compatibility.')
put('memory_store','T4', dict(memory_type=enum('working','session','long_term'), backing_type=enum('in_memory','relational','vector','object','file'), encryption_at_rest=b(), supports_ttl=b()), ('memory_type','backing_type'),'many','optional','Memory store shares storage or vector infrastructure across tiers.')
put('integration','T4', dict(integration_type=enum('api','webhook','event','connector'), auth_methods=arr(enum('none','api_key','oauth2','service_account','mTLS'),uniqueItems=True), rate_limit_per_minute=i(minimum=0), associated_tool_refs=arr(ref('tool'),uniqueItems=True)), ('integration_type',),'many','optional','External integrations can be callable via tools.')
put('training_framework','T5', dict(methods=arr(enum('sft','lora','qlora','dpo','full_finetune','distillation'),minItems=1,uniqueItems=True), backends=arr(enum('cuda','rocm','oneapi','metal','tpu','cpu','other'),minItems=1,uniqueItems=True), model_formats=arr(enum('safetensors','gguf','onnx','pytorch','api_only','other'),uniqueItems=True), distributed_supported=b()), ('methods','backends'),'many','optional','Fine-tuning method/backend support.')
put('training_compute','T5', dict(compute_profile_ref=ref('compute_profile'), max_gpu_hours=n(minimum=0), ephemeral=b(), storage_ref=ref('storage')), ('compute_profile_ref',),'many','optional','Training hardware provision reuses available compute profiles.')
put('training_dataset','T5', dict(data_source_refs=arr(ref('data_source'),minItems=1,uniqueItems=True), example_count=i(minimum=0), data_classification=enum('public','internal','confidential','restricted'), license_verified=b(), privacy_approved=b(), held_out_test_set=b()), ('data_source_refs','data_classification'),'many','optional','Training dataset governance and lineage.')
put('fine_tuned_model','T5', dict(base_model_ref=ref('model'), training_framework_ref=ref('training_framework'), training_dataset_ref=ref('training_dataset'), artifact_format=enum('safetensors','gguf','onnx','pytorch','api_only','other'), adapter_only=b(), supported_access_modes=arr(enum('api','weights'),uniqueItems=True)), ('base_model_ref','training_framework_ref','training_dataset_ref','artifact_format'),'many','optional','Derived model requires a traceable base, dataset, and training path.')
put('guardrail','T6', dict(targets=arr(enum('input','output','retrieval','tool','training'),minItems=1,uniqueItems=True), policies=arr(enum('pii','prompt_injection','toxicity','data_exfiltration','content','tool_permissions','secrets'),minItems=1,uniqueItems=True), enforcement=enum('audit','block','redact','escalate')), ('targets','policies','enforcement'),'many','optional','Safety and compliance controls at explicit enforcement points.')
put('evaluation_suite','T6', dict(metric_names=arr(s(minLength=1),minItems=1,uniqueItems=True), mode=enum('offline','online','both'), gate_on_deployment=b(), dataset_refs=arr(ref('training_dataset'),uniqueItems=True)), ('metric_names','mode'),'many','optional','A suite defines evaluation gates, not measured results.')
put('deployment_target','T6', dict(target_type=enum('api_endpoint','batch_worker','application','edge'), hosting_ref=ref('hosting_platform'), region=s(), supports_autoscale=b(), supports_rollback=b()), ('target_type',),'many','optional','The deployment artifact and runtime target.')
put('monitoring_stack','T6', dict(signals=arr(enum('latency','errors','token_usage','gpu_utilization','quality','drift','cost','traces','security'),minItems=1,uniqueItems=True), pii_redaction=b(), retention_days=i(minimum=0), exporter=enum('otlp','prometheus','vendor_api','none')), ('signals',),'many','optional','Central observability and resource/cost telemetry.')
put('cost_policy','T6', dict(default_currency=s(pattern='^[A-Z]{3}$'), supports_hard_cap=b(), alert_threshold_pct=n(minimum=0,maximum=100)), ('default_currency',),'one','optional','Budget controls applied to pricebook estimates.')

settings = {
 'workload':fieldset(dict(concurrency=i(minimum=1),requests_per_day=i(minimum=0),avg_input_tokens=i(minimum=0),avg_output_tokens=i(minimum=0),latency_budget_ms=i(minimum=1))),
 'deployment_mode':fieldset({}),
 'model_provider':fieldset(dict(region=s(),credential_ref=secret(),api_base_url=s(format='uri'))),
 'model':fieldset(dict(temperature=n(minimum=0,maximum=2),top_p=n(exclusiveMinimum=0,maximum=1),max_output_tokens=i(minimum=1),precision=enum('fp32','tf32','bf16','fp16','fp8','int8','int4'),serving_mode=enum('api','weights'),credential_ref=secret(),weights_uri=s(format='uri'))),
 'context_policy':fieldset(dict(requested_context_tokens=i(minimum=1),reserved_output_tokens=i(minimum=0),truncation_strategy=enum('reject','truncate_oldest','summarize','sliding_window'),kv_cache_precision=enum('fp32','bf16','fp16','fp8','int8','int4')), ('requested_context_tokens','reserved_output_tokens')),
 'hosting_platform':fieldset(dict(region=s(),account_ref=secret(),network_isolation=enum('public','private','air_gapped'))),
 'accelerator':fieldset(dict(device_count=i(minimum=1),tensor_parallel_groups=i(minimum=1)), ('device_count',)),
 'compute_profile':fieldset(dict(instances=i(minimum=1),reserved_hours_per_month=n(minimum=0),region=s()), ('instances',)),
 'inference_engine':fieldset(dict(tensor_parallel_size=i(minimum=1),max_batch_tokens=i(minimum=1),precision=enum('fp32','tf32','bf16','fp16','fp8','int8','int4'),quantization=enum('none','awq','gptq','gguf','bitsandbytes','other'))),
 'storage':fieldset(dict(provisioned_gb=n(minimum=0),region=s(),encryption_key_ref=secret())),
 'data_source':fieldset(dict(connector_secret_ref=secret(),refresh_minutes=i(minimum=1),enabled=b())),
 'knowledge_base':fieldset(dict(chunk_size_tokens=i(minimum=1),chunk_overlap_tokens=i(minimum=0),refresh_minutes=i(minimum=1),acl_enforced=b())),
 'embedding_model':fieldset(dict(credential_ref=secret(),output_dimensions=i(minimum=1),region=s())),
 'vector_database':fieldset(dict(index_dimension=i(minimum=1),similarity_metric=enum('cosine','dot','euclidean'),region=s(),index_name=s(minLength=1),credential_ref=secret()), ('index_dimension','similarity_metric')),
 'rag_pipeline':fieldset(dict(top_k=i(minimum=1),max_chunks=i(minimum=1),rerank_enabled=b())),
 'agent_framework':fieldset(dict(agent_count=i(minimum=1),max_iterations=i(minimum=1),timeout_ms=i(minimum=1))),
 'tool':fieldset(dict(enabled=b(),allowed_scopes=arr(s(),uniqueItems=True),timeout_ms=i(minimum=1),credential_ref=secret())),
 'mcp_server':fieldset(dict(endpoint=s(format='uri'),credential_ref=secret(),read_only=b())),
 'memory_store':fieldset(dict(ttl_hours=i(minimum=1),max_entries=i(minimum=1),encryption_key_ref=secret())),
 'integration':fieldset(dict(enabled=b(),endpoint=s(format='uri'),credential_ref=secret(),rate_limit_per_minute=i(minimum=0))),
 'training_framework':fieldset(dict(method=enum('sft','lora','qlora','dpo','full_finetune','distillation'),epochs=n(exclusiveMinimum=0),learning_rate=n(exclusiveMinimum=0),batch_size=i(minimum=1))),
 'training_compute':fieldset(dict(gpu_hours_budget=n(minimum=0),spot_allowed=b(),checkpoint_interval_minutes=i(minimum=1))),
 'training_dataset':fieldset(dict(train_split=n(minimum=0,maximum=1),eval_split=n(minimum=0,maximum=1),test_split=n(minimum=0,maximum=1),redaction_enabled=b())),
 'fine_tuned_model':fieldset(dict(use_adapter=b(),artifact_uri=s(format='uri'),revision=s())),
 'guardrail':fieldset(dict(enforcement=enum('audit','block','redact','escalate'),failure_action=enum('fail_closed','fail_open'))),
 'evaluation_suite':fieldset(dict(minimum_score=n(),gate_required=b(),dataset_size=i(minimum=1))),
 'deployment_target':fieldset(dict(environment=enum('development','staging','production'),replicas_min=i(minimum=0),replicas_max=i(minimum=1),region=s(),approval_ticket=s())),
 'monitoring_stack':fieldset(dict(sample_rate=n(minimum=0,maximum=1),retention_days=i(minimum=0),credential_ref=secret())),
 'cost_policy':fieldset(dict(monthly_budget_amount=decimal(),per_request_budget_amount=decimal(),enforce_hard_cap=b(),notify_at_pct=n(minimum=0,maximum=100))),
}
assert set(cat)==set(settings)

common_defs={
 'id':s(pattern=r'^[a-z][a-z0-9._:-]{2,119}$'),
 'selection_id':s(pattern=r'^[a-z][a-z0-9_-]{2,79}$'),
 'semver':s(pattern=r'^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$'),
 'timestamp':s(format='date-time'),
 'currency':s(pattern=r'^[A-Z]{3}$'),
 'decimal':decimal(),
 'money':fieldset({'amount':{'$ref':'#/$defs/decimal'},'currency':{'$ref':'#/$defs/currency'}},('amount','currency')),
 'secret_ref':secret(),
 'entity_ref':fieldset({'id':{'$ref':'#/$defs/id'},'version':s(minLength=1)},('id','version')),
 'provenance':fieldset({'source_uri':s(format='uri'),'checked_at':{'$ref':'#/$defs/timestamp'},'verification_status':enum('verified','user_supplied','estimated','unverified'),'notes':s()}, ('checked_at','verification_status')),
 'extensions':extension_fields()['extensions'],
}
emit('common.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'common.schema.json','title':'AI Builder common types','$defs':common_defs})

registry={'schema_version':VERSION,'description':'Canonical component-kind registry. All agent implementations MUST use these identifiers.','kinds':{k:{f:v for f,v in spec.items() if f!='catalog'} for k,spec in cat.items()}}
emit('component-registry.json',registry)

cat_defs={f'spec_{k}':v['catalog'] for k,v in cat.items()}
cat_fields={'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'kind':enum(*cat.keys()),'tier':enum('T0','T1','T2','T3','T4','T5','T6'),'name':s(minLength=1,maxLength=180),'version':s(minLength=1),'status':enum('active','preview','deprecated','retired'),'billing_class':enum('free','included','metered','unknown'),'spec':prop('object'),'description':s(),'tags':arr(s(),uniqueItems=True),'provenance':arr({'$ref':'common.schema.json#/$defs/provenance'},minItems=1),'license':fieldset({'spdx_id':s(),'commercial_use_allowed':b(),'self_hosting_allowed':b()}),'updated_at':{'$ref':'common.schema.json#/$defs/timestamp'}, 'extensions':{'$ref':'common.schema.json#/$defs/extensions'}}
cat_item=fieldset(cat_fields,('schema_version','id','kind','tier','name','version','status','billing_class','spec','provenance','updated_at'))
cat_item.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'catalog-item.schema.json','title':'Typed catalog item','$defs':cat_defs})
cat_item['allOf'] = []
for kind, value in cat.items():
    cat_item['allOf'].append({
        'if': {'properties': {'kind': {'const': kind}}, 'required':['kind']},
        'then': {'properties': {'tier': {'const': value['tier']}, 'spec': {'$ref':'#/$defs/spec_'+kind}}}
    })
emit('catalog-item.schema.json',cat_item)

selection_fields={'id':{'$ref':'common.schema.json#/$defs/selection_id'},'kind':enum(*cat.keys()),'catalog_item_id':{'$ref':'common.schema.json#/$defs/id'},'catalog_item_version':s(minLength=1),'role':s(pattern=r'^[a-z][a-z0-9_-]{0,49}$'),'enabled':b(),'settings':prop('object'),'notes':s(),'extensions':{'$ref':'common.schema.json#/$defs/extensions'}}
selection=fieldset(selection_fields,('id','kind','catalog_item_id','catalog_item_version','role','enabled','settings'))
selection.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'selection.schema.json','title':'Typed, version-pinned build component selection','$defs':{f'settings_{k}':v for k,v in settings.items()}})
selection['allOf'] = []
for kind in cat:
    selection['allOf'].append({
        'if': {'properties': {'kind': {'const': kind}}, 'required':['kind']},
        'then': {'properties': {'settings': {'$ref':'#/$defs/settings_'+kind}}}
    })
emit('selection.schema.json',selection)

build=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'revision':i(minimum=1),'name':s(minLength=1,maxLength=160),'owner_ref':s(minLength=1),
 'lifecycle':enum('draft','validated','ready','deployed','archived'),
 'created_at':{'$ref':'common.schema.json#/$defs/timestamp'}, 'updated_at':{'$ref':'common.schema.json#/$defs/timestamp'},
 'objectives':fieldset({'region':s(minLength=1),'currency':{'$ref':'common.schema.json#/$defs/currency'},'monthly_budget_amount':{'$ref':'common.schema.json#/$defs/decimal'},'requests_per_day':i(minimum=0),'avg_input_tokens':i(minimum=0),'avg_output_tokens':i(minimum=0),'max_concurrency':i(minimum=1),'data_classification':enum('public','internal','confidential','restricted'),'max_latency_ms':i(minimum=1)},('region','currency','data_classification')),
 'locks':fieldset({'catalog_snapshot_id':{'$ref':'common.schema.json#/$defs/id'},'ruleset_id':{'$ref':'common.schema.json#/$defs/id'},'ruleset_version':{'$ref':'common.schema.json#/$defs/semver'},'dependency_graph_id':{'$ref':'common.schema.json#/$defs/id'},'dependency_graph_revision':i(minimum=1),'pricebook_id':{'$ref':'common.schema.json#/$defs/id'}},('catalog_snapshot_id','ruleset_id','ruleset_version','dependency_graph_id','dependency_graph_revision')),
 'selections':arr({'$ref':'selection.schema.json'},minItems=2),
 'links':arr(fieldset({'id':{'$ref':'common.schema.json#/$defs/id'},'from_selection_id':{'$ref':'common.schema.json#/$defs/selection_id'},'to_selection_id':{'$ref':'common.schema.json#/$defs/selection_id'},'relation':enum('uses','provided_by','runs_on','served_by','stored_in','indexes_with','reads_from','derived_from','secured_by','evaluated_by','observed_by','deploys_to','trained_on','calls','exposes','feeds','other'),'required':b()},('id','from_selection_id','to_selection_id','relation'))),
 'policy':fieldset({'fail_on_unknown':b(),'require_evaluations_for_production':b(),'allow_unverified_catalog_items':b(),'min_resource_confidence':enum('estimated','calibrated','verified')},()),
 'extensions':{'$ref':'common.schema.json#/$defs/extensions'}
},('schema_version','id','revision','name','owner_ref','lifecycle','created_at','updated_at','objectives','locks','selections','links'))
build.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'build.schema.json','title':'AI Builder versioned build snapshot'})
emit('build.schema.json',build)

catalog_snapshot=fieldset({'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'revision':i(minimum=1),'captured_at':{'$ref':'common.schema.json#/$defs/timestamp'},'items':arr({'$ref':'catalog-item.schema.json'},minItems=1)},('schema_version','id','revision','captured_at','items'))
catalog_snapshot.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'catalog-snapshot.schema.json','title':'Versioned catalog snapshot'})
emit('catalog-snapshot.schema.json',catalog_snapshot)
print('Generated',len(cat),'component kinds and 5 schemas + registry')

# Cross-tier dependency graph: a dependency is not a validity rule. Graph edges drive invalidation.
dependency=fieldset({
 'schema_version':{'const':VERSION}, 'id':{'$ref':'common.schema.json#/$defs/id'},'revision':i(minimum=1),
 'edges':arr(fieldset({
   'id':{'$ref':'common.schema.json#/$defs/id'},
   'dependent_kind':enum(*cat.keys()), 'depends_on_kind':enum(*cat.keys()),
   'relationship':enum('requires','constrains','informs','produces'),
   'activation':enum('always','self_hosted','non_api','rag_enabled','agents_enabled','fine_tuning_enabled','if_selected','production_only'),
   'rationale':s(minLength=1)
 }, ('id','dependent_kind','depends_on_kind','relationship','activation','rationale')),minItems=1)
}, ('schema_version','id','revision','edges'))
dependency.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'dependency-graph.schema.json','title':'Bidirectional invalidation graph for component dependencies'})
emit('dependency-graph.schema.json',dependency)

operand= {'oneOf':[
    fieldset({'literal':{}},('literal',)),
    fieldset({'metric':enum('context.total_requested_tokens','compute.total_selected_vram_gb','compute.min_selected_device_vram_gb','inference.estimated_required_vram_gb','inference.estimated_peak_per_device_vram_gb','tools.mutating_count','cost.monthly_total_amount')},('metric',)),
    fieldset({'ref':fieldset({'scope':enum('build','catalog','selection'), 'pointer':s(pattern='^/'), 'kind':enum(*cat.keys()), 'role':s(pattern=r'^[a-z][a-z0-9_-]{0,49}$'),'selection_id':{'$ref':'common.schema.json#/$defs/selection_id'}},('scope','pointer'))},('ref',))
]}
compare_expr=fieldset({'op':enum('eq','ne','lt','lte','gt','gte','in','contains','subset_of','intersects'), 'left':{'$ref':'#/$defs/operand'}, 'right':{'$ref':'#/$defs/operand'}},('op','left','right'))
exists_expr=fieldset({'op':{'const':'exists'},'value':{'$ref':'#/$defs/operand'}},('op','value'))
logic_expr=fieldset({'op':enum('all','any'), 'args':arr({'$ref':'#/$defs/expression'},minItems=1)},('op','args'))
not_expr=fieldset({'op':{'const':'not'},'arg':{'$ref':'#/$defs/expression'}},('op','arg'))
implies_expr=fieldset({'op':{'const':'implies'},'if':{'$ref':'#/$defs/expression'},'then':{'$ref':'#/$defs/expression'}},('op','if','then'))
ruleset=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'version':{'$ref':'common.schema.json#/$defs/semver'},'published_at':{'$ref':'common.schema.json#/$defs/timestamp'},
 'rules':arr(fieldset({
   'id':{'$ref':'common.schema.json#/$defs/id'},'severity':enum('error','warning','info'),
   'applies_when':{'$ref':'#/$defs/expression'}, 'assert':{'$ref':'#/$defs/expression'},
   'on_unknown':enum('block','review','defer'),'message':s(minLength=1), 'remediation':s(minLength=1),
   'affected_kinds':arr(enum(*cat.keys()),minItems=1,uniqueItems=True),
   'owner':s(minLength=1)
 },('id','severity','applies_when','assert','on_unknown','message','remediation','affected_kinds')),minItems=1)
}, ('schema_version','id','version','published_at','rules'))
ruleset.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'ruleset.schema.json','title':'Declarative explainable cross-tier compatibility rules', '$defs':{'operand':operand,'expression':{'oneOf':[compare_expr,exists_expr,logic_expr,not_expr,implies_expr]}}})
emit('ruleset.schema.json',ruleset)

finding=fieldset({
 'rule_id':{'$ref':'common.schema.json#/$defs/id'},'outcome':enum('pass','fail','unknown','skipped'), 'severity':enum('error','warning','info'),
 'code':s(pattern=r'^[A-Z][A-Z0-9_]{2,80}$'),'message':s(minLength=1), 'remediation':s(),
 'selection_ids':arr({'$ref':'common.schema.json#/$defs/selection_id'},uniqueItems=True),
 'evidence':arr(fieldset({'path':s(), 'observed':{},'expected':{},'source_version':s()},('path',)))
},('rule_id','outcome','severity','code','message','selection_ids'))
report=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'build_id':{'$ref':'common.schema.json#/$defs/id'},'build_revision':i(minimum=1),
 'catalog_snapshot_id':{'$ref':'common.schema.json#/$defs/id'}, 'ruleset_id':{'$ref':'common.schema.json#/$defs/id'},'ruleset_version':{'$ref':'common.schema.json#/$defs/semver'},'dependency_graph_id':{'$ref':'common.schema.json#/$defs/id'},'dependency_graph_revision':i(minimum=1),
 'evaluated_at':{'$ref':'common.schema.json#/$defs/timestamp'}, 'result':enum('valid','invalid','indeterminate'),
 'deployment_readiness':enum('ready','blocked','needs_review'), 'findings':arr(finding),
 'summary':fieldset({'passed':i(minimum=0),'failed':i(minimum=0),'unknown':i(minimum=0),'skipped':i(minimum=0)},('passed','failed','unknown','skipped'))
},('schema_version','id','build_id','build_revision','catalog_snapshot_id','ruleset_id','ruleset_version','dependency_graph_id','dependency_graph_revision','evaluated_at','result','deployment_readiness','findings','summary'))
report.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'evaluation-report.schema.json','title':'Deterministic compatibility evaluation for a pinned build revision'})
emit('evaluation-report.schema.json',report)

meter=enum('input_tokens_1m','output_tokens_1m','cached_input_tokens_1m','embedding_tokens_1m','request','gpu_hour','cpu_hour','storage_gb_month','vector_gb_month','agent_run','seat_month','license_month','one_time')
rate=fieldset({
 'id':{'$ref':'common.schema.json#/$defs/id'}, 'catalog_item_id':{'$ref':'common.schema.json#/$defs/id'}, 'catalog_item_version':s(minLength=1),
 'meter':meter,'region':s(),'unit_price':{'$ref':'common.schema.json#/$defs/money'},
 'valid_from':{'$ref':'common.schema.json#/$defs/timestamp'},'valid_until':{'$ref':'common.schema.json#/$defs/timestamp'},
 'provenance':{'$ref':'common.schema.json#/$defs/provenance'},
 'conditions':arr(s()),'price_type':enum('list','contract','estimate')
},('id','catalog_item_id','catalog_item_version','meter','unit_price','valid_from','provenance','price_type'))
pricebook=fieldset({'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'revision':i(minimum=1),'captured_at':{'$ref':'common.schema.json#/$defs/timestamp'},'rates':arr(rate,minItems=1)},('schema_version','id','revision','captured_at','rates'))
pricebook.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'pricebook.schema.json','title':'Versioned sourced metered prices'})
emit('pricebook.schema.json',pricebook)

cost_line=fieldset({
 'id':{'$ref':'common.schema.json#/$defs/id'},'selection_id':{'$ref':'common.schema.json#/$defs/selection_id'}, 'price_rate_id':{'$ref':'common.schema.json#/$defs/id'},
 'meter':meter,'quantity':{'$ref':'common.schema.json#/$defs/decimal'},'unit_price':{'$ref':'common.schema.json#/$defs/money'},
 'amount':{'$ref':'common.schema.json#/$defs/money'},'method':enum('measured','workload_projection','vendor_quote','manual_override'),
 'confidence':enum('high','medium','low'),'assumptions':arr(s())
},('id','selection_id','price_rate_id','meter','quantity','unit_price','amount','method','confidence','assumptions'))
cost_estimate=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'}, 'build_id':{'$ref':'common.schema.json#/$defs/id'},'build_revision':i(minimum=1),
 'pricebook_id':{'$ref':'common.schema.json#/$defs/id'},'estimated_at':{'$ref':'common.schema.json#/$defs/timestamp'},
 'period_days':i(minimum=1), 'currency':{'$ref':'common.schema.json#/$defs/currency'},
 'line_items':arr(cost_line), 'subtotal':{'$ref':'common.schema.json#/$defs/money'},
 'tax':{'$ref':'common.schema.json#/$defs/money'},'total':{'$ref':'common.schema.json#/$defs/money'},
 'coverage':enum('complete','partial','unknown'),'unpriced_selection_ids':arr({'$ref':'common.schema.json#/$defs/selection_id'},uniqueItems=True),
 'warnings':arr(s())
},('schema_version','id','build_id','build_revision','pricebook_id','estimated_at','period_days','currency','line_items','subtotal','tax','total','coverage','unpriced_selection_ids','warnings'))
cost_estimate.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'cost-estimate.schema.json','title':'Auditable cost estimate based on pinned build and pricebook'})
emit('cost-estimate.schema.json',cost_estimate)

event=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},
 'type':enum('build.created','build.selection.upserted','build.selection.removed','build.link.upserted','build.objectives.updated','build.validation.completed','build.cost.estimated','build.deployment.requested','build.deployed','catalog.item.published','catalog.snapshot.published','ruleset.published','pricebook.published'),
 'occurred_at':{'$ref':'common.schema.json#/$defs/timestamp'},'subject_type':enum('build','catalog_item','catalog_snapshot','ruleset','pricebook'),
 'subject_id':{'$ref':'common.schema.json#/$defs/id'},'subject_revision':i(minimum=1),'subject_version':s(),
 'actor_ref':s(minLength=1),'correlation_id':s(minLength=1),'causation_id':s(), 'idempotency_key':s(minLength=1),
 'payload':fieldset({'selection_id':{'$ref':'common.schema.json#/$defs/selection_id'},'catalog_item_id':{'$ref':'common.schema.json#/$defs/id'},'affected_kinds':arr(enum(*cat.keys()),uniqueItems=True),'evaluation_report_id':{'$ref':'common.schema.json#/$defs/id'},'cost_estimate_id':{'$ref':'common.schema.json#/$defs/id'},'note':s()},())
},('schema_version','id','type','occurred_at','subject_type','subject_id','subject_revision','actor_ref','correlation_id','idempotency_key','payload'))
event.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'event.schema.json','title':'Minimal idempotent, secret-free integration event'})
emit('event.schema.json',event)
print('Generated dependency, rules, evaluation, pricebook, cost, and event schemas')

resource_estimate=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'build_id':{'$ref':'common.schema.json#/$defs/id'},'build_revision':i(minimum=1),
 'generated_at':{'$ref':'common.schema.json#/$defs/timestamp'},
 'estimates':arr(fieldset({
  'metric':enum('inference.estimated_required_vram_gb','inference.estimated_peak_per_device_vram_gb','inference.estimated_tokens_per_second','compute.estimated_gpu_power_w','training.estimated_gpu_hours'),
  'value':{'$ref':'common.schema.json#/$defs/decimal'},'unit':enum('gb','tokens_per_second','watt','gpu_hour'),
  'estimator_id':s(minLength=1),'estimator_version':s(minLength=1),
  'confidence':enum('verified','calibrated','estimated','unverified'),
  'source_uri':s(format='uri'),'assumptions':arr(s()),'selection_ids':arr({'$ref':'common.schema.json#/$defs/selection_id'},minItems=1,uniqueItems=True)
 },('metric','value','unit','estimator_id','estimator_version','confidence','assumptions','selection_ids')),minItems=1)
},('schema_version','id','build_id','build_revision','generated_at','estimates'))
resource_estimate.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'resource-estimate.schema.json','title':'Version-pinned external compute and model-capacity estimates'})
emit('resource-estimate.schema.json',resource_estimate)

quality_run=fieldset({
 'schema_version':{'const':VERSION}, 'id':{'$ref':'common.schema.json#/$defs/id'}, 'build_id':{'$ref':'common.schema.json#/$defs/id'}, 'build_revision':i(minimum=1),
 'evaluation_suite_selection_id':{'$ref':'common.schema.json#/$defs/selection_id'},
 'started_at':{'$ref':'common.schema.json#/$defs/timestamp'},'finished_at':{'$ref':'common.schema.json#/$defs/timestamp'},
 'status':enum('passed','failed','incomplete'), 'evaluator_version':s(minLength=1),
 'dataset_revision':s(minLength=1),'sample_size':i(minimum=1),
 'measurements':arr(fieldset({'metric':s(minLength=1),'observed':n(), 'threshold':n(), 'comparator':enum('gte','gt','lte','lt','eq'),'unit':s(), 'passed':b()},('metric','observed','threshold','comparator','passed')),minItems=1),
 'artifacts':arr(s(format='uri')), 'notes':arr(s())
},('schema_version','id','build_id','build_revision','evaluation_suite_selection_id','started_at','finished_at','status','evaluator_version','dataset_revision','sample_size','measurements','artifacts'))
quality_run.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'quality-evaluation-run.schema.json','title':'Measured quality/safety evaluation evidence, separate from compatibility'})
emit('quality-evaluation-run.schema.json',quality_run)

deployment_manifest=fieldset({
 'schema_version':{'const':VERSION},'id':{'$ref':'common.schema.json#/$defs/id'},'build_id':{'$ref':'common.schema.json#/$defs/id'}, 'build_revision':i(minimum=1),
 'deployment_target_selection_id':{'$ref':'common.schema.json#/$defs/selection_id'},
 'compatibility_report_id':{'$ref':'common.schema.json#/$defs/id'},'quality_run_id':{'$ref':'common.schema.json#/$defs/id'},
 'cost_estimate_id':{'$ref':'common.schema.json#/$defs/id'}, 'resource_estimate_id':{'$ref':'common.schema.json#/$defs/id'},
 'approvals':arr(fieldset({'approver_ref':s(minLength=1),'decision':enum('approved','rejected','pending'),'approved_at':{'$ref':'common.schema.json#/$defs/timestamp'},'scope':enum('security','owner','finance','compliance')},('approver_ref','decision','scope')),minItems=1),
 'rollout_strategy':enum('canary','blue_green','rolling','manual'), 'rollback_artifact_uri':s(format='uri'),
 'requested_at':{'$ref':'common.schema.json#/$defs/timestamp'},'status':enum('proposed','approved','rejected','deployed','rolled_back'),
 'deployment_reference':s(), 'notes':arr(s())
},('schema_version','id','build_id','build_revision','deployment_target_selection_id','compatibility_report_id','quality_run_id','cost_estimate_id','resource_estimate_id','approvals','rollout_strategy','requested_at','status'))
deployment_manifest.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':BASE+'deployment-manifest.schema.json','title':'Deployment evidence and explicit approval manifest'})
emit('deployment-manifest.schema.json',deployment_manifest)
print('Generated capacity evidence, quality evaluations, and deployment manifest schemas')
