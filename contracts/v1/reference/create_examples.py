"""Emit entirely fictional, internally consistent end-to-end fixtures for contract consumers."""
import json
from pathlib import Path
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[1]
EXAMPLES=ROOT/'examples'; SCHEMAS=ROOT/'schemas'
REG=json.loads((SCHEMAS/'component-registry.json').read_text())
NOW='2026-10-16T09:00:00Z'
V='1.0.0'

def save(name,data): (EXAMPLES/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
def rid(k): return 'cat.'+k+'.fixture'
def sid(k): return 'sel_'+k

# Fictional hardware, model, provider and rates: NOT public product specifications.
specs={
 'workload':dict(workload_type='agentic',modalities=['text'],concurrency=2,requests_per_day=200,avg_input_tokens=700,avg_output_tokens=400,data_classification='internal'),
 'deployment_mode':dict(mode='self_hosted',allowed_regions=['us-east-fixture']),
 'model_provider':dict(supports_fine_tuning=True,supported_regions=['us-east-fixture']),
 'model':dict(provider_ref=rid('model_provider'),model_type='generative',modalities_in=['text'],modalities_out=['text'],context_window_tokens=8192,max_output_tokens=1024,supports_tool_calling=True,supports_json_schema=True,supports_fine_tuning=True,access_modes=['weights'],weight_access='open',model_formats=['safetensors'],supported_precisions=['fp16','int8'],min_weights_vram_gb=12),
 'context_policy':dict(max_allowed_tokens=8192,supported_truncation=['reject','truncate_oldest']),
 'hosting_platform':dict(hosting_type='cloud',regions=['us-east-fixture'],accelerator_refs=[rid('accelerator')],supports_private_networking=True),
 'accelerator':dict(accelerator_type='gpu',vendor='Fixture Hardware Inc.',model_name='Demo GPU 24',vram_gb=24,backends=['cuda'],precisions=['fp16','int8'],interconnect='pcie'),
 'compute_profile':dict(hosting_ref=rid('hosting_platform'),accelerator_ref=rid('accelerator'),accelerator_count=1,cpu_cores=8,ram_gb=64,disk_gb=300,region='us-east-fixture'),
 'inference_engine':dict(backends=['cuda'],model_formats=['safetensors'],supported_precisions=['fp16','int8'],supports_tool_calling=True,supports_multi_gpu=True,max_batch_size=8),
 'storage':dict(storage_type='object',hosting_ref=rid('hosting_platform'),region='us-east-fixture',encryption_at_rest=True,max_capacity_gb=2000),
 'data_source':dict(source_type='file',modalities=['text'],classification='internal',refresh_supported=True,access_controlled=True),
 'knowledge_base':dict(data_source_refs=[rid('data_source')],supported_modalities=['text'],supports_acl=True,supports_incremental_sync=True),
 'embedding_model':dict(provider_ref=rid('model_provider'),embedding_dimensions=768,max_input_tokens=4096,similarity_metrics=['cosine'],supported_modalities=['text'],access_modes=['weights']),
 'vector_database':dict(supported_metrics=['cosine','dot'],max_dimensions=4096,supports_hybrid_search=True,supports_acl=True,regions=['us-east-fixture'],hosting_ref=rid('hosting_platform')),
 'rag_pipeline':dict(retrieval_mode='dense',supports_rerank=True,supported_chunking=['fixed','semantic']),
 'agent_framework':dict(programming_languages=['python'],supports_mcp=True,supports_memory=True,supports_multi_agent=True,supports_tool_execution=True),
 'tool':dict(protocol='mcp',side_effect='mutating',auth_methods=['oauth2'],required_scopes=['fixture.write'],is_networked=True),
 'mcp_server':dict(transport='streamable_http',tool_refs=[rid('tool')],auth_methods=['oauth2'],trust_level='internal'),
 'memory_store':dict(memory_type='long_term',backing_type='vector',encryption_at_rest=True,supports_ttl=True),
 'integration':dict(integration_type='api',auth_methods=['oauth2'],rate_limit_per_minute=60,associated_tool_refs=[rid('tool')]),
 'training_framework':dict(methods=['lora','sft'],backends=['cuda'],model_formats=['safetensors'],distributed_supported=False),
 'training_compute':dict(compute_profile_ref=rid('compute_profile'),max_gpu_hours=50,ephemeral=True,storage_ref=rid('storage')),
 'training_dataset':dict(data_source_refs=[rid('data_source')],example_count=2000,data_classification='internal',license_verified=True,privacy_approved=True,held_out_test_set=True),
 'fine_tuned_model':dict(base_model_ref=rid('model'),training_framework_ref=rid('training_framework'),training_dataset_ref=rid('training_dataset'),artifact_format='safetensors',adapter_only=True,supported_access_modes=['weights']),
 'guardrail':dict(targets=['input','output','retrieval','tool','training'],policies=['pii','prompt_injection','tool_permissions','secrets'],enforcement='block'),
 'evaluation_suite':dict(metric_names=['answer_quality','latency_ms','tool_safety'],mode='both',gate_on_deployment=True,dataset_refs=[rid('training_dataset')]),
 'deployment_target':dict(target_type='api_endpoint',hosting_ref=rid('hosting_platform'),region='us-east-fixture',supports_autoscale=True,supports_rollback=True),
 'monitoring_stack':dict(signals=['latency','errors','token_usage','gpu_utilization','cost','traces','security'],pii_redaction=True,retention_days=30,exporter='otlp'),
 'cost_policy':dict(default_currency='USD',supports_hard_cap=True,alert_threshold_pct=80)
}
assert set(specs)==set(REG['kinds'])
cat=[]
for kind, spec in specs.items():
    cat.append(dict(schema_version=V,id=rid(kind),kind=kind,tier=REG['kinds'][kind]['tier'],name=f'FICTIONAL {kind.replace("_"," ").title()}',version='2026.10-demo',status='active',billing_class='metered' if kind in ('compute_profile','storage') else 'included',spec=spec,**({'license':dict(spdx_id='TEST-ONLY',commercial_use_allowed=True,self_hosting_allowed=True)} if kind=='model' else {}),provenance=[dict(checked_at=NOW,verification_status='user_supplied',notes='FICTIONAL TEST FIXTURE. Not vendor specification or commercial pricing.')],updated_at=NOW))
CATALOG=dict(schema_version=V,id='catalog.fixture.1',revision=1,captured_at=NOW,items=cat)
save('catalog.json',CATALOG)

settings={
 'workload':dict(concurrency=2,requests_per_day=200,avg_input_tokens=700,avg_output_tokens=400),
 'deployment_mode':{},
 'model_provider':{},
 'model':dict(serving_mode='weights',precision='fp16',max_output_tokens=512,temperature=0.4),
 'context_policy':dict(requested_context_tokens=4096,reserved_output_tokens=512,truncation_strategy='reject'),
 'hosting_platform':dict(region='us-east-fixture',network_isolation='private'),
 'accelerator':dict(device_count=1,tensor_parallel_groups=1),
 'compute_profile':dict(instances=1,region='us-east-fixture',reserved_hours_per_month=720),
 'inference_engine':dict(precision='fp16',tensor_parallel_size=1,max_batch_tokens=4096),
 'storage':dict(provisioned_gb=50,region='us-east-fixture'),
 'data_source':dict(enabled=True),
 'knowledge_base':dict(chunk_size_tokens=300,chunk_overlap_tokens=30,acl_enforced=True),
 'embedding_model':dict(output_dimensions=768),
 'vector_database':dict(index_dimension=768,similarity_metric='cosine',region='us-east-fixture',index_name='fixture-collection'),
 'rag_pipeline':dict(top_k=5,max_chunks=8),
 'agent_framework':dict(agent_count=2,max_iterations=8),
 'tool':dict(enabled=True,allowed_scopes=['fixture.write']),
 'mcp_server':dict(read_only=False),
 'memory_store':dict(ttl_hours=720),
 'integration':dict(enabled=True,rate_limit_per_minute=60),
 'training_framework':dict(method='lora',epochs=3,batch_size=2),
 'training_compute':dict(gpu_hours_budget=25),
 'training_dataset':dict(train_split=0.8,eval_split=0.1,test_split=0.1,redaction_enabled=True),
 'fine_tuned_model':dict(use_adapter=True),
 'guardrail':dict(enforcement='block',failure_action='fail_closed'),
 'evaluation_suite':dict(gate_required=True,minimum_score=0.85),
 'deployment_target':dict(environment='production',replicas_min=1,replicas_max=2,region='us-east-fixture'),
 'monitoring_stack':dict(sample_rate=0.1,retention_days=30),
 'cost_policy':dict(monthly_budget_amount='1000.00',enforce_hard_cap=True,notify_at_pct=80)
}
assert set(settings)==set(specs)
selections=[dict(id=sid(k),kind=k,catalog_item_id=rid(k),catalog_item_version='2026.10-demo',role='primary',enabled=True,settings=settings[k]) for k in specs]
rels=[
 ('model','model_provider','provided_by'),('model','context_policy','uses'),
 ('compute_profile','hosting_platform','runs_on'),('compute_profile','accelerator','uses'),('model','inference_engine','served_by'),('inference_engine','compute_profile','runs_on'),
 ('knowledge_base','data_source','reads_from'),('rag_pipeline','knowledge_base','reads_from'),('rag_pipeline','embedding_model','uses'),('rag_pipeline','vector_database','indexes_with'),
 ('vector_database','storage','stored_in'),('memory_store','vector_database','stored_in'),('agent_framework','rag_pipeline','uses'),('agent_framework','tool','calls'),
 ('agent_framework','mcp_server','calls'),('mcp_server','tool','exposes'),('integration','tool','exposes'),
 ('fine_tuned_model','model','derived_from'),('fine_tuned_model','training_dataset','trained_on'),('fine_tuned_model','training_framework','uses'),('training_compute','compute_profile','runs_on'),
 ('training_dataset','data_source','reads_from'),('deployment_target','hosting_platform','runs_on'),('deployment_target','model','deploys_to'),
 ('agent_framework','guardrail','secured_by'),('agent_framework','evaluation_suite','evaluated_by'),('agent_framework','monitoring_stack','observed_by')
]
links=[dict(id='link.'+str(ix).zfill(2),from_selection_id=sid(a),to_selection_id=sid(b),relation=c) for ix,(a,b,c) in enumerate(rels,1)]
build=dict(schema_version=V,id='build.fixture.1',revision=1,name='FICTIONAL Full-Stack AI Build',owner_ref='team.fixture',lifecycle='draft',created_at=NOW,updated_at=NOW,objectives=dict(region='us-east-fixture',currency='USD',monthly_budget_amount='1000.00',requests_per_day=200,avg_input_tokens=700,avg_output_tokens=400,max_concurrency=2,data_classification='internal',max_latency_ms=6000),locks=dict(catalog_snapshot_id=CATALOG['id'],ruleset_id='rules.fixture.1',ruleset_version=V,dependency_graph_id='dependencies.core.1',dependency_graph_revision=1,pricebook_id='prices.fixture.1'),selections=selections,links=links,policy=dict(fail_on_unknown=True,require_evaluations_for_production=True,allow_unverified_catalog_items=True,min_resource_confidence='estimated'))
save('build.json',build)

edges=[]
def edge(dependent,dependency,relationship='constrains',activation='if_selected',why=None):
    edges.append(dict(id=f'dep.{dependent}.{dependency}',dependent_kind=dependent,depends_on_kind=dependency,relationship=relationship,activation=activation,rationale=why or f'{dependent} selection must be reevaluated when {dependency} changes.'))
for child, parent, relationship, activation in [
 ('model','deployment_mode','constrains','always'),('model','model_provider','requires','always'),('context_policy','model','constrains','always'),
 ('accelerator','model','constrains','self_hosted'),('accelerator','context_policy','constrains','self_hosted'),
 ('compute_profile','accelerator','requires','self_hosted'),('compute_profile','hosting_platform','requires','self_hosted'),('compute_profile','model','constrains','self_hosted'),
 ('inference_engine','model','constrains','self_hosted'),('inference_engine','accelerator','constrains','self_hosted'),('inference_engine','fine_tuned_model','constrains','if_selected'),
 ('hosting_platform','deployment_mode','constrains','non_api'),('storage','hosting_platform','constrains','if_selected'),
 ('knowledge_base','data_source','requires','if_selected'),('embedding_model','model_provider','requires','if_selected'),
 ('vector_database','embedding_model','constrains','rag_enabled'),('vector_database','storage','informs','if_selected'),('vector_database','hosting_platform','constrains','if_selected'),
 ('rag_pipeline','knowledge_base','requires','rag_enabled'),('rag_pipeline','embedding_model','requires','rag_enabled'),('rag_pipeline','vector_database','requires','rag_enabled'),('rag_pipeline','model','constrains','rag_enabled'),
 ('agent_framework','model','constrains','agents_enabled'),('agent_framework','rag_pipeline','informs','if_selected'),('agent_framework','tool','constrains','agents_enabled'),
 ('mcp_server','agent_framework','constrains','agents_enabled'),('mcp_server','tool','requires','if_selected'),('mcp_server','hosting_platform','informs','if_selected'),
 ('integration','tool','informs','if_selected'),('memory_store','agent_framework','constrains','agents_enabled'),('memory_store','vector_database','constrains','if_selected'),('memory_store','storage','informs','if_selected'),
 ('training_framework','model','constrains','fine_tuning_enabled'),('training_compute','training_framework','constrains','fine_tuning_enabled'),('training_compute','compute_profile','requires','fine_tuning_enabled'),
 ('training_dataset','data_source','requires','fine_tuning_enabled'),('fine_tuned_model','model','requires','fine_tuning_enabled'),('fine_tuned_model','training_dataset','requires','fine_tuning_enabled'),('fine_tuned_model','training_framework','requires','fine_tuning_enabled'),
 ('guardrail','tool','constrains','if_selected'),('guardrail','rag_pipeline','constrains','if_selected'),('guardrail','model','constrains','always'),
 ('evaluation_suite','model','constrains','always'),('evaluation_suite','rag_pipeline','constrains','if_selected'),('evaluation_suite','agent_framework','constrains','if_selected'),('evaluation_suite','fine_tuned_model','constrains','if_selected'),
 ('deployment_target','hosting_platform','constrains','non_api'),('deployment_target','model','requires','always'),('deployment_target','agent_framework','informs','if_selected'),('deployment_target','guardrail','constrains','production_only'),('deployment_target','evaluation_suite','constrains','production_only'),
 ('monitoring_stack','deployment_target','informs','if_selected'),('monitoring_stack','model','informs','always'),('monitoring_stack','compute_profile','informs','if_selected'),
 ('cost_policy','model','informs','always'),('cost_policy','compute_profile','informs','self_hosted'),('cost_policy','storage','informs','if_selected'),('cost_policy','integration','informs','if_selected'),('cost_policy','training_compute','informs','if_selected')
]: edge(child,parent,relationship,activation)
save('dependency-graph.json',dict(schema_version=V,id='dependencies.core.1',revision=1,edges=edges))

# Rule expression helper DSL. The compatibility engine interprets these without eval().
def literal(v):return {'literal':v}
def r(kind,path,scope='catalog',role='primary'):return {'ref':{'scope':scope,'kind':kind,'role':role,'pointer':path}}
def bref(path):return {'ref':{'scope':'build','pointer':path}}
def metric(name):return {'metric':name}
def cmp(op,a,b):return dict(op=op,left=a,right=b)
def has(a):return dict(op='exists',value=a)
def ALL(*expr):return dict(op='all',args=list(expr))
def ANY(*expr):return dict(op='any',args=list(expr))
def NOT(expr):return dict(op='not',arg=expr)
def present(kind):return has(r(kind,'/id',scope='selection'))
def is_mode(mode):return cmp('eq',r('deployment_mode','/spec/mode'),literal(mode))

rules=[]
def rule(identifier,severity,when,assertion,message,remediation,kinds,on_unknown='block'):
    rules.append(dict(id='rule.'+identifier,severity=severity,applies_when=when,**{'assert':assertion},on_unknown=on_unknown,message=message,remediation=remediation,affected_kinds=kinds,owner='compatibility-agent'))
ALWAYS=cmp('eq',literal(True),literal(True))
rule('required.foundation','error',ALWAYS,ALL(present('workload'),present('deployment_mode'),present('model'),present('context_policy')),'Required T0/T1 components are absent.','Choose workload, deployment mode, primary model and context.',['workload','deployment_mode','model','context_policy'])
rule('model.provider.match','error',present('model'),cmp('eq',r('model','/spec/provider_ref'),r('model_provider','/catalog_item_id','selection')),'Selected model belongs to a different provider.','Select the corresponding model provider.',['model','model_provider'])
rule('model.context.fit','error',present('model'),cmp('gte',r('model','/spec/context_window_tokens'),metric('context.total_requested_tokens')),'Requested total tokens exceed model context capacity.','Reduce prompt/reserved output or select a model with a larger context window.',['model','context_policy','compute_profile'])
rule('model.output.limit','error',present('model'),cmp('gte',r('model','/spec/max_output_tokens'),r('context_policy','/settings/reserved_output_tokens','selection')),'Requested output reservation exceeds model maximum.','Reduce reserved output tokens or change model.',['model','context_policy'])
rule('selfhost.requires.infrastructure','error',is_mode('self_hosted'),ALL(present('hosting_platform'),present('accelerator'),present('compute_profile'),present('inference_engine')),'Self-hosting requires hosting, compute, accelerator and inference engine.','Choose compatible self-hosted infrastructure.',['deployment_mode','hosting_platform','accelerator','compute_profile','inference_engine'])
rule('selfhost.requires.weights','error',is_mode('self_hosted'),cmp('contains',r('model','/spec/access_modes'),literal('weights')),'Model weights are unavailable for self-hosting.','Choose a weights-access model or API mode.',['deployment_mode','model'])
rule('engine.model.format','error',ALL(is_mode('self_hosted'),present('inference_engine')),cmp('intersects',r('model','/spec/model_formats'),r('inference_engine','/spec/model_formats')),'Inference engine cannot load this model format.','Change model format or inference engine.',['model','inference_engine','fine_tuned_model'])
rule('engine.accelerator.backend','error',ALL(is_mode('self_hosted'),present('inference_engine')),cmp('intersects',r('accelerator','/spec/backends'),r('inference_engine','/spec/backends')),'Inference backend is incompatible with accelerator.','Select a compatible runtime/backend or accelerator.',['accelerator','inference_engine','hosting_platform'])
rule('precision.engine','error',ALL(is_mode('self_hosted'),present('inference_engine')),cmp('contains',r('inference_engine','/spec/supported_precisions'),r('model','/settings/precision','selection')),'Inference engine does not support selected model precision.','Change precision or inference engine.',['model','inference_engine'])
rule('precision.accelerator','error',ALL(is_mode('self_hosted'),present('accelerator')),cmp('contains',r('accelerator','/spec/precisions'),r('model','/settings/precision','selection')),'Accelerator does not support selected precision.','Change precision or accelerator.',['model','accelerator'])
rule('vram.estimate.fit','error',ALL(is_mode('self_hosted'),present('accelerator')),cmp('gte',metric('compute.total_selected_vram_gb'),metric('inference.estimated_required_vram_gb')),'Available accelerator memory is below calibrated runtime requirement or estimate is missing.','Provide a calibrated model+context+batch VRAM estimate; choose enough compatible GPU memory.',['model','accelerator','context_policy','inference_engine','compute_profile'],on_unknown='block')
rule('api.model.access','error',is_mode('api'),cmp('contains',r('model','/spec/access_modes'),literal('api')),'Model cannot be served by API mode.','Select an API-capable model or change deployment mode.',['deployment_mode','model'])
rule('host.region','error',ALL(is_mode('self_hosted'),present('hosting_platform')),cmp('eq',r('hosting_platform','/settings/region','selection'),bref('/objectives/region')),'Host region conflicts with build objective.','Select a hosting region allowed by the workload.',['hosting_platform','workload','deployment_target'])
rule('embedding.dimension','error',ALL(present('embedding_model'),present('vector_database')),cmp('eq',r('embedding_model','/settings/output_dimensions','selection'),r('vector_database','/settings/index_dimension','selection')),'Embedding and vector index dimensions do not match.','Recreate compatible index or select a matching embedding dimension.',['embedding_model','vector_database','memory_store','rag_pipeline'])
rule('vector.dimension.support','error',present('vector_database'),cmp('gte',r('vector_database','/spec/max_dimensions'),r('vector_database','/settings/index_dimension','selection')),'Vector index dimension exceeds DB capability.','Reduce dimensions or change vector database.',['vector_database','embedding_model'])
rule('vector.distance.support','error',present('vector_database'),cmp('contains',r('vector_database','/spec/supported_metrics'),r('vector_database','/settings/similarity_metric','selection')),'Selected similarity metric unsupported by vector database.','Change metric or vector DB.',['vector_database','embedding_model'])
rule('embedding.distance.support','error',ALL(present('embedding_model'),present('vector_database')),cmp('contains',r('embedding_model','/spec/similarity_metrics'),r('vector_database','/settings/similarity_metric','selection')),'Selected distance metric unsupported by embedding model.','Choose compatible embedding model or metric.',['embedding_model','vector_database'])
rule('rag.knowledge','error',present('rag_pipeline'),present('knowledge_base'),'RAG pipeline lacks a knowledge base.','Select a knowledge base.',['rag_pipeline','knowledge_base','data_source'])
rule('rag.dense.dependencies','error',ALL(present('rag_pipeline'),ANY(cmp('eq',r('rag_pipeline','/spec/retrieval_mode'),literal('dense')),cmp('eq',r('rag_pipeline','/spec/retrieval_mode'),literal('hybrid')))),ALL(present('embedding_model'),present('vector_database')),'Dense/hybrid retrieval requires an embedding model and vector database.','Select embedding and index components, or change to keyword retrieval.',['rag_pipeline','embedding_model','vector_database'])
rule('agent.tools.framework','error',present('tool'),ALL(present('agent_framework'),cmp('eq',r('agent_framework','/spec/supports_tool_execution'),literal(True))),'Tool execution is unsupported or no framework selected.','Choose a framework with supported tool execution.',['tool','agent_framework'])
rule('agent.mcp.framework','error',present('mcp_server'),ALL(present('agent_framework'),cmp('eq',r('agent_framework','/spec/supports_mcp'),literal(True))),'Selected framework does not support MCP.','Change framework or disable MCP.',['mcp_server','agent_framework','tool'])
rule('memory.vector.storage','error',ALL(present('memory_store'),cmp('eq',r('memory_store','/spec/backing_type'),literal('vector'))),present('vector_database'),'Vector-backed memory requires a vector database.','Select a vector database or change memory backend.',['memory_store','vector_database'])
rule('tool.mutation.guardrails','error',cmp('gt',metric('tools.mutating_count'),literal(0)),ALL(present('guardrail'),cmp('contains',r('guardrail','/spec/policies'),literal('tool_permissions'))),'Mutating tools require tool-permission guardrails.','Add a tool-permissions policy with enforceable actions.',['tool','mcp_server','guardrail','agent_framework'])
rule('training.model.capable','error',present('fine_tuned_model'),ALL(present('training_framework'),present('training_compute'),present('training_dataset'),cmp('eq',r('model','/spec/supports_fine_tuning'),literal(True))),'Fine-tuning path or base-model capability is incomplete.','Choose supported training framework, compute and dataset.',['model','fine_tuned_model','training_framework','training_compute','training_dataset'])
rule('training.dataset.governance','error',present('training_dataset'),ALL(cmp('eq',r('training_dataset','/spec/license_verified'),literal(True)),cmp('eq',r('training_dataset','/spec/privacy_approved'),literal(True))),'Training dataset license/privacy approval not verified.','Obtain approvals before training.',['training_dataset','data_source','guardrail'])
rule('training.base.lineage','error',present('fine_tuned_model'),cmp('eq',r('fine_tuned_model','/spec/base_model_ref'),r('model','/catalog_item_id','selection')),'Fine-tuning base model does not match selected model.','Align fine-tuned model base lineage and active model selection.',['fine_tuned_model','model'])
rule('training.method.support','error',present('training_framework'),cmp('contains',r('training_framework','/spec/methods'),r('training_framework','/settings/method','selection')),'Selected training method unsupported by framework.','Change training method.',['training_framework','model'])
rule('training.backend.support','error',ALL(present('training_framework'),present('accelerator')),cmp('intersects',r('training_framework','/spec/backends'),r('accelerator','/spec/backends')),'Training framework incompatible with accelerator backend.','Select compatible training compute/backend.',['training_framework','accelerator','training_compute'])
rule('restricted.monitoring.redaction','error',cmp('eq',bref('/objectives/data_classification'),literal('restricted')),ALL(present('monitoring_stack'),cmp('eq',r('monitoring_stack','/spec/pii_redaction'),literal(True))),'Restricted data requires observability redaction.','Enable PII redaction and audit its operation.',['workload','monitoring_stack'])
rule('production.gates','error',ALL(present('deployment_target'),cmp('eq',r('deployment_target','/settings/environment','selection'),literal('production'))),ALL(present('evaluation_suite'),present('monitoring_stack'),present('guardrail')),'Production deployment requires evaluation, monitoring and guardrails.','Configure and enforce production gates.',['deployment_target','evaluation_suite','monitoring_stack','guardrail'])
rule('budget.monthly.cap','error',ALL(present('cost_policy'),cmp('eq',r('cost_policy','/settings/enforce_hard_cap','selection'),literal(True))),cmp('lte',metric('cost.monthly_total_amount'),bref('/objectives/monthly_budget_amount')),'Estimated cost exceeds approved budget or pricing is incomplete.','Adjust capacity, token usage, or budget; obtain full pricing.',['cost_policy','model','compute_profile','storage','integration','training_compute'],on_unknown='block')

rule('compute.sku.accelerator','error',ALL(is_mode('self_hosted'),present('compute_profile')),cmp('eq',r('compute_profile','/spec/accelerator_ref'),r('accelerator','/catalog_item_id','selection')),'Compute SKU references another accelerator.','Select a compute SKU with this accelerator.',['compute_profile','accelerator'])
rule('compute.sku.host','error',ALL(is_mode('self_hosted'),present('compute_profile')),cmp('eq',r('compute_profile','/spec/hosting_ref'),r('hosting_platform','/catalog_item_id','selection')),'Compute profile belongs to another hosting platform.','Choose a compute SKU from the selected host.',['compute_profile','hosting_platform'])
rule('compute.accelerator.count','error',ALL(is_mode('self_hosted'),present('compute_profile')),cmp('gte',r('compute_profile','/spec/accelerator_count'),r('accelerator','/settings/device_count','selection')),'Compute SKU offers fewer accelerator devices than requested.','Reduce device count or choose a larger SKU.',['compute_profile','accelerator'])
rule('host.accelerator.catalog','error',ALL(is_mode('self_hosted'),present('hosting_platform')),cmp('contains',r('hosting_platform','/spec/accelerator_refs'),r('accelerator','/catalog_item_id','selection')),'Selected hosting platform does not offer the accelerator.','Choose a supported accelerator or host.',['hosting_platform','accelerator'])
rule('tensor.parallel.devices','error',ALL(is_mode('self_hosted'),present('inference_engine')),cmp('gte',r('accelerator','/settings/device_count','selection'),r('inference_engine','/settings/tensor_parallel_size','selection')),'Tensor-parallel size exceeds device count.','Reduce tensor parallelism or provision more GPUs.',['inference_engine','accelerator','compute_profile'])
rule('context.policy.limit','error',present('context_policy'),cmp('gte',r('context_policy','/spec/max_allowed_tokens'),metric('context.total_requested_tokens')),'Requested total context exceeds selected policy cap.','Reduce requested token capacity or select a larger context policy.',['context_policy','model'])
rule('model.serving.mode.selfhost','error',is_mode('self_hosted'),cmp('eq',r('model','/settings/serving_mode','selection'),literal('weights')),'Self-hosted deployment requires weights serving mode.','Select model serving_mode=weights.',['deployment_mode','model'])
rule('model.selfhost.license','error',is_mode('self_hosted'),cmp('eq',r('model','/license/self_hosting_allowed'),literal(True)),'Model self-hosting rights not confirmed by verified license metadata.','Verify model license before deploying or change model.',['model','deployment_mode'],on_unknown='block')
rule('deployment.target.region','error',present('deployment_target'),cmp('eq',r('deployment_target','/settings/region','selection'),bref('/objectives/region')),'Deployment target region differs from residency objective.','Select a compliant deployment region.',['deployment_target','hosting_platform','workload'])
rule('memory.framework.compatibility','error',present('memory_store'),ALL(present('agent_framework'),cmp('eq',r('agent_framework','/spec/supports_memory'),literal(True))),'Selected framework does not support memory.','Select a memory-capable framework or remove memory.',['memory_store','agent_framework'])
rule('training.artifact.engine','error',ALL(present('fine_tuned_model'),present('inference_engine')),cmp('contains',r('inference_engine','/spec/model_formats'),r('fine_tuned_model','/spec/artifact_format')),'Fine-tuned artifact format is not supported by inference engine.','Convert artifact or change engine.',['fine_tuned_model','inference_engine'])
rule('knowledge.restricted.acl','error',ALL(present('knowledge_base'),ANY(cmp('eq',bref('/objectives/data_classification'),literal('restricted')),cmp('eq',bref('/objectives/data_classification'),literal('confidential')))),cmp('eq',r('knowledge_base','/settings/acl_enforced','selection'),literal(True)),'Confidential/restricted knowledge must enforce access control.','Enable knowledge-base ACL enforcement.',['knowledge_base','workload','guardrail'])


rule('vram.per.device.fit','error',ALL(is_mode('self_hosted'),present('accelerator')),cmp('gte',metric('compute.min_selected_device_vram_gb'),metric('inference.estimated_peak_per_device_vram_gb')),'Per-device VRAM is below the model runtime peak (multi-GPU aggregate is not sufficient).','Provide per-device estimate or change sharding/quantization/GPU.',['model','accelerator','context_policy','inference_engine','compute_profile'],on_unknown='block')
rule('tensor.parallel.engine.support','error',ALL(is_mode('self_hosted'),present('inference_engine'),cmp('gt',r('inference_engine','/settings/tensor_parallel_size','selection'),literal(1))),cmp('eq',r('inference_engine','/spec/supports_multi_gpu'),literal(True)),'Inference runtime lacks multi-GPU tensor-parallel support.','Choose a supported engine or use single-device tensor parallelism.',['inference_engine','accelerator','compute_profile'])

RULES=dict(schema_version=V,id='rules.fixture.1',version=V,published_at=NOW,rules=rules)
save('ruleset.json',RULES)

rate_specs=[('compute_profile','gpu_hour','0.80'),('storage','storage_gb_month','0.05')]
rates=[]
for k,meter,price in rate_specs:
    rates.append(dict(id='rate.'+k+'.fixture',catalog_item_id=rid(k),catalog_item_version='2026.10-demo',meter=meter,region='us-east-fixture',unit_price=dict(amount=price,currency='USD'),valid_from=NOW,provenance=dict(checked_at=NOW,verification_status='estimated',notes='Illustrative price, NOT a live market quote.'),price_type='estimate'))
save('pricebook.json',dict(schema_version=V,id='prices.fixture.1',revision=1,captured_at=NOW,rates=rates))
lines=[]
for k,meter,price,qty in [('compute_profile','gpu_hour','0.80','720'),('storage','storage_gb_month','0.05','50')]:
    cost=Decimal(price)*Decimal(qty)
    lines.append(dict(id='line.'+k+'.fixture',selection_id=sid(k),price_rate_id='rate.'+k+'.fixture',meter=meter,quantity=qty,unit_price=dict(amount=price,currency='USD'),amount=dict(amount=f'{cost:.2f}',currency='USD'),method='workload_projection',confidence='low',assumptions=['FIXTURE ONLY: usage and pricing are illustrative.']))
subtotal=sum((Decimal(l['amount']['amount']) for l in lines),Decimal('0'))
COST=dict(schema_version=V,id='estimate.fixture.1',build_id=build['id'],build_revision=build['revision'],pricebook_id='prices.fixture.1',estimated_at=NOW,period_days=30,currency='USD',line_items=lines,subtotal=dict(amount=f'{subtotal:.2f}',currency='USD'),tax=dict(amount='0.00',currency='USD'),total=dict(amount=f'{subtotal:.2f}',currency='USD'),coverage='complete',unpriced_selection_ids=[],warnings=['Example treats non-metered test fixtures as included; does not estimate real licensing, taxes, network egress or training usage.'])
save('cost-estimate.json',COST)

EVENT=dict(schema_version=V,id='evt.fixture.1',type='build.selection.upserted',occurred_at=NOW,subject_type='build',subject_id=build['id'],subject_revision=1,actor_ref='agent.model-agent',correlation_id='correlation.fixture.1',idempotency_key='build.fixture.1.rev1.sel_model',payload=dict(selection_id='sel_model',affected_kinds=['model','context_policy','compute_profile','inference_engine','rag_pipeline','agent_framework','cost_policy']))
save('event.json',EVENT)
print('Wrote',len(cat),'catalog items,',len(selections),'selections,',len(links),'links,',len(edges),'graph edges,',len(rules),'cross-tier rules, 2 prices')
RESOURCE=dict(schema_version=V,id='resources.fixture.1',build_id=build['id'],build_revision=1,generated_at=NOW,estimates=[dict(metric='inference.estimated_required_vram_gb',value='20.0',unit='gb',estimator_id='fixture.estimator',estimator_version='0.0-fixture',confidence='estimated',assumptions=['Synthetic figure only. Includes fictitious model weights, KV cache and serving overhead at the selected context/concurrency.'],selection_ids=[sid('model'),sid('context_policy'),sid('inference_engine'),sid('accelerator')]),dict(metric='inference.estimated_peak_per_device_vram_gb',value='20.0',unit='gb',estimator_id='fixture.estimator',estimator_version='0.0-fixture',confidence='estimated',assumptions=['Synthetic per-device peak VRAM fixture, not a measured estimate.'],selection_ids=[sid('model'),sid('context_policy'),sid('inference_engine'),sid('accelerator')])])
save('resource-estimate.json',RESOURCE)
QUALITY=dict(schema_version=V,id='quality.fixture.1',build_id=build['id'],build_revision=1,evaluation_suite_selection_id=sid('evaluation_suite'),started_at=NOW,finished_at=NOW,status='passed',evaluator_version='0.0-fixture',dataset_revision='fixture-synthetic-dataset-v1',sample_size=100,measurements=[dict(metric='answer_quality',observed=0.91,threshold=0.85,comparator='gte',unit='score',passed=True)],artifacts=[],notes=['TEST FIXTURE: synthetic score, not an actual evaluation.'])
save('quality-evaluation-run.json',QUALITY)
MANIFEST=dict(schema_version=V,id='manifest.fixture.1',build_id=build['id'],build_revision=1,deployment_target_selection_id=sid('deployment_target'),compatibility_report_id='evaluation.build.fixture.1.r1',quality_run_id=QUALITY['id'],cost_estimate_id=COST['id'],resource_estimate_id=RESOURCE['id'],approvals=[dict(approver_ref='user.fixture',decision='pending',scope='owner')],rollout_strategy='canary',requested_at=NOW,status='proposed',notes=['Not approved or deployed. All evidence is synthetic.'])
save('deployment-manifest.json',MANIFEST)
print('Wrote capacity estimate, quality run, and pending deployment manifest fixtures')
# Reviewed starter contracts for real agents to extend with verified vendor data.
# These are general constraints, not a claim that catalog fixtures are production-ready.
BASELINE=ROOT/'baseline'
BASELINE.mkdir(exist_ok=True)
base_graph=dict(schema_version=V,id='dependencies.core.1',revision=1,edges=edges)
base_rules=dict(schema_version=V,id='rules.core.1',version=V,published_at=NOW,rules=rules)
for filename,obj in [('core-dependency-graph.json',base_graph),('core-ruleset.json',base_rules)]:
    (BASELINE/filename).write_text(json.dumps(obj,indent=2)+'\n')
print('Wrote 59-edge baseline dependency graph and 45-rule starter ruleset')
