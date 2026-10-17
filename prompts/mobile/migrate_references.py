"""Apply the recorded issue transfer map without confusing repository namespaces.

This does not create or transfer issues. Original snapshot records and immutable
publication links remain historical evidence. Call rewrite only on mutable text.
"""
import json
import re
from pathlib import Path


def rewrite(text, mapping, qualify_bare=False):
    by_number = {m['old_number']: m for m in mapping}

    def ref(number):
        m = by_number.get(int(number))
        return (f"{m['repository']}#{m['new_number']}" if m
                else f'Pick-Your-AI/pickyour.ai#{number}')

    def url(value):
        return re.sub(r'https://github\.com/Pick-Your-AI/pickyour\.ai/issues/(\d+)\b',
                      lambda m: by_number[int(m[1])]['new_url']
                      if int(m[1]) in by_number else m[0], value)

    # Linked labels inherit the linked repository, never the containing issue.
    links = []
    def protect(match):
        label, target = match[1], match[2]
        target = url(target)
        linked = re.fullmatch(r'https://github\.com/(Pick-Your-AI/[\w.-]+)/issues/(\d+)(?:[?#].*)?', target)
        if linked:
            label = (f'{linked[1]}#{linked[2]}' if label.isdigit() else
                     re.sub(r'(?:Pick-Your-AI/[\w.-]+)?#\d+',
                            f'{linked[1]}#{linked[2]}', label))
        links.append(f'[{label}]({target})')
        return f'@@MOBILELINK{len(links)-1}@@'
    text = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', protect, text)

    # Older generated prose sometimes qualified a research shorthand as website.
    text = re.sub(r'(?i)(research\s+)((?:(?:Pick-Your-AI/pickyour\.ai)?#\d+)(?:[/, ]+#\d+)*)',
                  lambda m: m[1] + re.sub(r'(?:Pick-Your-AI/pickyour\.ai)?#(\d+)',
                                         r'Pick-Your-AI/pick-your-ai-research#\1', m[2]), text)
    text = re.sub(r'Pick-Your-AI/pickyour\.ai#(\d+)\b', lambda m: ref(m[1]), text)
    text = url(text)
    if qualify_bare:
        text = re.sub(r'(?<![\w/#])#(\d+)\b',
                      lambda m: m[0] if re.search(r'(?i)project\s+$', text[max(0,m.start()-12):m.start()])
                      else ref(m[1]), text)
    text = re.sub(r'@@MOBILELINK(\d+)@@',lambda m: links[int(m[1])],text)
    return text


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    mapping = json.loads(Path(__file__).with_name('issue-migration.json').read_text(encoding='utf-8'))['issues']
    result = rewrite(args.path.read_text(encoding='utf-8'), mapping)
    if args.write:
        args.path.write_text(result, encoding='utf-8', newline='\n')
    else:
        print(result)
