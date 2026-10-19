#!/usr/bin/env python3
"""Build the opt-in MR-09 CPU estimator from a pinned local upstream checkout.

No model, GPU or native measurement is fetched or executed. Only an explicitly
selected module download can use the network; an existing dependency cache is
the default. The output directory must not already exist.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'research/market/measurements/gguf-parser-mr09'
PIN = '637cd9a7a03993ab30ace3c53dd8af5c37f46a94'
TREE = '4b67ed5331cbd40639db36890f8453c61ac604b7'

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--go', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--module-cache', type=Path, required=True)
    parser.add_argument('--build-cache', type=Path)
    parser.add_argument('--allow-module-download', action='store_true')
    args = parser.parse_args()
    upstream, compiler = args.upstream.resolve(), args.go.resolve(strict=True)
    manifest = json.loads((BUNDLE / 'source-manifest.json').read_text())
    for relative, expected in manifest['package_sha256'].items():
        if sha(ROOT / relative) != expected:
            parser.error(f'package hash mismatch: {relative}')
    actual = subprocess.check_output(['git', '--no-replace-objects', '-C', str(upstream), 'rev-parse', f'{PIN}^{{tree}}'], text=True).strip()
    if actual != TREE:
        parser.error('upstream tree mismatch')
    version = subprocess.check_output([str(compiler), 'version'], text=True).strip()
    if not version.startswith('go version go1.22.9 '):
        parser.error('this source preparation requires Go 1.22.9')
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = output / 'source'
    source.mkdir()
    archive = subprocess.check_output(['git', '--no-replace-objects', '-C', str(upstream), 'archive', PIN])
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(source, filter='data')
    # Archive attributes can omit or substitute leaves; verify every literal
    # pinned Git blob and executable bit before applying the derivative.
    tree_bytes = subprocess.check_output(['git', '--no-replace-objects', '-C', str(upstream), 'ls-tree', '-rz', PIN])
    expected_leaves = {}
    for item in tree_bytes.split(b'\0'):
        if not item:
            continue
        meta, name = item.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise RuntimeError('unsupported upstream tree entry')
        expected_leaves[name.decode()] = (mode, blob)
    actual_leaves = {}
    for path in source.rglob('*'):
        if path.is_symlink():
            raise RuntimeError('unexpected archived symlink')
        if not path.is_file():
            continue
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        mode = '100755' if path.stat().st_mode & 0o111 else '100644'
        actual_leaves[path.relative_to(source).as_posix()] = (mode, blob)
    if actual_leaves != expected_leaves:
        raise RuntimeError('archive does not preserve the complete pinned Git leaf inventory')
    env = os.environ.copy()
    env.update(GOTOOLCHAIN='local', GOWORK='off', GOENV='off', GOROOT=str(compiler.parent.parent),
               GOEXPERIMENT='', GOMAXPROCS='2', GOFLAGS='', CGO_ENABLED='0',
               GOPRIVATE='', GONOPROXY='', GONOSUMDB='', GOVCS='*:off',
               GOSUMDB='sum.golang.org' if args.allow_module_download else 'off',
               GOPROXY='https://proxy.golang.org' if args.allow_module_download else 'off',
               GOMODCACHE=str(args.module_cache.resolve()),
               GOCACHE=str((args.build_cache or output / 'cache').resolve()))
    # Fix host compilation, even if a caller's environment requested cross-builds.
    hosts = subprocess.check_output([str(compiler), 'env', 'GOHOSTOS', 'GOHOSTARCH'], text=True, env=env).splitlines()
    env.update(GOOS=hosts[0], GOARCH=hosts[1])
    verify_command = [str(compiler), 'mod', 'verify']
    with (output / 'module-verify.log').open('wb') as log:
        subprocess.run(verify_command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    original = source / 'mr09_output_semantic_test.go'
    shutil.copyfile(ROOT / 'tests/native/mr09_original_semantic_test.go', original)
    original_command = [str(compiler), 'test', '-p', '1', '-count=1', '-run', '^TestMR09(OriginalSemanticFixture|DefaultBehaviorReceipt)$', '-v', '.']
    with (output / 'original-red.log').open('wb') as log:
        before = subprocess.run(original_command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    before_log = (output / 'original-red.log').read_text()
    expected_failures = ['initial host output payload: got 24576 bytes', 'device output graph term: got 0 bytes', 'output graph placed on host: got 24576 bytes']
    if (before.returncode != 1 or re.findall(r'^--- FAIL: (\S+)', before_log, re.M) != ['TestMR09OriginalSemanticFixture']
            or '--- PASS: TestMR09DefaultBehaviorReceipt' not in before_log
            or any(before_log.count(item) != 1 for item in expected_failures)):
        raise RuntimeError('original run did not reproduce the selected three semantic assertions')
    original.unlink()
    subprocess.run(['git', 'apply', '--check', str(BUNDLE / 'derivative.patch')], cwd=source, check=True)
    subprocess.run(['git', 'apply', str(BUNDLE / 'derivative.patch')], cwd=source, check=True)
    shutil.copyfile(ROOT / 'tests/native/mr09_output_semantic_test.go', source / 'mr09_output_semantic_test.go')
    commands = [
        [str(compiler), 'test', '-p', '1', '-count=1', '-run', '^TestMR09', '-v', '.'],
        [str(compiler), 'build', '-p', '1', '-buildvcs=false', '-o', str(output / 'mr09-init-estimate'), './cmd/mr09-init-estimate'],
    ]
    for index, command in enumerate(commands):
        with (output / ('cpu-tests.log' if index == 0 else 'build.log')).open('wb') as log:
            subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    binary = output / 'mr09-init-estimate'
    build_info_command = [str(compiler), 'version', '-m', str(binary)]
    with (output / 'binary-build-info.log').open('wb') as log:
        subprocess.run(build_info_command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=30)
    cli_command = [sys.executable, str(ROOT / 'tests/native/mr09_cli_admission.py'), '--binary', str(binary)]
    with (output / 'cli-admission.json').open('wb') as log:
        subprocess.run(cli_command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    receipt = {
        'status': 'experimental CPU build; no native comparison',
        'python_version': sys.version, 'python_optimization': sys.flags.optimize,
        'upstream_commit': PIN, 'upstream_tree': TREE, 'verified_upstream_leaves': len(actual_leaves),
        'package_sha256': manifest['package_sha256'],
        'go_version': version, 'go_executable_sha256': sha(compiler),
        'module_verify_log_sha256': sha(output / 'module-verify.log'),
        'binary_build_info_sha256': sha(output / 'binary-build-info.log'),
        'go_mod_sha256': sha(source / 'go.mod'), 'go_sum_sha256': sha(source / 'go.sum'),
        'commands': [verify_command, original_command] + commands + [build_info_command, cli_command],
        'effective_build_environment': {key: env[key] for key in ('GOTOOLCHAIN','GOWORK','GOENV','GOROOT','GOEXPERIMENT','GOMAXPROCS','GOFLAGS','CGO_ENABLED','GOPRIVATE','GONOPROXY','GONOSUMDB','GOVCS','GOSUMDB','GOPROXY','GOMODCACHE','GOCACHE','GOOS','GOARCH')},
        'candidate_executable_sha256': sha(binary), 'candidate_executable_bytes': binary.stat().st_size,
        'original_red_log_sha256': sha(output / 'original-red.log'),
        'cli_admission_sha256': sha(output / 'cli-admission.json'),
        'cpu_test_log_sha256': sha(output / 'cpu-tests.log'),
    }
    (output / 'candidate-manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
