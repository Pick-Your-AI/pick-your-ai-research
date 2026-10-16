#!/usr/bin/env python3
"""Validate the local issue-prompt package; no network or third-party dependencies.

This checks coverage and captured instruction structure, not live GitHub state,
claim accuracy, human acceptance, legal rights, repository CI or research completion.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

EXPECTED = set(range(47, 67))
SECTIONS = (
    '## Mission and invocation',
    '## Scope and writable deliverables',
    '## Starting context to verify',
    '## Orchestrated execution',
    '## Dependencies and handoffs',
    '## Acceptance criteria to preserve',
    '## Commit, push, sync and merge this issue',
    '## Required final report',
)

def check(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [f'Cannot load manifest: {exc}']
    entries = manifest.get('issues', [])
    ids = [entry.get('issue') for entry in entries]
    if len(ids) != len(EXPECTED) or set(ids) != EXPECTED:
        errors.append('Manifest must contain exactly one issue for each ID 47 through 66.')
    expected_files = {f'issue-{number:03d}.md' for number in EXPECTED}
    actual_files = {path.name for path in root.glob('issue-*.md')}
    if actual_files != expected_files:
        errors.append(f'Prompt coverage mismatch: missing={expected_files-actual_files}, extra={actual_files-expected_files}')
    parent_map = {n:47 for n in range(48,60)} | {47:None,60:55,61:56,62:56,63:52,64:54,65:56,66:50}
    by_id = {e['issue']:e for e in entries if e.get('issue') in EXPECTED}
    for entry in entries:
        number=entry.get('issue')
        if number not in EXPECTED:
            continue
        prompt=root / entry['prompt']
        try:
            text=prompt.read_text(encoding='utf-8')
        except OSError as exc:
            errors.append(f'{prompt.name}: {exc}')
            continue
        if not text.startswith(f"# Issue #{number} — {entry['title']}\n"):
            errors.append(f'{prompt.name}: heading does not match the captured issue.')
        for section in SECTIONS:
            if text.count(section) != 1:
                errors.append(f'{prompt.name}: expected exactly one {section}')
        if entry.get('parent') != parent_map[number]:
            errors.append(f'{prompt.name}: captured parent relationship mismatch.')
        for criterion in entry.get('criteria', []):
            if '- [ ] ' + criterion not in text:
                errors.append(f'{prompt.name}: omitted captured criterion: {criterion}')
        for path in entry.get('files', []):
            if f'`{path}`' not in text:
                errors.append(f'{prompt.name}: omitted deliverable {path}')
        for token in [f'Refs #{number}',f'Closes #{number}','SHARED.md','head-SHA guard','canonical-main','ZIP/diff']:
            if token not in text:
                errors.append(f'{prompt.name}: missing delivery safeguard {token}')
        if text.count('```') % 2:
            errors.append(f'{prompt.name}: unbalanced fenced blocks.')
    for number,entry in by_id.items():
        expected_children=sorted(n for n,p in parent_map.items() if p==number)
        if sorted(entry.get('children', [])) != expected_children:
            errors.append(f'#{number}: native children do not match parent map.')
        expected_blocked=[66] if number in (57,58) else []
        if entry.get('blocked_by') != expected_blocked:
            errors.append(f'#{number}: unexpected native prerequisite.')
        expected_blocks=[57,58] if number==66 else []
        if entry.get('blocks') != expected_blocks:
            errors.append(f'#{number}: unexpected native downstream blocking relation.')
    for path in root.glob('*.md'):
        text=path.read_text(encoding='utf-8')
        if not text.endswith('\n'):
            errors.append(f'{path.name}: missing final newline.')
        if '\r' in text:
            errors.append(f'{path.name}: unexpected carriage return.')
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in link or link.startswith(('#','mailto:')):
                continue
            target=(path.parent / link.split('#',1)[0]).resolve()
            if not target.is_file():
                errors.append(f'{path.name}: missing local link target {link}')
    shared=(root/'SHARED.md').read_text(encoding='utf-8')
    for phrase in ('#66 → #57','#66 → #58','spare-local-capacity-only'):
        if phrase not in shared:
            errors.append(f'SHARED.md: missing critical guard {phrase}')
    return errors

def main() -> int:
    root=Path(__file__).resolve().parent
    errors=check(root)
    if errors:
        for message in errors:
            print(f'FAIL: {message}',file=sys.stderr)
        return 1
    print('PASS: exactly 20 issue prompts (#47–#66).')
    print('PASS: issue headings, required sections, captured criteria and deliverable paths.')
    print('PASS: 19 parent/child relationships and only #66 → #57/#58 native blockers.')
    print('PASS: commit/push/sync/review/merge safeguards and local Markdown links.')
    print('NOT CHECKED: live GitHub state, repository research tests/CI, evidence truth or owner acceptance.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
