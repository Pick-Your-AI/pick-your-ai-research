"""Synthetic CD-13 wire binding for already-normalized Boolean rule inputs.

Bind one universal selection rule to complete frozen-format build and CD-1
answer bytes. This is not a general predicate DSL, evidence resolver, activation
planner, catalog reader, migration or released contract implementation.
"""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_research import SCHEMAS, intake_json, schema_errors
from tests.selection_quantifier_prototype import (
    Result, Rule, Selection, evaluate, validate_identities,
)
from tests.t0_answer_state_prototype import Answer, AnswerIndex


WIRE_SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                          "selection-binding.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(WIRE_SCHEMA)
FIELDS = ("applies_when", "assertion")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError("CD-13 retained inputs must be UTF-8 bytes")
    return intake_json(raw.decode("utf-8"))


def answer_path(selection_id, rule_id, rule_version, field):
    """Use literal JSON Pointer tokens, never dotted paths or array offsets."""
    tokens = ("selection_checks", selection_id, rule_id, rule_version, field)
    return "/" + "/".join(token.replace("~", "~0").replace("/", "~1")
                          for token in tokens)


@dataclass(frozen=True)
class Operands:
    selection_id: str
    applies_when: Answer
    assertion: Answer


@dataclass(frozen=True)
class BoundResult:
    rule_version: str
    result: Result
    answers: tuple[Operands, ...]
    eligibility: tuple[tuple[str, bool | None, bool | None], ...]


class SelectionRuleRecord:
    """Evaluate all enabled selections, preserving typed unresolved operands.

    Complete-byte equality only binds inputs. The caller separately establishes
    eligibility for EACH applicability/assertion answer; even a provided false
    applicability value cannot skip a rule on ineligible evidence.
    """

    def __init__(self, binding_raw, build_raw, answers_raw):
        binding = decode(binding_raw)
        try:
            WIRE.validate(binding)
        except ValidationError as error:
            raise ValueError("invalid CD-13 binding: " + error.message) from error
        proposal = binding["x_t0_selection_rule"]
        for label, raw in (("build", build_raw), ("answer_states", answers_raw)):
            if type(raw) is not bytes or digest(raw) != proposal[label + "_sha256"]:
                raise ValueError(label + " bytes do not match the selection binding")
        build = decode(build_raw)
        errors = schema_errors(build, SCHEMAS["build.schema.json"])
        if errors:
            raise ValueError("invalid retained build: " + errors[0])
        if type(build["revision"]) is not int:
            raise ValueError("build revision must use a JSON integer")
        selections = tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                           for s in build["selections"])
        # Frozen regexes use $, which can match before a final LF. This new
        # pointer-binding boundary requires full canonical selection/role text.
        id_pattern = SCHEMAS["common.schema.json"]["$defs"]["selection_id"]["pattern"]
        role_pattern = SCHEMAS["selection.schema.json"]["properties"]["role"]["pattern"]
        for selection in selections:
            if (re.fullmatch(id_pattern, selection.id) is None or
                    re.fullmatch(role_pattern, selection.role) is None):
                raise ValueError("selection identity/role must match the whole string")
        validate_identities(selections)
        rule = proposal["rule"]
        index = AnswerIndex(answers_raw)
        # Validate every scoped provided operand, including disabled selections
        # and assertions whose applicability will later be false or unresolved.
        # No malformed known value can disappear through a short circuit.
        operands = {}
        for selection in sorted(selections, key=lambda item: item.id):
            if selection.kind == rule["kind"]:
                values = {field: index.read(answer_path(selection.id, rule["id"],
                                                        rule["version"], field),
                                             {"type": "boolean"}) for field in FIELDS}
                operands[selection.id] = Operands(selection.id, **values)
        self._binding_bytes = binding_raw
        self._build_bytes = build_raw
        self._answer_bytes = answers_raw
        self._selections = selections
        self._rule = deepcopy(rule)
        self._operands = operands

    @property
    def original_bytes(self):
        return self._binding_bytes, self._build_bytes, self._answer_bytes

    def evaluate(self, eligible_answers=None):
        """Caller-established per-operand eligibility; omission stays unknown.

        False and unresolved eligibility both prevent that operand from becoming
        a predicate fact. Their values remain separately visible in the result.
        This method does not infer eligibility from an answer's source label.
        """
        if eligible_answers is None:
            eligible_answers = {}
        if type(eligible_answers) is not dict:
            raise ValueError("answer eligibility must be a selection-keyed object")
        if any(key not in self._operands for key in eligible_answers):
            raise ValueError("answer eligibility names an unscoped selection")
        for values in eligible_answers.values():
            if type(values) is not dict or set(values) - set(FIELDS):
                raise ValueError("answer eligibility must name known operands")
            if any(value is not None and type(value) is not bool for value in values.values()):
                raise ValueError("answer eligibility must be exact Boolean or unresolved")
        eligible = {key: {field: eligible_answers.get(key, {}).get(field)
                          for field in FIELDS} for key in self._operands}

        def predicate(selection, field):
            answer = getattr(self._operands[selection.id], field)
            if eligible[selection.id][field] is not True or not answer.provided:
                return None
            return answer.value

        result = evaluate(self._selections, Rule(
            self._rule["id"], self._rule["kind"], self._rule["severity"],
            lambda selection: predicate(selection, "applies_when"),
            lambda selection: predicate(selection, "assertion"),
        ))
        return BoundResult(
            self._rule["version"], result,
            tuple(deepcopy(tuple(self._operands.values()))),
            tuple((key, values["applies_when"], values["assertion"])
                  for key, values in eligible.items()),
        )
