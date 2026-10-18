"""Synthetic CD-1 encoding/normalization; not a released contract reader.

An explicit answer state is separate from its value, field type and rule policy.
Callers supply the field's reviewed local schema before using a provided value.
This module reads a test-only sidecar; it never rewrites historical build bytes,
resolves catalog evidence or chooses which selections a rule covers.
The typed terminal rule boundary retains explicit answer policy and reasons.
"""

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
import json
import math
from pathlib import Path
import re
from typing import assert_never

from jsonschema import Draft202012Validator, ValidationError

from tests.selection_quantifier_prototype import Outcome
from tests.t0_known_value_schema import known_value_validator


SCHEMA_PATH = Path(__file__).with_name("fixtures") / "t0-answer-states.schema.json"
ENCODING = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


class State(StrEnum):
    PROVIDED = "provided"
    UNKNOWN = "unknown"
    MISSING = "missing"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class Answer:
    state: State
    value: object = None
    source: str | None = None
    source_path: str | None = None

    @property
    def provided(self):
        return self.state is State.PROVIDED


@dataclass(frozen=True, slots=True)
class PredicateResult:
    """A predicate fact that cannot become true through Python truthiness.

    Compose negation before lowering. The two value adapters are only for the
    final normalized-rule boundary, whose bool/None interface is unchanged.
    They are not intermediate values for Python ``not``, ``and`` or ``or``.
    """

    state: State
    _value: bool | None
    source_path: str | None = None

    def __post_init__(self):
        if not isinstance(self.state, State):
            raise ValueError("predicate result must retain an answer State")
        if self._value is not True and self._value is not False and self._value is not None:
            raise ValueError("predicate must return a normalized bool or None")
        if self.state is not State.PROVIDED and self._value is not None:
            raise ValueError("unresolved answer cannot retain a predicate value")

    def __bool__(self):
        raise TypeError(
            "CD-1 predicate results have no implicit Boolean value; "
            "use negated() and a final rule adapter"
        )

    def negated(self):
        """Invert only a known Boolean, retaining unresolved state and path."""
        value = None if self._value is None else not self._value
        return PredicateResult(self.state, value, self.source_path)

    def compatibility_value(self):
        """Lower once at the rule boundary; unresolved input stays None."""
        return self._value

    def recommendation_value(self):
        """Apply the existing known-answer gate before final rule lowering.

        An unresolved answer skips a recommendation. A provided answer whose
        value predicate is unresolved still returns None, not a default false.
        """
        return self._value if self.state is State.PROVIDED else False


class RulePolicy(StrEnum):
    """The caller's explicit policy for an unresolved applicability answer."""

    COMPATIBILITY = "compatibility"
    RECOMMENDATION = "recommendation"


@dataclass(frozen=True, slots=True)
class AnswerRule:
    """One fixed-severity rule over caller-selected, typed answer predicates."""

    id: str
    severity: str
    policy: RulePolicy
    applies_when: Callable[[], PredicateResult]
    assertion: Callable[[], PredicateResult]

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("answer rule must have a nonempty id")
        if not isinstance(self.severity, str) or self.severity not in {"info", "warning", "error"}:
            raise ValueError("answer rule must have one fixed severity")
        if not isinstance(self.policy, RulePolicy):
            raise ValueError("answer rule must declare a typed rule policy")
        if not callable(self.applies_when) or not callable(self.assertion):
            raise ValueError("answer rule predicates must be lazy callables")


@dataclass(frozen=True, slots=True)
class AnswerRuleResult:
    """A terminal finding, retaining the answer responsible for its outcome.

    This is not a selection aggregate, wire report or evidence qualification.
    No original answer value is copied into the result.
    """

    rule_id: str
    severity: str
    outcome: Outcome
    reason: str
    position: str
    answer_state: State
    source_path: str | None

    def __bool__(self):
        raise TypeError("answer rule results have no implicit Boolean value; inspect outcome")


_ANSWER_REASONS = {
    State.WITHHELD: "answer_withheld",
    State.UNKNOWN: "answer_unknown",
    State.MISSING: "answer_missing",
    State.NOT_APPLICABLE: "answer_not_applicable",
}


def evaluate_answer_rule(rule: AnswerRule) -> AnswerRuleResult:
    """Evaluate one typed rule without losing answer-state policy or reasons.

    Recommendations skip an unresolved *applicability answer*. Once known
    applicability is true, an unresolved assertion remains unknown. An explicit
    not-applicable answer skips its dependent predicate at either position.
    A provided answer with unresolved predicate evidence is never defaulted.
    """
    if not isinstance(rule, AnswerRule):
        raise ValueError("expected a typed answer rule")

    def checked(callback):
        result = callback()
        if not isinstance(result, PredicateResult):
            raise ValueError("answer rule predicates must return PredicateResult")
        return result

    def finish(predicate, position, outcome, reason):
        return AnswerRuleResult(
            rule.id, rule.severity, outcome, reason, position,
            predicate.state, predicate.source_path,
        )

    applicable = checked(rule.applies_when)
    if applicable.state is State.NOT_APPLICABLE:
        return finish(applicable, "applies_when", Outcome.SKIPPED,
                      _ANSWER_REASONS[applicable.state])
    if applicable.state is not State.PROVIDED:
        outcome = (Outcome.SKIPPED if rule.policy is RulePolicy.RECOMMENDATION
                   else Outcome.UNKNOWN)
        return finish(applicable, "applies_when", outcome,
                      _ANSWER_REASONS[applicable.state])
    if applicable._value is None:
        return finish(applicable, "applies_when", Outcome.UNKNOWN, "predicate_unknown")
    if applicable._value is False:
        return finish(applicable, "applies_when", Outcome.SKIPPED, "applicability_false")

    assertion = checked(rule.assertion)
    if assertion.state is State.NOT_APPLICABLE:
        return finish(assertion, "assertion", Outcome.SKIPPED,
                      _ANSWER_REASONS[assertion.state])
    if assertion.state is not State.PROVIDED:
        return finish(assertion, "assertion", Outcome.UNKNOWN,
                      _ANSWER_REASONS[assertion.state])
    if assertion._value is None:
        return finish(assertion, "assertion", Outcome.UNKNOWN, "predicate_unknown")
    if assertion._value is False:
        return finish(assertion, "assertion", Outcome.FAIL, "assertion_false")
    return finish(assertion, "assertion", Outcome.PASS, "assertion_true")


