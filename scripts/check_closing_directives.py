"""Conservative, offline pre-merge text check; not GitHub's Markdown parser."""
import argparse
from pathlib import Path
import re

KEYWORD = r"(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)"
TARGET = r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#[1-9][0-9]*|https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*"
CANDIDATE = re.compile(rf"(?<![A-Za-z0-9]){KEYWORD}(?![A-Za-z0-9])[\s:*`_\[<]*(?P<target>{TARGET})", re.I)
EXPLICIT = re.compile(rf"{KEYWORD}:?\s+(?P<target>{TARGET})", re.I)
FENCE = re.compile(r" {0,3}(?P<marker>`{3,}|~{3,})(?P<tail>.*)$")


def fenced_lines(text):
    """Track top-level Markdown fences across paragraph boundaries.

    This is deliberately not a full Markdown parser. Indented/container content
    cannot be allowlisted because intentional directives must be unindented.
    """
    protected = set()
    active = None
    for number, line in enumerate(text.splitlines(), 1):
        fence = FENCE.fullmatch(line)
        if active is not None:
            protected.add(number)
            if (fence is not None
                    and fence.group('marker')[0] == active[0]
                    and len(fence.group('marker')) >= len(active)
                    and not fence.group('tail').strip()):
                active = None
        elif fence is not None:
            marker, tail = fence.group('marker', 'tail')
            # Backticks are forbidden in a backtick fence's info string.
            if marker[0] == '~' or '`' not in tail:
                protected.add(number)
                active = marker
    return protected


def check_text(text, allowed=()):
    """Allow only standalone directives for individually reviewed target strings.

    Scan raw text, including quotes/code, so negation and ranges cannot silently
    excuse a directive. False positives should be rewritten using Refs.
    """
    allowed = set(allowed)
    protected = fenced_lines(text)
    errors = []
    offset = 0
    for paragraph in re.split(r"\n[ \t]*\n", text):
        start = text.find(paragraph, offset)
        offset = start + len(paragraph)
        first_line = text.count('\n', 0, start) + 1
        directives = [EXPLICIT.fullmatch(line.rstrip()) for line in paragraph.splitlines()]
        intentional = bool(directives) and all(
            directive is not None and directive.group('target') in allowed
            and first_line + index not in protected
            for index, directive in enumerate(directives)
        )
        if not intentional:
            for match in CANDIDATE.finditer(paragraph):
                line = text.count('\n', 0, start + match.start()) + 1
                errors.append((line, match.group('target')))
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
