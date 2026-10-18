"""Typed CD-11 research input bound to CD-1 bytes and an exact normalized route.

All scope/evidence facts are synthetic or already normalized by the caller.
This does not derive active scope from a build, authenticate a source, count
tokens, select a route, resolve extension evidence or migrate a frozen record.
"""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from tests.context_budget_prototype import (
    Budget, Check, Outcome, Semantics, TokenRange, combine, evaluate,
)
from tests.t0_answer_state_prototype import Answer, AnswerIndex, State, unique_object


SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "context-budget-binding.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(SCHEMA)
SCOPE = Draft202012Validator({"$ref": "#/$defs/scope", "$defs": SCHEMA["$defs"]})
INTEGER = {"type": "integer", "minimum": 0}
INPUT_RANGE = {
    "type": "object", "required": ["lower", "upper"], "additionalProperties": False,
    "properties": {"lower": {"type": "integer", "minimum": 1},
                   "upper": {"type": "integer", "minimum": 1}},
}
FIELDS = {
    "semantics": {"enum": ["shared", "separate"]},
    "input_tokens": INPUT_RANGE,
    "reserved_output_tokens": INTEGER,
    "output_cap_tokens": INTEGER,
    "shared_cap_tokens": {"type": "integer", "minimum": 1},
    "input_cap_tokens": {"type": "integer", "minimum": 1},
    "policy_total_cap_tokens": INTEGER,
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError("CD-11 retained inputs must be UTF-8 bytes")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    json.dumps(value, allow_nan=False)
    return value


def validate(validator, value, label):
    try:
        validator.validate(value)
    except ValidationError as error:
        raise ValueError(f"invalid {label}: {error.message}") from error


@dataclass(frozen=True)
class BoundResult:
    outcome: Outcome
    may_not_fit: bool
    reason: str
    checks: tuple[Check, ...]
    answers: tuple[tuple[str, Answer], ...]


class ContextRecord:
    """Choose explicit route-scoped caps; never merge another route's limits.

    Unknown states are retained independently of numeric values. A caller must
    establish active selection/route/tokenizer/config identity and evidence
    eligibility separately; equality of labels or digests cannot certify that.
    """

    def __init__(self, proposal_raw, answers_raw):
        proposal = decode(proposal_raw)
        validate(WIRE, proposal, "CD-11 encoding")
        value = proposal["x_t0_context_budget"]
        if type(answers_raw) is not bytes or digest(answers_raw) != value["answer_states_sha256"]:
            raise ValueError("answer bytes do not match the declared context binding")
        index = AnswerIndex(answers_raw)
        answers = {name: index.read("/context/" + name, schema)
                   for name, schema in FIELDS.items()}
        # JSON Schema's mathematical integer includes 1.0. This wire candidate
        # requires JSON integer tokens for every count, without coercion.
        for name, answer in answers.items():
            if not answer.provided or name == "semantics":
                continue
            values = answer.value.values() if name == "input_tokens" else (answer.value,)
            if any(type(number) is not int for number in values):
                raise ValueError("context token counts require exact JSON integers")
        counts = answers["input_tokens"]
        if counts.provided and counts.value["lower"] > counts.value["upper"]:
            raise ValueError("input count bounds must be ordered")
        semantics = answers["semantics"]
        if (semantics.provided and semantics.value == "separate"
                and answers["shared_cap_tokens"].provided):
            raise ValueError("separate budgets cannot declare a shared vendor window")
        self._original_bytes = proposal_raw
        self._answer_bytes = answers_raw
        self._scope = deepcopy(value["scope"])
        self._answers = deepcopy(answers)

    @property
    def scope(self):
        return deepcopy(self._scope)

    @property
    def original_bytes(self):
        return self._original_bytes

    @property
    def answer_bytes(self):
        return self._answer_bytes

    def evaluate(self, selected_scope, *, enabled, evidence_eligible):
        """Apply the existing conservative predicate only after typed admission.

        False or unresolved source eligibility gives unknown, never unsupported.
        Disabled is an explicit applicability decision, distinct from every
        unresolved answer. No new physical or independent-verification claim
        follows from passing this synthetic arithmetic screen.
        """
        if enabled is not None and type(enabled) is not bool:
            raise ValueError("enabled must be an exact Boolean or unresolved")
        if evidence_eligible is not None and type(evidence_eligible) is not bool:
            raise ValueError("evidence eligibility must be an exact Boolean or unresolved")
        if selected_scope is not None:
            validate(SCOPE, selected_scope, "selected context scope")
        states = tuple(deepcopy(self._answers).items())
        def unresolved(reason, outcome=Outcome.UNKNOWN):
            return BoundResult(outcome, False, reason, (), states)
        if enabled is False:
            return unresolved("selection_not_enabled", Outcome.SKIPPED)
        if enabled is None:
            return unresolved("selection_activation_unknown")
        if selected_scope is None:
            return unresolved("selection_scope_missing")
        if selected_scope != self._scope:
            return unresolved("route_scope_mismatch")
        if evidence_eligible is not True:
            return unresolved("source_evidence_unresolved" if evidence_eligible is None
                              else "source_evidence_ineligible")
        def provided(name):
            answer = self._answers[name]
            return answer.value if answer.provided else None
        semantics = provided("semantics")
        interval = provided("input_tokens")
        budget = Budget(
            semantics=Semantics(semantics) if semantics is not None else Semantics.UNKNOWN,
            input_tokens=TokenRange(**interval) if interval is not None else None,
            reserved_output=provided("reserved_output_tokens"),
            output_cap=provided("output_cap_tokens"),
            shared_cap=provided("shared_cap_tokens"),
            input_cap=provided("input_cap_tokens"),
            policy_total_cap=provided("policy_total_cap_tokens"),
        )
        result = evaluate(budget)
        checks = list(result.checks)
        # Optional constraints need an explicit not_applicable answer to mean
        # no additional constraint. Missing/unknown/withheld cannot become an
        # implicit absence of a possibly applicable cap.
        for field, check_name in (("input_cap_tokens", "input"),
                                  ("policy_total_cap_tokens", "policy_total")):
            if (not self._answers[field].provided
                    and self._answers[field].state is not State.NOT_APPLICABLE
                    and not any(check.name == check_name for check in checks)):
                checks.append(Check(check_name, Outcome.UNKNOWN, Outcome.UNKNOWN))
        outcome = combine(tuple(check.upper for check in checks))
        lower = combine(tuple(check.lower for check in checks))
        return BoundResult(outcome, outcome is Outcome.FAIL and lower is not Outcome.FAIL,
                           "normalized_context_screen", tuple(checks), states)
