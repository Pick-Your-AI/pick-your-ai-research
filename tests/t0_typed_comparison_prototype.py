"""Synthetic typed-comparison/0.1 semantics; no application or replay dispatch.

The only input API is compare(profile, operator, left_json, right_json). Operands
are original UTF-8 bytes; Python None is unresolved and b"null" is known JSON null.
This deliberately versioned experiment does not modify the frozen interpreter.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
import json
import re


PROFILE = "typed-comparison/0.1"
MAX_BYTES = 65_536
MAX_DEPTH = 32
MAX_NODES = 10_000
MAX_STRING_CHARS = 4_096
MAX_NUMBER_CHARS = 128
MAX_ABS_EXPONENT = 1_000
MAX_WORK = 200_000
OPERATORS = frozenset(("eq", "ne", "lt", "lte", "gt", "gte", "in", "contains", "intersects", "subset_of"))
_DECIMAL_STRING = re.compile(r"(0|[1-9][0-9]*)(\.[0-9]{1,12})?", re.ASCII)
_UNRESOLVED = object()


class ComparisonError(ValueError):
    """Whole-attempt rejection with a fixed reason, never rejected input text."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


class Outcome(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Limits:
    """Resource ceilings of this profile; experiments can only reduce them."""

    max_bytes: int = MAX_BYTES
    max_depth: int = MAX_DEPTH
    max_nodes: int = MAX_NODES
    max_string_chars: int = MAX_STRING_CHARS
    max_number_chars: int = MAX_NUMBER_CHARS
    max_abs_exponent: int = MAX_ABS_EXPONENT
    max_work: int = MAX_WORK

    def __post_init__(self):
        caps = (("max_bytes", MAX_BYTES), ("max_depth", MAX_DEPTH),
                ("max_nodes", MAX_NODES), ("max_string_chars", MAX_STRING_CHARS),
                ("max_number_chars", MAX_NUMBER_CHARS),
                ("max_abs_exponent", MAX_ABS_EXPONENT), ("max_work", MAX_WORK))
        for name, cap in caps:
            value = getattr(self, name)
            minimum = 0 if name == "max_abs_exponent" else 1
            if type(value) is not int or not minimum <= value <= cap:
                raise ComparisonError("invalid_limits")


class _Work:
    def __init__(self, maximum):
        self.remaining = maximum

    def charge(self, amount=1):
        self.remaining -= amount
        if self.remaining < 0:
            raise ComparisonError("work_limit")


def _nesting(text, maximum):
    # Guard parser recursion before json.loads, ignoring braces inside strings.
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > maximum:
                raise ComparisonError("depth_limit")
        elif char in "]}":
            depth -= 1


def _number(token, limits):
    if len(token) > limits.max_number_chars:
        raise ComparisonError("number_limit")
    exponent = re.search(r"[eE]([+-]?[0-9]+)$", token)
    if exponent and abs(int(exponent.group(1))) > limits.max_abs_exponent:
        raise ComparisonError("number_limit")
    try:
        value = Decimal(token)
    except InvalidOperation:
        raise ComparisonError("number_limit") from None
    if not value.is_finite():
        raise ComparisonError("non_finite")
    if abs(value.as_tuple().exponent) > limits.max_abs_exponent:
        raise ComparisonError("number_limit")
    return value


def _text(value, limits, work):
    if len(value) > limits.max_string_chars:
        raise ComparisonError("string_limit")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise ComparisonError("invalid_unicode")
    work.charge(len(value))


def _read(raw, limits, work):
    if raw is None:
        return _UNRESOLVED
    if type(raw) is not bytes:
        raise ComparisonError("operand_bytes_required")
    if len(raw) > limits.max_bytes:
        raise ComparisonError("byte_limit")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeError:
        raise ComparisonError("invalid_utf8") from None
    work.charge(len(text))  # Reserve original-text scanning, including escapes/whitespace.
    _nesting(text, limits.max_depth)

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ComparisonError("duplicate_key")
            result[key] = value
        return result

    def integer(token):
        _number(token, limits)
        return int(token)

    def constant(_token):
        raise ComparisonError("non_finite")

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_int=integer,
                           parse_float=lambda token: _number(token, limits),
                           parse_constant=constant)
    except (json.JSONDecodeError, RecursionError):
        raise ComparisonError("invalid_json") from None

    # Validate every supplied member before any semantic shortcut. Object keys
    # count as nodes too. Container nesting, not string contents, defines depth.
    pending, nodes = [(value, 0)], 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        if nodes > limits.max_nodes:
            raise ComparisonError("node_limit")
        work.charge()
        if type(item) in (list, dict):
            if depth + 1 > limits.max_depth:
                raise ComparisonError("depth_limit")
            if type(item) is dict:
                for key, child in item.items():
                    nodes += 1
                    if nodes > limits.max_nodes:
                        raise ComparisonError("node_limit")
                    work.charge()
                    _text(key, limits, work)
                    pending.append((child, depth + 1))
            else:
                pending.extend((child, depth + 1) for child in item)
        elif type(item) is str:
            _text(item, limits, work)
            if _DECIMAL_STRING.fullmatch(item):
                _number(item, limits)
        elif type(item) is int:
            work.charge(len(str(item)))
        elif type(item) is Decimal:
            work.charge(len(item.as_tuple().digits) + len(str(item.as_tuple().exponent)))
        elif item is not None and type(item) is not bool:
            raise ComparisonError("unsupported_value")
    return value


