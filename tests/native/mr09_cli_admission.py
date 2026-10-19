#!/usr/bin/env python3
"""Exercise the actual experimental CLI using a tiny synthetic GGUF, never weights."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile


def synthetic():
    string = lambda text: struct.pack('<Q', len(text.encode())) + text.encode()
    kv = {'context_length': 2048, 'embedding_length': 8, 'block_count': 1,
          'feed_forward_length': 16, 'attention.head_count': 2,
          'attention.head_count_kv': 1, 'attention.key_length': 4,
          'attention.value_length': 4, 'vocab_size': 16}
    meta = string('general.architecture') + struct.pack('<I', 8) + string('llama')
    for key, value in sorted(kv.items()):
        meta += string('llama.' + key) + struct.pack('<II', 4, value)
    tensors = [('token_embd.weight', [8,16]), ('blk.0.attn_norm.weight',[8]),
               ('blk.0.attn_q.weight',[8,8]), ('blk.0.attn_k.weight',[8,4]),
               ('blk.0.attn_v.weight',[8,4]), ('blk.0.attn_output.weight',[8,8]),
               ('blk.0.ffn_norm.weight',[8]), ('blk.0.ffn_gate.weight',[8,16]),
               ('blk.0.ffn_up.weight',[8,16]), ('blk.0.ffn_down.weight',[16,8]),
               ('output_norm.weight',[8]), ('output.weight',[8,16])]
    data = struct.pack('<IIQQ', 0x46554747, 3, len(tensors), len(kv)+1) + meta
    offset = 0
    for name, dimensions in tensors:
        data += string(name) + struct.pack('<I',len(dimensions))
        size = 2
        for dim in dimensions:
            data += struct.pack('<Q', dim)
            size *= dim
        data += struct.pack('<IQ', 1, offset)
        offset = (offset + size + 31) // 32 * 32
    return data + bytes((-len(data)) % 32) + bytes(offset)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    data = synthetic()
    digest = hashlib.sha256(data).hexdigest()
    p = dict(runtime_commit='620d2225cc436ab0b001e3200e590e3b286ef9ab',
             stage='completed-initialization-before-free', allocation='allocated',
             placement='single-CUDA0-all-layers', output_backend='CUDA0', host_readback='host',
             embeddings='disabled', backend_samplers='disabled', flash_attention='disabled',
             mmap='enabled', kv_offload='enabled', operation_offload='enabled',
             cache_key='f16', cache_value='f16', context_size=512, logical_batch_size=256,
             physical_batch_size=256, sequence_capacity=1, outputs_max=256, outputs_max_per_sequence=1)
    normal = json.dumps(p, separators=(',',':'))
    cases = [
        ('valid', normal, digest, False, 0),
        ('alias-only', normal.replace('"context_size"','"CONTEXT_SIZE"'), digest, False, 1),
        ('canonical-plus-alias', normal[:-1]+',"CONTEXT_SIZE":256}', digest, False, 1),
        ('duplicate', normal[:-1]+',"context_size":256}', digest, False, 1),
        ('unknown', normal[:-1]+',"extra":1}', digest, False, 1),
        ('fractional-capacity', normal.replace('"sequence_capacity":1','"sequence_capacity":1.5'),digest,False,1),
        ('boolean-capacity', normal.replace('"sequence_capacity":1','"sequence_capacity":true'),digest,False,1),
        ('overflow-capacity', normal.replace('"context_size":512','"context_size":4294967296'),digest,False,1),
        ('wrong-artifact', normal, '0'*64, False, 1),
        ('pipe', normal, digest, True, 1),
    ]
    results=[]
    with tempfile.TemporaryDirectory(prefix='mr09-cli-synthetic-') as tmp:
        path=Path(tmp)/'synthetic.gguf'
        path.write_bytes(data)
        for name, profile, pin, pipe, expected in cases:
            command=[str(binary),'--sha256',pin,'--profile',profile]
            if pipe:
                run=subprocess.run(command,input=data,capture_output=True,timeout=10)
            else:
                with path.open('rb') as source:
                    run=subprocess.run(command,stdin=source,capture_output=True,timeout=10)
            if run.returncode != expected:
                raise AssertionError((name,run.returncode,expected,run.stdout,run.stderr))
            if expected == 0:
                value=json.loads(run.stdout)
                if (value['host_readback_rows'] != 1 or value['graph_output_rows'] != 256
                        or value['estimate']['devices'][1]['computation']['output'] != 24576
                        or value['artifact_sha256'] != digest or value['artifact_bytes'] != len(data)):
                    raise AssertionError(('successful CLI output drift', value))
            else:
                if run.stdout or not isinstance(json.loads(run.stderr)['error'], str):
                    raise AssertionError(('failure was not a structured stderr error', name))
            results.append({'case':name,'expected_exit':expected,'actual_exit':run.returncode,
                            'profile':profile,'artifact_pin':pin,'stdin_kind':'pipe' if pipe else 'regular file',
                            'stdout':run.stdout.decode(),'stderr':run.stderr.decode()})
    print(json.dumps({'scope':'synthetic CPU CLI admission only','python_version':sys.version,'python_optimization':sys.flags.optimize,'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
                      'synthetic_bytes':len(data),'synthetic_sha256':digest,'cases':results},indent=2))

if __name__=='__main__':
    main()
