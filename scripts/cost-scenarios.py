#!/usr/bin/env python3
"""Re-compute low / expected / high cost scenarios from a JSON spec, and check the figures a record quotes.

Usage: cost-scenarios.py SPEC_JSON [--json OUT_JSON]
SPEC_JSON:
  {"sig_figs": 2,
   "shared": {"name": value, ...},                      # inputs every scenario sees
   "cases": {"low": {...}, "expected": {...}, "high": {...}},   # driver values per case
   "scenarios": [{"id": "W1", "title": "...",
                  "vars": {...},                         # scenario inputs (all cases)
                  "case_vars": {"low": {...}, ...},      # scenario inputs per case (optional)
                  "steps": [["name", "expression"], ...],   # evaluated in order, per case
                  "report": ["name", ...],               # quantities to print
                  "expect": {"name": {"low": x, "expected": y, "high": z, "sf": 6}}}]}   # figures the record quotes;
                                                         # optional "sf" overrides sig_figs (use it for counts)
Expressions are Python arithmetic over the names in scope plus ceil, floor, sqrt, max, min, round.
Prints one table per scenario (full value, then rounded to sig_figs). Exits 1 if any expect value differs
from the re-computed value rounded to sig_figs.
"""
import json, math, sys
from decimal import Decimal, ROUND_HALF_UP

FUNCS = {'ceil': math.ceil, 'floor': math.floor, 'sqrt': math.sqrt, 'max': max, 'min': min, 'round': round}

def sf(x, n):
    # half-up rounding to n significant figures (Python's round() is half-even: 32,500 would give 32,000)
    if x == 0: return 0
    q = Decimal(1).scaleb(int(math.floor(math.log10(abs(x)))) - (n - 1))
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))

def fmt(x):
    if isinstance(x, float) and not x.is_integer(): return f'{x:,.6g}' if abs(x) < 1000 else f'{x:,.2f}'
    return f'{int(x):,}'

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__); sys.exit(0 if len(sys.argv) > 1 else 2)
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    n = spec.get('sig_figs', 2)
    cases = list(spec['cases'])
    out, bad = {}, []
    for sc in spec['scenarios']:
        res = {}
        for c in cases:
            env = dict(FUNCS)
            env.update(spec.get('shared', {})); env.update(spec['cases'][c])
            env.update(sc.get('vars', {})); env.update(sc.get('case_vars', {}).get(c, {}))
            for name, expr in sc['steps']:
                # eval is deliberate: the spec is a local file written by the record author, builtins are
                # stripped, and only arithmetic names are in scope. Do not point this at untrusted specs.
                env[name] = eval(expr, {'__builtins__': {}}, env)
            res[c] = {k: env[k] for k in sc['report']}
        out[sc['id']] = res
        print(f"\n{sc['id']}: {sc.get('title', '')}")
        print('  quantity'.ljust(34) + ''.join(c.rjust(26) for c in cases))
        for k in sc['report']:
            print(('  ' + k).ljust(34) + ''.join(f"{fmt(res[c][k])} ({fmt(sf(res[c][k], n))})".rjust(26) for c in cases))
        for k, want in sc.get('expect', {}).items():
            kn = want.get('sf', n)
            for c, v in want.items():
                if c == 'sf': continue
                got = sf(res[c][k], kn)
                if abs(got - v) > 1e-9 * max(1, abs(v)):
                    bad.append(f"{sc['id']} {k} {c}: record says {v}, re-computed {got} (full {res[c][k]})")
    if '--json' in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
    checked = sum(len([c for c in w if c != 'sf']) for sc in spec['scenarios'] for w in sc.get('expect', {}).values())
    print(f'\nchecked {checked} quoted figures against the re-computation')
    if bad: print('MISMATCH:', *bad, sep='\n  '); sys.exit(1)
    print('all quoted figures match')

if __name__ == '__main__':
    main()