def _truth(value):
    return Outcome.TRUE if value else Outcome.FALSE


def _all(values):
    result = Outcome.TRUE
    for value in values:
        if value is Outcome.FALSE:
            result = Outcome.FALSE
        elif value is Outcome.UNKNOWN and result is Outcome.TRUE:
            result = Outcome.UNKNOWN
    return result


def _any(values):
    result = Outcome.FALSE
    for value in values:
        if value is Outcome.TRUE:
            result = Outcome.TRUE
        elif value is Outcome.UNKNOWN and result is Outcome.FALSE:
            result = Outcome.UNKNOWN
    return result


class _Comparison:
    def __init__(self, work):
        self.work = work

    def numeric(self, value):
        if type(value) is int:
            self.work.charge(len(str(value)))
            return Decimal(value)
        if type(value) is Decimal:
            self.work.charge(len(value.as_tuple().digits) + len(str(value.as_tuple().exponent)))
            return value
        if type(value) is str:
            self.work.charge(len(value))
            if _DECIMAL_STRING.fullmatch(value):
                return Decimal(value)
        return None  # Boolean is intentionally never an integer here.

    def scalar_equal(self, left, right):
        self.work.charge()
        a, b = self.numeric(left), self.numeric(right)
        if a is not None or b is not None:
            return _truth(a == b) if a is not None and b is not None else Outcome.UNKNOWN
        if type(left) is not type(right):
            return Outcome.UNKNOWN
        if left is None or type(left) in (bool, str):
            return _truth(left == right)
        return Outcome.UNKNOWN  # Direct eq/ne do not admit containers.

    def element_equal(self, left, right):
        self.work.charge()
        if type(left) is list and type(right) is list:
            if len(left) != len(right):
                return Outcome.FALSE
            return _all(self.element_equal(a, b) for a, b in zip(left, right))
        if type(left) is dict and type(right) is dict:
            self.work.charge(sum(len(key) + 1 for key in left) + sum(len(key) + 1 for key in right))
            if left.keys() != right.keys():
                return Outcome.FALSE
            return _all(self.element_equal(left[key], right[key]) for key in sorted(left))
        return self.scalar_equal(left, right)

    def contains(self, container, item):
        self.work.charge()
        if type(container) is list:
            return _any(self.element_equal(value, item) for value in container)
        if type(container) is str and type(item) is str:
            self.work.charge((len(container) + 1) * (len(item) + 1))
            return _truth(item in container)
        return Outcome.UNKNOWN

    def compare(self, operator, left, right):
        if left is _UNRESOLVED or right is _UNRESOLVED:
            return Outcome.UNKNOWN
        if operator in ("eq", "ne"):
            value = self.scalar_equal(left, right)
            if operator == "ne" and value is not Outcome.UNKNOWN:
                return Outcome.FALSE if value is Outcome.TRUE else Outcome.TRUE
            return value
        if operator in ("lt", "lte", "gt", "gte"):
            a, b = self.numeric(left), self.numeric(right)
            if a is None or b is None:
                return Outcome.UNKNOWN
            if operator == "lt":
                return _truth(a < b)
            if operator == "lte":
                return _truth(a <= b)
            if operator == "gt":
                return _truth(a > b)
            return _truth(a >= b)
        if operator == "contains":
            return self.contains(left, right)
        if operator == "in":
            return self.contains(right, left)
        if type(left) is not list or type(right) is not list:
            return Outcome.UNKNOWN
        if operator == "intersects":
            return _any(self.contains(right, item) for item in left)
        return _all(self.contains(right, item) for item in left)


def compare(profile, operator, left_json, right_json, *, limits=Limits()):
    """Return TRUE/FALSE/UNKNOWN, or reject the whole original-byte attempt.

    Both operands are fully admitted before unresolved, shape or empty-list
    outcomes. No decoded host object, floating-point value or profile fallback is
    accepted. Comparison traversal also consumes the same bounded work allowance.
    """
    if type(profile) is not str or profile != PROFILE:
        raise ComparisonError("unsupported_profile")
    if type(operator) is not str or operator not in OPERATORS:
        raise ComparisonError("unsupported_operator")
    if type(limits) is not Limits:
        raise ComparisonError("invalid_limits")
    limits.__post_init__()
    work = _Work(limits.max_work)
    left = _read(left_json, limits, work)
    right = _read(right_json, limits, work)
    return _Comparison(work).compare(operator, left, right)
