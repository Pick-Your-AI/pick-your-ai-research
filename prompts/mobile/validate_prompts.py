"""Validate mobile prompt coverage; optionally compare a fresh read-only GH snapshot.

Run from any directory. --audit-dir expects issues.json, items4.json/items5.json
and fields4.json/fields5.json from paginated GitHub reads, not invented fixtures.
This checks traceability and drift, not product evidence or review acceptance.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

from acceptance_placements import read_json, validate_placements

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent


def sections(body):
    return {m[1]: m[2].strip() for m in re.findall(
        r'(^|\n)## ([^\n]+)\n(.*?)(?=\n## |\Z)', body, re.S)}


def checklist(text):
    return [re.sub(r'^- \[[ xX]\] ', '', line).strip()
            for line in text.splitlines() if line.strip()]


def validate(audit_dir=None):
    records = read_json(ROOT / 'coverage.json')['issues']
    projects = json.loads((ROOT / 'project-fields.json').read_text(encoding='utf-8'))['projects']
    by_issue = {r['issue']: r for r in records}
    by_url = {r['url']: r for r in records}
    assert len(by_issue) == len(records), 'Duplicate issue mappings'
    index = (ROOT / 'INDEX.md').read_text(encoding='utf-8')
    placements = validate_placements(read_json(ROOT / 'acceptance-placements.json'),
                                     records, index)
    for p in projects:
        members = {r['issue'] for r in records if r['project'] == p['project']}
        assert members == set(p['issues']), 'Project coverage mismatch'
        assert by_issue[p['program']]['level'] == 'Program'
        fields = {f['name']: f for f in p['fields']}
        assert len({f['id'] for f in p['fields']}) == len(p['fields'])
        for r in records:
            if r['project'] != p['project']:
                continue
            for key, value in r['project_fields'].items():
                field_name = 'Acceptance Gate' if key == 'acceptance Gate' else key.title()
                assert value in {o['name'] for o in fields[field_name]['options']}
    for r in records:
        n = r['issue']
        assert r['issue'] == f"{r['repository']}#{r['number']}"
        assert r['url'] == f"https://github.com/{r['repository']}/issues/{r['number']}"
        assert index.count(f'id="issue-{r["platform"]}-{r["number"]}"') == 1
        assert r['acceptance_criteria'] and r['validation'] and r['delivery_review_boundary']
        assert r['review_roles'] and r['acceptance_output']
        for field in ['prompt', 'shared', 'launch']:
            assert (ROOT / r[field]).is_file(), (n, field)
        if r['level'] != 'Program':
            parent = by_issue[r['parent']]
            assert n in parent['children'], ('parent mismatch', n)
            assert parent['platform'] == r['platform']
        for child in r['children']:
            assert by_issue[child]['parent'] == n
        if r['level'] == 'Feature':
            assert r['prompt'] == by_issue[r['parent']]['prompt']
            assert r['implementation_steps'], n
            assert r['url'] in (ROOT / r['prompt']).read_text(encoding='utf-8')
        if r['acceptance_path']:
            assert f'`{r["acceptance_path"]}`' in r['delivery_review_boundary']
        else:
            assert r['platform'] == 'apple' and r['placement_decision'].startswith('Pick-Your-AI/pick-your-ai-apple#')
        for url in r['native_prerequisites'] + r['handoff_references']:
            assert re.fullmatch(r'https://github.com/Pick-Your-AI/[\w.-]+/issues/\d+', url), url

    migration = json.loads((ROOT / 'issue-migration.json').read_text(encoding='utf-8'))['issues']
    assert len({m['old_url'] for m in migration}) == len(records)
    assert {m['new_url'] for m in migration} == set(by_url)
    for m in migration:
        r = by_url[m['new_url']]
        assert r['previous_url'] == m['old_url']
        assert r['repository'] == m['repository']
        assert r['number'] == m['new_number']

    # Cycles among covered native prerequisites are invalid; information links are excluded.
    visiting, visited = set(), set()

    def visit(n):
        assert n not in visiting, ('native prerequisite cycle', n)
        if n in visited:
            return
        visiting.add(n)
        for url in by_issue[n]['native_prerequisites']:
            if url in by_url:
                visit(by_url[url]['issue'])
        visiting.remove(n)
        visited.add(n)
    for n in by_issue:
        visit(n)

    for path in ROOT.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if re.match(r'https?://', target):
                continue
            rel, _, anchor = unquote(target).partition('#')
            dest = (path.parent / rel).resolve() if rel else path
            assert dest.is_relative_to(REPO), (path, target)
            assert dest.is_file(), ('broken link', path, target)
            if anchor:
                contents = dest.read_text(encoding='utf-8')
                ids = set(re.findall(r'id="([^"]+)"', contents))
                for heading in re.findall(r'^#+ (.+)$', contents, re.M):
                    ids.add(re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-'))
                assert anchor in ids, ('broken anchor', path, target)

    if audit_dir:
        audit = Path(audit_dir)
        live = {i['url']: i for i in json.loads((audit / 'issues.json').read_text(encoding='utf-8'))}
        for r in records:
            issue = live[r['url']]
            sec = sections(issue['body'])
            body = issue['body']
            for marker in ['mobile-maintainer-prompts', 'mobile-issue-migration']:
                body = re.sub(r'\n*<!-- ' + marker + r':start -->.*?<!-- ' + marker + r':end -->\n?', '', body, flags=re.S)
            assert hashlib.sha256(body.rstrip().encode()).hexdigest() == r['source_body_sha256'], ('source changed; review needed', r['issue'])
            assert checklist(sec['Acceptance criteria']) == r['acceptance_criteria']
            assert checklist(sec.get('Implementation subtasks', '')) == r['implementation_steps']
            assert (by_url[issue['parent']['url']]['issue'] if issue['parent'] else None) == r['parent']
            assert {by_url[i['url']]['issue'] for i in issue['subIssues']['nodes']} == set(r['children'])
            assert {i['url'] for i in issue['blockedBy']['nodes']} == set(r['native_prerequisites'])
            assert [a['login'] for a in issue['assignees']['nodes']] == r['assignees']
            for connection in ['subIssues', 'blockedBy', 'comments']:
                assert issue[connection]['totalCount'] == len(issue[connection]['nodes']), ('paginate', r['number'], connection)
        for p in projects:
            number = p['project']
            items = json.loads((audit / f'items{number}.json').read_text(encoding='utf-8'))
            assert items['totalCount'] == len(items['items'])
            assert {f"{i['content']['repository']}#{i['content']['number']}" for i in items['items']} == set(p['issues'])
            assert json.loads((audit / f'fields{number}.json').read_text(encoding='utf-8'))['fields'] == p['fields']
            for item in items['items']:
                r = by_issue[f"{item['content']['repository']}#{item['content']['number']}"]
                assert all(item.get(k) == v for k, v in r['project_fields'].items())
    print(f'PASS: {len(projects)} Projects, {len(records)} issues, '
          f'{sum(r["level"] == "Epic" for r in records)} epic prompts, '
          f'{sum(len(r["acceptance_criteria"]) for r in records)} criteria, '
          f'{sum(len(r["implementation_steps"]) for r in records)} steps; '
          f'mappings, paths, local links, field vocabulary and prerequisite DAG; '
          f'{placements} accepted placement coordinates')
    if audit_dir:
        print('PASS: exact acceptance/steps, source, ownership, hierarchy, prerequisites and Project snapshot comparison')
    print('Not certified: source truth, rights/freshness, application behavior, devices, store/release state or reviewer acceptance.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir', type=Path)
    validate(parser.parse_args().audit_dir)
