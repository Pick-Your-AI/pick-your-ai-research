"""CD-5 research normalization for independently qualified stage workloads.

The stage inventory binds complete original Build and CD-1 bytes. It preserves
separate operation/configuration/tokenizer scopes and supplies no execution
order, fan-out, retry, tokenization, aggregate-cost or memory/latency model.
Ready means the scoped input record is complete, never that a build fits.
"""

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_research import SCHEMAS, intake_json, schema_errors
from tests.selection_quantifier_prototype import Selection, validate_identities
from tests.t0_answer_state_prototype import Answer, AnswerIndex, State


SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "stage-workload-binding.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(SCHEMA)
BOOL = {"type": "boolean"}
COUNT = SCHEMA["$defs"]["count"]
DECIMAL = SCHEMA["$defs"]["decimal"]
REQUESTS = {
    "type": "object", "required": ["count", "period"], "additionalProperties": False,
    "properties": {"count": COUNT, "period": {"enum": ["day", "month"]}},
}
POSITIVE_COUNT = {**COUNT, "minimum": 1}
SCALARS = {
    "active": BOOL,
    "scope_confirmed": BOOL,
    "requests": REQUESTS,
    "peak_concurrency": POSITIVE_COUNT,
    "input_uses_tokens": BOOL,
    "output_generates_tokens": BOOL,
    "native_input_units_complete": BOOL,
    "native_output_units_complete": BOOL,
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError("CD-5 retained inputs must be UTF-8 bytes")
    return intake_json(raw.decode("utf-8"))


def descriptor_digest(value):
    """Hash this candidate's string/list/object descriptors, not original files."""
    payload = "cd5-0.1\n" + json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return digest(payload.encode("utf-8"))


def answer_path(proposal, stage, *tokens):
    # Complete Build bytes scope every fact, including unchanged stage IDs.
    parts = ("stage_workloads", proposal["build_sha256"], proposal["inventory_id"],
             "stages", stage["id"], descriptor_digest(stage), *tokens)
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def inventory_path(proposal):
    stages = sorted(proposal["stages"], key=lambda stage: stage["id"])
    parts = ("stage_workloads", proposal["build_sha256"], proposal["inventory_id"],
             "inventories", descriptor_digest(stages), "complete")
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def length_schema(unit, *, input_tokens=False):
    maximum = DECIMAL if unit in ("audio_seconds", "video_seconds") else COUNT
    if input_tokens:
        maximum = POSITIVE_COUNT
    return {
        "type": "object", "required": ["mean", "max"], "additionalProperties": False,
        "properties": {"mean": DECIMAL, "max": maximum},
    }


class Status(StrEnum):
    READY = "ready"
    INCOMPLETE = "incomplete"
    INACTIVE = "inactive"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class Requests:
    count: int
    period: str


@dataclass(frozen=True)
class Length:
    mean: Decimal
    maximum: int | Decimal
    unit: str


@dataclass(frozen=True)
class Metric:
    name: str
    status: Status
    reason: str
    value: Requests | Length | int | bool | None = None


@dataclass(frozen=True)
class StageResult:
    scope: dict
    status: Status
    reason: str
    metrics: tuple[Metric, ...]


@dataclass(frozen=True)
class Result:
    status: Status
    reason: str
    inventory: Metric
    stages: tuple[StageResult, ...]
    answers: tuple[tuple[str, Answer], ...]
    eligibility: tuple[tuple[str, bool | None], ...]
    binding_sha256: str
    build_sha256: str
    answer_states_sha256: str


class StageWorkloadRecord:
    """Validate every declared stage before any activation or eligibility gate.

    Repeated calls to the same selection have distinct stage identities. The
    descriptor fixes operation/version, configuration, tokenizer and native-unit
    inventories; a separately qualified scope_confirmed answer establishes the
    actual association. A changed Build or descriptor invalidates old fact keys.
    """

    def __init__(self, binding_raw, build_raw, answers_raw):
        binding = decode(binding_raw)
        try:
            WIRE.validate(binding)
        except ValidationError as error:
            raise ValueError("invalid CD-5 binding: " + error.message) from error
        proposal = binding["x_t0_stage_workload"]
        for label, raw in (("build", build_raw), ("answer_states", answers_raw)):
            if type(raw) is not bytes or digest(raw) != proposal[label + "_sha256"]:
                raise ValueError(label + " bytes do not match the stage binding")
        build = decode(build_raw)
        errors = schema_errors(build, SCHEMAS["build.schema.json"])
        if errors:
            raise ValueError("invalid retained build: " + errors[0])
        if type(build["revision"]) is not int:
            raise ValueError("build revision must use a JSON integer")
        selections = tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                           for s in build["selections"])
        for selection in selections:
            for value, pattern in (
                    (selection.id, SCHEMAS["common.schema.json"]["$defs"]["selection_id"]["pattern"]),
                    (selection.role, SCHEMAS["selection.schema.json"]["properties"]["role"]["pattern"])):
                if re.fullmatch(pattern, value) is None:
                    raise ValueError("selection identity/role must match the whole string")
        validate_identities(selections)
        selected = {selection.id: selection for selection in selections}
        stages = {}
        index = AnswerIndex(answers_raw)
        answers = {}

        def read(path, schema):
            answers[path] = index.read(path, schema)
            return answers[path]

        def read_length(stage, field, unit):
            answer = read(answer_path(proposal, stage, *field),
                          length_schema(unit, input_tokens=field == ("input_tokens",)))
            if not answer.provided:
                return
            value = answer.value
            maximum = value["max"]
            if unit in ("audio_seconds", "video_seconds"):
                maximum = Decimal(maximum)
            elif type(maximum) is not int:
                raise ValueError("token/image maxima require exact JSON integers")
            mean = Decimal(value["mean"])
            if mean > maximum:
                raise ValueError("stage mean cannot exceed its maximum")
            if field == ("input_tokens",) and mean < 1:
                raise ValueError("input token mean must be at least one")

        read(inventory_path(proposal), BOOL)
        for stage in proposal["stages"]:
            if stage["id"] in stages:
                raise ValueError("duplicate stage identity")
            if stage["selection_id"] not in selected:
                raise ValueError("stage references an unknown selection")
            stages[stage["id"]] = deepcopy(stage)
            for name, schema in SCALARS.items():
                answer = read(answer_path(proposal, stage, name), schema)
                if answer.provided:
                    if name == "requests" and type(answer.value["count"]) is not int:
                        raise ValueError("request count requires an exact JSON integer")
                    if name == "peak_concurrency" and type(answer.value) is not int:
                        raise ValueError("peak concurrency requires an exact JSON integer")
            read_length(stage, ("input_tokens",), "tokens")
            read_length(stage, ("output_tokens",), "tokens")
            for direction in ("native_input_units", "native_output_units"):
                for unit in stage[direction]:
                    read_length(stage, (direction, unit), unit)
        self._bytes = binding_raw, build_raw, answers_raw
        self._proposal = deepcopy(proposal)
        self._stages = stages
        self._selections = selected
        self._answers = answers

    @property
    def original_bytes(self):
        return self._bytes

    @property
    def answer_paths(self):
        return tuple(self._answers)

    def evaluate(self, eligible_answers=None):
        """Normalize only caller-qualified facts; retain every unresolved state.

        Each Boolean, numeric record, non-applicability answer and completeness
        fact has separate eligibility. A source label, hash or preset cannot
        qualify itself. No stage inherits global objectives or sibling answers.
        """
        eligible_answers = {} if eligible_answers is None else eligible_answers
        if type(eligible_answers) is not dict or set(eligible_answers) - set(self._answers):
            raise ValueError("eligibility must name only scoped stage answer paths")
        if any(value is not None and type(value) is not bool for value in eligible_answers.values()):
            raise ValueError("answer eligibility must be an exact Boolean or unresolved")
        eligibility = {path: eligible_answers.get(path) for path in self._answers}

        def fact(path):
            answer = self._answers[path]
            return answer.value if answer.provided and eligibility[path] is True else None

        coverage_path = inventory_path(self._proposal)
        complete = fact(coverage_path) is True
        coverage = Metric("stage_inventory", Status.READY if complete else Status.INCOMPLETE,
                          "complete_inventory_confirmed" if complete else "stage_inventory_unconfirmed",
                          True if complete else None)
        results = []
        for _, stage in sorted(self._stages.items()):
            sid = stage["selection_id"]

            def path(*tokens):
                return answer_path(self._proposal, stage, *tokens)

            def finish(status, reason, metrics=()):
                results.append(StageResult(deepcopy(stage), status, reason, tuple(metrics)))

            # Frozen Build selection state is authoritative; scoped stage facts
            # cannot enable a disabled component.
            if not self._selections[sid].enabled:
                finish(Status.INACTIVE, "selection_disabled")
                continue
            active = fact(path("active"))
            if active is False:
                finish(Status.INACTIVE, "stage_explicitly_inactive")
                continue
            if active is None:
                finish(Status.INCOMPLETE, "stage_activation_unresolved")
                continue
            if fact(path("scope_confirmed")) is not True:
                finish(Status.INCOMPLETE, "stage_scope_unconfirmed")
                continue
            metrics = []

            def ordinary(name, convert):
                value = fact(path(name))
                metrics.append(Metric(name, Status.INCOMPLETE, "fact_unresolved") if value is None
                               else Metric(name, Status.READY, "scoped_fact", convert(value)))

            ordinary("requests", lambda value: Requests(**value))
            ordinary("peak_concurrency", lambda value: value)

            def length(field, unit):
                value = fact(path(*field))
                name = "/".join(field)
                if value is None:
                    return Metric(name, Status.INCOMPLETE, "length_unresolved")
                maximum = (Decimal(value["max"]) if unit in ("audio_seconds", "video_seconds")
                           else value["max"])
                return Metric(name, Status.READY, "scoped_length",
                              Length(Decimal(value["mean"]), maximum, unit))

            for field, applicability in (("input_tokens", "input_uses_tokens"),
                                         ("output_tokens", "output_generates_tokens")):
                applies = fact(path(applicability))
                answer = self._answers[path(field)]
                if applies is None:
                    metric = Metric(field, Status.INCOMPLETE, "token_operation_unresolved")
                elif applies is False:
                    confirmed_absence = (answer.state is State.NOT_APPLICABLE
                                         and eligibility[path(field)] is True)
                    metric = Metric(field, Status.NOT_APPLICABLE if confirmed_absence
                                    else Status.INCOMPLETE,
                                    "operation_has_no_tokens" if confirmed_absence
                                    else "token_nonapplicability_unconfirmed")
                elif stage["tokenizer"] is None:
                    metric = Metric(field, Status.INCOMPLETE, "tokenizer_scope_missing")
                else:
                    metric = length((field,), "tokens")
                metrics.append(metric)
            for direction in ("native_input_units", "native_output_units"):
                covered = fact(path(direction + "_complete")) is True
                metrics.append(Metric(direction, Status.READY if covered else Status.INCOMPLETE,
                                      "native_inventory_confirmed" if covered
                                      else "native_inventory_unconfirmed", True if covered else None))
                metrics.extend(length((direction, unit), unit) for unit in stage[direction])
            unresolved = any(metric.status is Status.INCOMPLETE for metric in metrics)
            finish(Status.INCOMPLETE if unresolved else Status.READY,
                   "stage_inputs_unresolved" if unresolved else "stage_inputs_ready", metrics)
        if not results:
            status, reason = Status.INCOMPLETE, "no_stage_records"
        elif not complete or any(stage.status is Status.INCOMPLETE for stage in results):
            status, reason = Status.INCOMPLETE, "scoped_inventory_unresolved"
        elif all(stage.status is Status.INACTIVE for stage in results):
            status, reason = Status.INACTIVE, "all_declared_stages_inactive"
        else:
            status, reason = Status.READY, "scoped_stage_inputs_ready"
        return Result(status, reason, coverage, tuple(results),
                      tuple(deepcopy(self._answers).items()), tuple(eligibility.items()),
                      *(digest(raw) for raw in self._bytes))