def pointer_tokens(pointer):
    """Non-root RFC 6901 string form; never dotted paths or URI fragments."""
    if not isinstance(pointer, str) or re.fullmatch(r"(?:/(?:[^~/]|~[01])*)+", pointer) is None:
        raise ValueError("answer path must be a non-root JSON Pointer")
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in pointer.split("/")[1:])


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate answer JSON key: {key!r}")
        result[key] = value
    return result


def finite_float(token):
    """Keep the existing float API only for the supported decimal precision."""
    number = float(token)
    if not math.isfinite(number):
        raise ValueError("non-finite CD-1 answer number")
    try:
        original = Decimal(token)
    except InvalidOperation as error:
        raise ValueError("unsupported CD-1 numeric precision") from error
    # Ordinary decimal fields retain floats (for example, 0.1), but their
    # shortest decimal readback must denote the original token's value.
    # Whole-valued floats must additionally retain the exact integer: 1e23
    # prints as 1e+23 despite representing a different integral value.
    if (not original.is_finite() or original != Decimal(str(number)) or
            (number.is_integer() and original != int(number))):
        raise ValueError("unsupported CD-1 numeric precision")
    return number


class AnswerIndex:
    def __init__(self, raw):
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        document = json.loads(raw, object_pairs_hook=unique_object, parse_float=finite_float)
        # Reject accepted-by-Python NaN/Infinity and overflowing JSON numbers.
        json.dumps(document, allow_nan=False)
        try:
            ENCODING.validate(document)
        except ValidationError as error:
            raise ValueError(f"invalid CD-1 answer encoding: {error.message}") from error
        answers = document["x_t0_answer_states"]["answers"]
        self._answers = {
            pointer_tokens(path): (path, deepcopy(answer))
            for path, answer in answers.items()
        }
        for tokens in self._answers:
            if any(tokens[:length] in self._answers for length in range(1, len(tokens))):
                raise ValueError("overlapping parent/child answer paths")
        self._withheld_ancestors: dict[tuple[str, ...], str] = {}
        for child, (path, record) in sorted(self._answers.items(), key=lambda item: item[1][0]):
            match State(record["state"]):
                case State.WITHHELD:
                    for length in range(1, len(child)):
                        self._withheld_ancestors.setdefault(child[:length], path)
                case State.PROVIDED | State.UNKNOWN | State.MISSING | State.NOT_APPLICABLE:
                    continue
                case unreachable:
                    assert_never(unreachable)

    def read(self, pointer, value_schema):
        """Read a typed fact, preserving unresolved state and source attribution.

        A withheld/unresolved parent covers its descendants. A provided parent
        can supply a nested value; absent members/indices are missing. Invalid
        array syntax or scalar traversal is an input error, never a known false.
        The schema describes the requested field, not the whole parent value.
        """
        tokens = pointer_tokens(pointer)
        for length in range(len(tokens), 0, -1):
            match = self._answers.get(tokens[:length])
            if match is not None:
                break
        else:
            source_path = self._withheld_ancestors.get(tokens)
            if source_path is not None:
                return Answer(State.WITHHELD, source_path=source_path)
            return Answer(State.MISSING)
        source_path, record = match
        state = State(record["state"])
        if state is not State.PROVIDED:
            return Answer(state, source_path=source_path)
        value = record["value"]
        for token in tokens[length:]:
            if isinstance(value, dict):
                if token not in value:
                    return Answer(State.MISSING, source_path=source_path)
                value = value[token]
            elif isinstance(value, list):
                if re.fullmatch(r"0|[1-9][0-9]*", token) is None:
                    raise ValueError("invalid answer array index")
                index = int(token)
                if index >= len(value):
                    return Answer(State.MISSING, source_path=source_path)
                value = value[index]
            else:
                raise ValueError("cannot traverse a scalar answer")
        validator = known_value_validator(value_schema)
        try:
            validator.validate(value)
        except ValidationError as error:
            raise ValueError(f"invalid provided value at {pointer}: {error.message}") from error
        except RecursionError as error:
            raise ValueError("invalid known-value schema: recursive application did not resolve") from error
        return Answer(state, deepcopy(value), record.get("source"), source_path)

    def predicate(self, pointer, value_schema, predicate) -> PredicateResult:
        """Evaluate provided, field-valid data without implicit truth coercion."""
        answer = self.read(pointer, value_schema)
        if not answer.provided:
            return PredicateResult(answer.state, None, answer.source_path)
        result = predicate(answer.value)
        return PredicateResult(answer.state, result, answer.source_path)
