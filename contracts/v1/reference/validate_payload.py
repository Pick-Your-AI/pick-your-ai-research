"""Validate an arbitrary AI Builder JSON payload against a bundled contract schema.

Usage: python reference/validate_payload.py schemas/build.schema.json examples/build.json
Requires jsonschema>=4.20, supports local relative schema references only.
"""
import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=Registry().with_resources((x['$id'],Resource.from_contents(x)) for x in (json.loads(p.read_text()) for p in (ROOT/'schemas').glob('*.schema.json')))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('schema_file',type=Path)
    parser.add_argument('data_file',type=Path)
    args=parser.parse_args()
    schema=json.loads(args.schema_file.read_text())
    payload=json.loads(args.data_file.read_text())
    Draft202012Validator.check_schema(schema)
    errors=sorted(Draft202012Validator(schema,registry=REGISTRY,format_checker=FormatChecker()).iter_errors(payload),key=lambda e:list(map(str,e.path)))
    if errors:
        for err in errors:
            path='/'+'/'.join(map(str,err.absolute_path))
            print(f'INVALID {path}: {err.message}')
        raise SystemExit(1)
    print(f'VALID {args.data_file} against {args.schema_file}')

if __name__=='__main__':main()
