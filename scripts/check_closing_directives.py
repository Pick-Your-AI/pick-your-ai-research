"""Conservative, offline pre-merge text check; not GitHub's Markdown parser."""
import argparse
from pathlib import Path
import re

KEYWORD = r"(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)"
TARGET = r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#[1-9][0-9]*|https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*"
CANDIDATE = re.compile(rf"\b{KEYWORD}\b[\s:*`_]*(?P<target>{TARGET})", re.I)
EXPLICIT = re.compile(rf"{KEYWORD}:?\s+(?P<target>{TARGET})", re.I)


def check_text(text, allowed=()):
    """Allow only standalone directives for individually reviewed target strings.

    Scan raw text, including quotes/code, so negation and ranges cannot silently
    excuse a directive. False positives should be rewritten using Refs.
    """
    allowed = set(allowed)
    errors = []
    for match in CANDIDATE.finditer(text):
        start = text.rfind('\n', 0, match.start()) + 1
        end = text.find('\n', match.end())
        line = text[start:end if end >= 0 else len(text)].strip()
        explicit = EXPLICIT.fullmatch(line)
        if explicit is None or explicit.group('target') not in allowed:
            errors.append((text.count('\n', 0, match.start()) + 1, match.group('target')))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path, help='fresh PR body or commit-message text files')
    parser.add_argument('--allow', action='append', default=[], metavar='TARGET',
                        help='exact target whose full acceptance and closure were reviewed; repeat per target')
    args = parser.parse_args(argv)
    failed = False
    for path in args.files:
        for line, target in check_text(path.read_text(encoding='utf-8'), args.allow):
            print(f'{path}:{line}: review closing directive for {target}; use Refs for partial work')
            failed = True
    if not failed:
        print('Text check passed; independently inspect live linked issues and acceptance before merge.')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
