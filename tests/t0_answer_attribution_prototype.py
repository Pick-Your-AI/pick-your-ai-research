"""Explicit CD-1 0.2 source/assumption candidate over existing read mechanics.

Original UTF-8 bytes remain available unchanged. A private 0.1-shaped view
reuses the current pointer/type/policy implementation, never an exported
migration. Neither source names nor assumption flags qualify evidence.
"""

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from tests.t0_answer_state_prototype import (
    Answer, AnswerIndex, AnswerRule, AnswerRuleResult, PredicateResult, State,
    evaluate_answer_rule, finite_float, unique_object,
)


SCHEMA_PATH = Path(__file__).with_name("fixtures") / "t0-answer-attribution.schema.json"
ATTRIBUTION = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
PRESET_SOURCE = Draft202012Validator(ATTRIBUTION.schema["$defs"]["preset_source"])


def _attribution(state, source, assumption):
    """Validate explicit metadata; never derive one field from another."""
    if state is State.PROVIDED:
        if type(assumption) is not bool:
            raise ValueError("provided attribution requires an explicit Boolean assumption")
        if source is not None:
            try:
                PRESET_SOURCE.validate(source)
            except ValidationError as error:
                raise ValueError("source must use the preset:<name> candidate profile") from error
    elif source is not None or assumption is not None:
        raise ValueError("unresolved answers cannot retain provided attribution")


@dataclass(frozen=True, slots=True)
class AttributedAnswer(Answer):
    assumption: bool | None = None

    def __post_init__(self):
        if not isinstance(self.state, State):
            raise ValueError("attributed answer must retain an answer State")
        _attribution(self.state, self.source, self.assumption)


@dataclass(frozen=True, slots=True)
class AttributedPredicate(PredicateResult):
    source: str | None = None
    assumption: bool | None = None

    def __post_init__(self):
        PredicateResult.__post_init__(self)
        _attribution(self.state, self.source, self.assumption)

    def negated(self):
        result = PredicateResult.negated(self)
        return AttributedPredicate(result.state, result._value, result.source_path,
                                   self.source, self.assumption)


@dataclass(frozen=True, slots=True)
class AttributedRuleResult:
    """Terminal rule finding plus its actual causal answer's attribution."""

    finding: AnswerRuleResult
    source: str | None
    assumption: bool | None

    def __bool__(self):
        raise TypeError("attributed rule results have no implicit Boolean value; inspect finding.outcome")


class AttributedAnswerIndex:
    """Read only explicit cd1-0.2 bytes; existing cd1-0.1 callers stay separate."""

    def __init__(self, raw):
        if type(raw) is not bytes:
            raise ValueError("CD-1 attribution inputs must be original UTF-8 bytes")
        try:
            # Apply the accepted numeric profile to the original tokens, before
            # building the private reader view can conceal a rounded value.
            document = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                                  parse_float=finite_float)
            json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (UnicodeError, ValueError) as error:
            raise ValueError("invalid attribution JSON") from error
        try:
            ATTRIBUTION.validate(document)
        except ValidationError as error:
            raise ValueError("invalid CD-1 0.2 attribution: " + error.message) from error
        self._raw = raw
        self._records = deepcopy(document["x_t0_answer_states"]["answers"])
        # Reuse pointer traversal, field validation and unresolved-state policy
        # only after strict 0.2 admission. No projected bytes are published or
        # used as the identity of the original candidate.
        view = deepcopy(document)
        view["x_t0_answer_states"]["proposal_version"] = "cd1-0.1"
        for record in view["x_t0_answer_states"]["answers"].values():
            record.pop("assumption", None)
        self._reader = AnswerIndex(json.dumps(view, ensure_ascii=False, allow_nan=False))

    @property
    def original_bytes(self):
        return self._raw

    def read(self, pointer, value_schema):
        answer = self._reader.read(pointer, value_schema)
        # Only a provided value inherits its actual recorded ancestor's flag.
        # An absent member or unresolved child has no provided attribution.
        assumption = (self._records[answer.source_path]["assumption"]
                      if answer.provided else None)
        return AttributedAnswer(answer.state, answer.value, answer.source,
                                answer.source_path, assumption)

    def predicate(self, pointer, value_schema, predicate):
        answer = self.read(pointer, value_schema)
        result = predicate(answer.value) if answer.provided else None
        return AttributedPredicate(answer.state, result, answer.source_path,
                                   answer.source, answer.assumption)


def evaluate_attributed_rule(rule):
    """Keep explicit attribution alongside the unchanged typed policy result.

    Lazy callbacks run only through the existing terminal evaluator. The
    metadata comes from the predicate responsible for that exact outcome,
    without fetching an unevaluated assertion or qualifying source evidence.
    """
    if not isinstance(rule, AnswerRule):
        raise ValueError("expected a typed answer rule")
    observed = {}

    def capture(position, callback):
        def execute():
            result = callback()
            if not isinstance(result, AttributedPredicate):
                raise ValueError("attributed rules require AttributedPredicate callbacks")
            observed[position] = result
            return result
        return execute

    finding = evaluate_answer_rule(AnswerRule(
        rule.id, rule.severity, rule.policy,
        capture("applies_when", rule.applies_when), capture("assertion", rule.assertion),
    ))
    cause = observed[finding.position]
    return AttributedRuleResult(finding, cause.source, cause.assumption)
