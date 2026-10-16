"""Small deterministic evaluator for the contract's safe rules DSL.

This demonstrates cross-tier graph validation. It is NOT a calibrated VRAM estimator,
benchmark engine, deployment gate, or vendor product compatibility certification.
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

UNKNOWN = object()
ID_RE = re.compile(r'^[a-z][a-z0-9._:-]{2,119}$')
DECIMAL_RE = re.compile(r'^(0|[1-9][0-9]*)(\.[0-9]{1,12})?$')


def pointer_get(document: object, pointer: str):
    if not pointer.startswith('/'):
        return UNKNOWN
    cur = document
    for segment in pointer[1:].split('/'):
        key = segment.replace('~1','/').replace('~0','~')
        if isinstance(cur,dict):
            if key not in cur:return UNKNOWN
            cur=cur[key]
        elif isinstance(cur,list) and key.isdecimal() and int(key)<len(cur):
            cur=cur[int(key)]
        else:return UNKNOWN
    return cur


def numeric(x):
    if isinstance(x,bool):return None
    if isinstance(x,(int,float,Decimal)):
        return Decimal(str(x))
    if isinstance(x,str) and DECIMAL_RE.fullmatch(x):return Decimal(x)
    return None


def boolean_and(args):
    if False in args:return False
    if UNKNOWN in args:return UNKNOWN
    return True


def boolean_or(args):
    if True in args:return True
    if UNKNOWN in args:return UNKNOWN
    return False


class Evaluator:
    def __init__(self, build, catalog, ruleset, metrics=None, cost_estimate=None, resource_estimate=None):
        self.build=build;self.ruleset=ruleset
        self.catalog={i['id']:i for i in catalog['items']}
        self.active=[s for s in build['selections'] if s['enabled']]
        self.metrics=metrics or {}
        self.cost_estimate=cost_estimate
        self.resource_estimate=resource_estimate

    def selected(self, ref):
        matches=[s for s in self.active if (not ref.get('kind') or s['kind']==ref['kind'])
                 and (not ref.get('role') or s['role']==ref['role'])
                 and (not ref.get('selection_id') or s['id']==ref['selection_id'])]
        return matches[0] if len(matches)==1 else UNKNOWN

    def value(self, operand):
        if 'literal' in operand:return operand['literal']
        if 'metric' in operand:
            name=operand['metric']
            if name in self.metrics:return self.metrics[name] # development fixture override only
            if name.startswith('inference.') or name.startswith('training.') or name.startswith('compute.estimated_'):
                doc=self.resource_estimate
                if doc and doc.get('build_id')==self.build['id'] and doc.get('build_revision')==self.build['revision']:
                    ranks={'unverified':0,'estimated':1,'calibrated':2,'verified':3}
                    minimum=self.build.get('policy',{}).get('min_resource_confidence','calibrated')
                    for estimate in doc['estimates']:
                        if estimate['metric']==name and ranks[estimate['confidence']]>=ranks[minimum]:
                            return Decimal(estimate['value'])
                return UNKNOWN
            if name == 'context.total_requested_tokens':
                s=self.selected({'kind':'context_policy','role':'primary'})
                if s is UNKNOWN:return UNKNOWN
                a=s['settings'].get('requested_context_tokens',UNKNOWN)
                b=s['settings'].get('reserved_output_tokens',UNKNOWN)
                return a+b if a is not UNKNOWN and b is not UNKNOWN else UNKNOWN
            if name == 'compute.total_selected_vram_gb':
                matches=[s for s in self.active if s['kind']=='accelerator']
                if not matches:return UNKNOWN
                total=Decimal('0')
                for s in matches:
                    item=self.catalog.get(s['catalog_item_id'])
                    if not item:return UNKNOWN
                    v=item['spec'].get('vram_gb',UNKNOWN)
                    count=s['settings'].get('device_count',UNKNOWN)
                    if v is UNKNOWN or count is UNKNOWN:return UNKNOWN
                    total+=Decimal(str(v))*count
                return total
            if name == 'compute.min_selected_device_vram_gb':
                matches=[s for s in self.active if s['kind']=='accelerator']
                if not matches:return UNKNOWN
                amounts=[]
                for s in matches:
                    item=self.catalog.get(s['catalog_item_id'])
                    if not item or not isinstance(item['spec'].get('vram_gb'),(int,float)):return UNKNOWN
                    amounts.append(Decimal(str(item['spec']['vram_gb'])))
                return min(amounts)
            if name == 'tools.mutating_count':
                matches=[s for s in self.active if s['kind']=='tool' and s['settings'].get('enabled',True)]
                n=0
                for s in matches:
                    c=self.catalog.get(s['catalog_item_id'])
                    if not c:return UNKNOWN
                    v=c['spec'].get('side_effect',UNKNOWN)
                    if v is UNKNOWN:return UNKNOWN
                    n+=int(v=='mutating')
                return n
            if name == 'cost.monthly_total_amount':
                q=self.cost_estimate
                if not q or q.get('coverage')!='complete' or q.get('build_revision')!=self.build['revision'] or q.get('build_id')!=self.build['id'] or q.get('period_days')!=30:return UNKNOWN
                if q['currency']!=self.build['objectives']['currency']:return UNKNOWN
                return q['total']['amount']
            # Runtime memory is deliberately never guessed from weight size.
            return UNKNOWN
        ref=operand['ref']
        if ref['scope']=='build': return pointer_get(self.build,ref['pointer'])
        sel=self.selected(ref)
        if sel is UNKNOWN:return UNKNOWN
        if ref['scope']=='selection': return pointer_get(sel,ref['pointer'])
        cat=self.catalog.get(sel['catalog_item_id'],UNKNOWN)
        if cat is UNKNOWN or cat['version']!=sel['catalog_item_version']:return UNKNOWN
        return pointer_get(cat,ref['pointer'])

    def compare(self,op,l,r):
        if l is UNKNOWN or r is UNKNOWN:return UNKNOWN
        if op in ('eq','ne'):
            nl,nr=numeric(l),numeric(r)
            equal= nl==nr if nl is not None and nr is not None else l==r
            return equal if op=='eq' else not equal
        if op in ('lt','lte','gt','gte'):
            nl,nr=numeric(l),numeric(r)
            if nl is None or nr is None:return UNKNOWN
            return {'lt':lambda: nl<nr,'lte':lambda:nl<=nr,'gt':lambda:nl>nr,'gte':lambda:nl>=nr}[op]()
        if op in ('contains','in'):
            container,item = (l,r) if op=='contains' else (r,l)
            return item in container if isinstance(container,(str,list,tuple,set)) else UNKNOWN
        if op=='intersects':return bool(set(l)&set(r)) if isinstance(l,list) and isinstance(r,list) else UNKNOWN
        if op=='subset_of':return set(l)<=set(r) if isinstance(l,list) and isinstance(r,list) else UNKNOWN
        return UNKNOWN

    def expr(self,expr):
        op=expr['op']
        if op=='exists':
            return self.value(expr['value']) is not UNKNOWN and self.value(expr['value']) is not None
        if op in ('all','any'):
            values=[self.expr(x) for x in expr['args']]
            return boolean_and(values) if op=='all' else boolean_or(values)
        if op=='not':
            x=self.expr(expr['arg'])
            return UNKNOWN if x is UNKNOWN else not x
        if op=='implies':
            a=self.expr(expr['if']); b=self.expr(expr['then'])
            return boolean_or([UNKNOWN if a is UNKNOWN else not a,b])
        return self.compare(op,self.value(expr['left']),self.value(expr['right']))

    def evaluate(self):
        findings=[]
        for rule in self.ruleset['rules']:
            applicable=self.expr(rule['applies_when'])
            result=self.expr(rule['assert']) if applicable is True else (None if applicable is False else UNKNOWN)
            outcome='skipped' if result is None else ('unknown' if result is UNKNOWN else ('pass' if result else 'fail'))
            code=rule['id'].replace('.','_').upper()
            selection_ids=sorted({s['id'] for s in self.active if s['kind'] in rule['affected_kinds']})
            findings.append(dict(rule_id=rule['id'],outcome=outcome,severity=rule['severity'],code=code,message=rule['message'] if outcome in ('fail','unknown') else f'{rule["id"]}: {outcome}',remediation=rule['remediation'] if outcome in ('fail','unknown') else '',selection_ids=selection_ids))
        summary={k:sum(f['outcome']==v for f in findings) for k,v in [('passed','pass'),('failed','fail'),('unknown','unknown'),('skipped','skipped')]}
        failures=any(f['outcome']=='fail' and f['severity']=='error' for f in findings)
        unknowns=any(f['outcome']=='unknown' for f in findings)
        unknown_blocks=any(f['outcome']=='unknown' and rule['on_unknown']=='block' for f,rule in zip(findings,self.ruleset['rules']))
        policy=self.build.get('policy',{})
        readiness='blocked' if failures or unknown_blocks or (unknowns and policy.get('fail_on_unknown',False)) else 'needs_review'
        # Even a structurally valid compatibility result is not proof of quality-evaluation gate success.
        return dict(schema_version=self.build['schema_version'],id=f'evaluation.{self.build["id"]}.r{self.build["revision"]}',build_id=self.build['id'],build_revision=self.build['revision'],catalog_snapshot_id=self.build['locks']['catalog_snapshot_id'],ruleset_id=self.ruleset['id'],ruleset_version=self.ruleset['version'],dependency_graph_id=self.build['locks']['dependency_graph_id'],dependency_graph_revision=self.build['locks']['dependency_graph_revision'],evaluated_at='2026-10-16T09:00:00Z',result='invalid' if failures else ('indeterminate' if unknowns else 'valid'),deployment_readiness=readiness,findings=findings,summary=summary)


def load(p):return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--build',required=True);ap.add_argument('--catalog',required=True);ap.add_argument('--rules',required=True)
    ap.add_argument('--cost');ap.add_argument('--resource',help='Version-pinned resource estimation evidence');ap.add_argument('--metrics',help='UNVERIFIED TEST OVERRIDE ONLY: JSON object of metrics');ap.add_argument('--output')
    args=ap.parse_args()
    ev=Evaluator(load(args.build),load(args.catalog),load(args.rules),json.loads(args.metrics) if args.metrics else None,load(args.cost) if args.cost else None,load(args.resource) if args.resource else None)
    result=ev.evaluate()
    output=json.dumps(result,indent=2)+'\n'
    if args.output:Path(args.output).write_text(output)
    else:print(output)

if __name__=='__main__':main()
