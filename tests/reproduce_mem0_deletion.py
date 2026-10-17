"""Opt-in, networked reproduction of the source-pinned Mem0 deletion finding.

Run: python tests/reproduce_mem0_deletion.py
Downloads two small upstream source files and checks their hashes. Executes the
exact synchronous deletion method with real upstream in-memory SQLite history,
a synthetic vector stub, and a no-op entity-cleanup stub. No Mem0 installation,
service, external storage, asynchronous path, or production data is involved.
This script is deliberately outside automatic unittest discovery.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
import logging
from types import SimpleNamespace
from typing import Optional
from urllib.request import urlopen


COMMIT = '94c3fe9f238f3dbf29c9ce98643bd71eb13077cd'
HASHES = {
    'main.py': 'f329ca4a17af1fbefb32ac10d4cc7ae7ddbdb7435a87eb74c30915cff98b8b7c',
    'storage.py': '5f5ecdadd2b260fd14f36a0f338336eb760275465dd1056a99a47e1ef07702bd',
}


def fetch(name):
    url = f'https://raw.githubusercontent.com/mem0ai/mem0/{COMMIT}/mem0/memory/{name}'
    with urlopen(url, timeout=30) as response:
        data = response.read(1_000_001)
    if len(data) > 1_000_000 or hashlib.sha256(data).hexdigest() != HASHES[name]:
        raise ValueError(f'Unexpected source bytes: {name}; refusing execution')
    return data.decode('utf-8')


def main():
    source = ast.parse(fetch('main.py'))
    memory = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'Memory')
    deletion = next(n for n in memory.body if isinstance(n, ast.FunctionDef) and n.name == '_delete_memory')
    normalizer = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == '_normalize_iso_timestamp_to_utc')
    namespace = {'logger': logging.getLogger(__name__), 'datetime': datetime, 'timezone': timezone, 'Optional': Optional}
    exec(compile(ast.Module(body=[normalizer, deletion], type_ignores=[]), 'pinned_main.py', 'exec'), namespace)
    storage = {}
    exec(compile(fetch('storage.py'), 'pinned_storage.py', 'exec'), storage)
    db = storage['SQLiteManager'](':memory:')
    vectors = {'synthetic-memory': SimpleNamespace(payload={
        'data': 'SYNTHETIC retained text', 'created_at': '2026-10-17T00:00:00Z',
    })}
    vector_store = SimpleNamespace(
        get=lambda vector_id: vectors.get(vector_id),
        delete=lambda vector_id: vectors.pop(vector_id),
    )
    instance = SimpleNamespace(vector_store=vector_store, db=db, _remove_memory_from_entity_store=lambda *_: None)
    try:
        namespace['_delete_memory'](instance, 'synthetic-memory')
        rows = db.get_history('synthetic-memory')
        if vectors or len(rows) != 1 or rows[0]['old_memory'] != 'SYNTHETIC retained text' or rows[0]['event'] != 'DELETE' or not rows[0]['is_deleted']:
            raise AssertionError('Pinned deletion/history outcome changed')
        print(json.dumps({
            'commit': COMMIT, 'source_sha256': HASHES,
            'scope': 'isolated synchronous method and SQLite history; synthetic vector/entity stubs',
            'vector_present_after_delete': bool(vectors),
            'history': {key: rows[0][key] for key in ['old_memory', 'new_memory', 'event', 'is_deleted']},
        }, indent=2))
    finally:
        db.close()


if __name__ == '__main__':
    main()
