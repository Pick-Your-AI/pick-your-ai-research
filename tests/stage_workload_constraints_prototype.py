"""CD-5 0.2 synthetic mechanics candidate; no released contract or fit verdict.

The earlier 0.1 module and original fixture bytes remain historical witnesses.
This reader admits exact serving-selection bindings, typed tokenizer assumptions
and independently qualified facts. It never executes stages or aggregates load.
"""

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import StrEnum
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_research import SCHEMAS, schema_errors
from tests.stage_workload_binding_prototype import (
    BOOL, COUNT, REQUESTS, Length, Requests, decode, digest, length_schema,
)
from tests.t0_answer_state_prototype import Answer, AnswerIndex, State


SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "stage-workload-binding-v02.schema.json").read_text(encoding="utf-8"))
# Root identity/hash failures prevent reading the inventory. Individual stage
# failures instead become bounded results; the published schema remains strict.
_envelope = deepcopy(SCHEMA)
_envelope["properties"]["x_t0_stage_workload"]["properties"]["stages"]["items"] = {}
ENVELOPE = Draft202012Validator(_envelope)
STAGE = Draft202012Validator({"$ref": "#/$defs/stage", "$defs": SCHEMA["$defs"]})
TOKENIZER = {"$ref": "#/$defs/tokenizer_value", "$defs": SCHEMA["$defs"]}
SERVING_KINDS = frozenset(("model", "embedding_model", "vector_database", "fine_tuned_model"))
MODEL_KINDS = SERVING_KINDS - {"vector_database"}
SCALARS = {
    "active": BOOL,
    "scope_confirmed": BOOL,
    "requests": REQUESTS,
    "peak_concurrency": COUNT,
    "input_uses_tokens": BOOL,
    "output_generates_tokens": BOOL,
    "native_input_units_complete": BOOL,
    "native_output_units_complete": BOOL,
}


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def descriptor_digest(value):
    # An escaped lone surrogate is possible in otherwise valid UTF-8 JSON.
    # Keep malformed rows in coverage using their JSON escape, so stage
    # validation can reject them locally. Valid descriptor UTF-8 is unchanged.
    return digest(("cd5-0.2\n" + _canonical(value)).encode("utf-8", errors="backslashreplace"))


def _pointer(parts):
    return "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)


def answer_path(proposal, stage, *tokens):
    return _pointer(("stage_workloads", proposal["build_sha256"], proposal["inventory_id"],
                     "stages", stage["id"], descriptor_digest(stage), *tokens))


def inventory_path(proposal):
    # Sorting complete descriptors also retains duplicate/malformed records in
    # the identity of an inventory that will receive a local rejection result.
    stages = sorted(proposal["stages"], key=_canonical)
    return _pointer(("stage_workloads", proposal["build_sha256"], proposal["inventory_id"],
                     "inventories", descriptor_digest(stages), "complete"))


class Status(StrEnum):
    READY = "ready"
    INCOMPLETE = "incomplete"
    INACTIVE = "inactive"
    NOT_APPLICABLE = "not_applicable"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Problem:
    reason: str
    document: str
    path: str


@dataclass(frozen=True)
class TokenizerAssumption:
    basis: str
    reference_id: str
    reference_version: str
    assumption: bool = True


@dataclass(frozen=True)
class Metric:
    name: str
    status: Status
    reason: str
    value: object = None
    answer_state: State | None = None
    source_path: str | None = None
    source_document: str = "answers"


@dataclass(frozen=True)
class StageResult:
    stage_index: int
    scope: dict | None
    status: Status
    reason: str
    metrics: tuple[Metric, ...] = ()
    problems: tuple[Problem, ...] = ()


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


@dataclass(frozen=True)
class RuleGate:
    outcome: str | None
    reason: str
    severity: str


def rule_gate(finding, *, policy, severity):
    """Map a normalized input into a dependent rule without claiming fit.

    None means the caller must evaluate that rule's actual predicate. Readiness
    never becomes pass. Severity is supplied once by the rule, not by its result.
    """
    if policy not in ("compatibility", "recommendation"):
        raise ValueError("unknown CD-5 dependent rule policy")
    if severity not in ("info", "warning", "error"):
        raise ValueError("invalid fixed rule severity")
    if not isinstance(finding, (Metric, StageResult, Result)):
        raise ValueError("rule gate requires a CD-5 normalized finding")
    if finding.status is Status.READY:
        return RuleGate(None, "predicate_not_evaluated", severity)
    if finding.status in (Status.INACTIVE, Status.NOT_APPLICABLE):
        return RuleGate("skipped", finding.reason, severity)
    return RuleGate("unknown" if policy == "compatibility" else "skipped",
                    finding.reason, severity)


class _StageError(Exception):
    def __init__(self, problem):
        self.problem = problem


class StageWorkloadRecord:
    """Read a 0.2 candidate without changing the three original input strings.

    Serving-kind membership is a research scope gate. In particular, the source
    qualifier must establish that a fine-tuned artifact is a full serving model;
    this candidate does not resolve a catalog or classify an adapter itself.
    """

    def __init__(self, binding_raw, build_raw, answers_raw):
        binding = decode(binding_raw)
        try:
            ENVELOPE.validate(binding)
        except ValidationError as error:
            raise ValueError("invalid CD-5 0.2 envelope") from error
        proposal = binding["x_t0_stage_workload"]
        for label, raw in (("build", build_raw), ("answer_states", answers_raw)):
            if type(raw) is not bytes or digest(raw) != proposal[label + "_sha256"]:
                raise ValueError(label + " bytes do not match the stage binding")
        build = decode(build_raw)
        errors = schema_errors(build, SCHEMAS["build.schema.json"])
        if errors:
            raise ValueError("invalid retained build")
        if type(build["revision"]) is not int:
            raise ValueError("build revision must use a JSON integer")
        for selection in build["selections"]:
            for value, pattern in (
                    (selection["id"], SCHEMAS["common.schema.json"]["$defs"]["selection_id"]["pattern"]),
                    (selection["role"], SCHEMAS["selection.schema.json"]["properties"]["role"]["pattern"])):
                if re.fullmatch(pattern, value) is None:
                    raise ValueError("selection identity/role must match the whole string")
        maximum = build["objectives"].get("max_concurrency")
        if maximum is not None and type(maximum) is not int:
            raise ValueError("Build concurrency bound requires an exact JSON integer")
        counts = Counter(selection["id"] for selection in build["selections"])
        selected = {s["id"]: deepcopy(s) for s in build["selections"] if counts[s["id"]] == 1}
        selection_positions = {s["id"]: position for position, s in enumerate(build["selections"])
                               if counts[s["id"]] == 1}
        ids = Counter(stage["id"] for stage in proposal["stages"]
                      if isinstance(stage, dict) and type(stage.get("id")) is str)
        index = AnswerIndex(answers_raw)
        answers, origins, consumed = {}, {}, []

        def read(path, schema):
            consumed.append(path)
            try:
                answers[path] = index.read(path, schema)
            except ValueError as error:
                raise _StageError(Problem("invalid_provided_value", "answers", path)) from error
            origins[path] = "answers"
            return answers[path]

        def reject(reason, path):
            raise _StageError(Problem(reason, "answers", path))

        def read_length(stage, field, unit):
            path = answer_path(proposal, stage, *field)
            answer = read(path, length_schema(unit, input_tokens=field == ("input_tokens",)))
            if not answer.provided:
                return
            maximum = answer.value["max"]
            if unit in ("audio_seconds", "video_seconds"):
                maximum = Decimal(maximum)
            elif type(maximum) is not int:
                reject("exact_integer_required", path)
            mean = Decimal(answer.value["mean"])
            if mean > maximum:
                reject("length_mean_exceeds_maximum", path)
            if field == ("input_tokens",) and mean < 1:
                reject("input_token_mean_below_one", path)

        inventory_error = None
        try:
            read(inventory_path(proposal), BOOL)
        except _StageError as error:
            inventory_error = error.problem
        records = []
        for position, candidate in enumerate(proposal["stages"]):
            location = f"/x_t0_stage_workload/stages/{position}"
            try:
                STAGE.validate(candidate)
            except ValidationError:
                records.append((position, None, (Problem("invalid_stage_descriptor", "binding", location),)))
                continue
            stage = deepcopy(candidate)
            problems = []
            if ids[stage["id"]] != 1:
                problems.append(Problem("duplicate_stage_id", "binding", location + "/id"))
            sid = stage["selection_id"]
            if counts[sid] == 0:
                problems.append(Problem("selection_not_found", "binding", location + "/selection_id"))
            elif counts[sid] > 1:
                problems.append(Problem("duplicate_selection_id", "binding", location + "/selection_id"))
            elif selected[sid]["kind"] not in SERVING_KINDS:
                problems.append(Problem("selection_is_not_serving_component", "binding", location + "/selection_id"))
            elif (selected[sid]["kind"] == "fine_tuned_model"
                  and selected[sid]["settings"].get("use_adapter") is True):
                problems.append(Problem("adapter_is_not_serving_component", "binding", location + "/selection_id"))
            if problems:
                records.append((position, stage, tuple(problems)))
                continue
            output_limit = selected[sid]["settings"].get("max_output_tokens")
            if output_limit is not None and (type(output_limit) is not int or output_limit < 0):
                records.append((position, stage, (Problem("invalid_selection_output_bound", "build",
                                f"/selections/{selection_positions[sid]}/settings/max_output_tokens"),)))
                continue
            try:
                for name, schema in SCALARS.items():
                    path = answer_path(proposal, stage, name)
                    answer = read(path, schema)
                    if answer.provided:
                        value = answer.value["count"] if name == "requests" else answer.value
                        if name in ("requests", "peak_concurrency") and type(value) is not int:
                            reject("exact_integer_required", path)
                read_length(stage, ("input_tokens",), "tokens")
                read_length(stage, ("output_tokens",), "tokens")
                for direction in ("native_input_units", "native_output_units"):
                    for unit in stage[direction]:
                        read_length(stage, (direction, unit), unit)
                path = answer_path(proposal, stage, "tokenizer_assumption")
                consumed.append(path)
                # The typed descriptor is its sole authority. A separate CD-1
                # document is used only to reuse its unchanged answer decoder;
                # no sidecar value or inherited stage parent overrides it.
                document = {"x_t0_answer_states": {"proposal_version": "cd1-0.1",
                            "answers": {"/tokenizer": stage["tokenizer_assumption"]}}}
                answer = AnswerIndex(json.dumps(document)).read("/tokenizer", TOKENIZER)
                answers[path] = replace(answer, source_path=location + "/tokenizer_assumption")
                origins[path] = "binding"
            except _StageError as error:
                problems.append(error.problem)
            records.append((position, stage, tuple(problems)))
        self._bytes = binding_raw, build_raw, answers_raw
        self._proposal, self._build = deepcopy(proposal), deepcopy(build)
        self._records, self._selections = tuple(records), selected
        self._answers, self._origins = answers, origins
        self._consumed = tuple(dict.fromkeys(consumed))
        self._inventory_error = inventory_error

    @property
    def original_bytes(self):
        return self._bytes

    @property
    def answer_paths(self):
        return self._consumed

    def evaluate(self, eligible_answers=None):
        """Return independent stage findings; eligibility cannot repair bad input."""
        eligible_answers = {} if eligible_answers is None else eligible_answers
        if type(eligible_answers) is not dict or set(eligible_answers) - set(self._consumed):
            raise ValueError("eligibility must name only consumed scoped answer paths")
        if any(value is not None and type(value) is not bool for value in eligible_answers.values()):
            raise ValueError("answer eligibility must be an exact Boolean or unresolved")
        eligibility = {path: eligible_answers.get(path) for path in self._consumed}

        def fact(path):
            answer = self._answers.get(path)
            return answer.value if answer and answer.provided and eligibility[path] is True else None

        def metric(path, name, convert=lambda value: value):
            answer = self._answers[path]
            fields = (answer.state, answer.source_path, self._origins[path])
            if answer.state in (State.UNKNOWN, State.MISSING, State.WITHHELD):
                return Metric(name, Status.INCOMPLETE, "answer_" + answer.state, None, *fields)
            if eligibility[path] is not True:
                reason = "evidence_ineligible" if eligibility[path] is False else "evidence_unresolved"
                return Metric(name, Status.INCOMPLETE, reason, None, *fields)
            if answer.state is State.NOT_APPLICABLE:
                return Metric(name, Status.NOT_APPLICABLE, "answer_not_applicable", None, *fields)
            return Metric(name, Status.READY, "scoped_fact", convert(answer.value), *fields)

        coverage_path = inventory_path(self._proposal)
        if self._inventory_error:
            coverage = Metric("stage_inventory", Status.REJECTED, "invalid_inventory_answer")
        else:
            coverage = metric(coverage_path, "stage_inventory")
            if coverage.status is Status.READY and coverage.value is not True:
                coverage = replace(coverage, status=Status.INCOMPLETE, reason="stage_inventory_unconfirmed")
        complete = coverage.status is Status.READY and coverage.value is True
        inventory = coverage
        results = []
        for position, stage, problems in self._records:
            def finish(status, reason, metrics=(), issues=()):
                results.append(StageResult(position, deepcopy(stage), status, reason,
                                           tuple(metrics), tuple(issues)))
            if problems:
                finish(Status.REJECTED, problems[0].reason, issues=problems)
                continue
            selected = self._selections[stage["selection_id"]]

            def path(*tokens):
                return answer_path(self._proposal, stage, *tokens)

            # These are comparisons of qualified stage facts with explicit
            # input constraints. They do not verify a provider's capabilities.
            conflicts = []
            requests, peak, output = (fact(path(name)) for name in
                                      ("requests", "peak_concurrency", "output_tokens"))
            if requests is not None and requests["count"] == 0 and peak is not None and peak > 0:
                conflicts.append(Problem("zero_requests_with_positive_peak", "answers", path("peak_concurrency")))
            limit = selected["settings"].get("max_output_tokens")
            if output is not None and limit is not None and output["max"] > limit:
                conflicts.append(Problem("stage_output_exceeds_selection_maximum", "answers", path("output_tokens")))
            limit = self._build["objectives"].get("max_concurrency")
            if peak is not None and limit is not None and peak > limit:
                conflicts.append(Problem("stage_peak_exceeds_build_maximum", "answers", path("peak_concurrency")))
            if conflicts:
                finish(Status.REJECTED, conflicts[0].reason, issues=conflicts)
                continue
            if not selected["enabled"]:
                finish(Status.INACTIVE, "selection_disabled")
                continue
            activation = metric(path("active"), "active")
            if activation.status is Status.NOT_APPLICABLE:
                finish(Status.NOT_APPLICABLE, activation.reason, (activation,))
                continue
            if activation.status is not Status.READY:
                finish(Status.INCOMPLETE, "stage_activation_" + activation.reason, (activation,))
                continue
            if activation.value is False:
                finish(Status.INACTIVE, "stage_explicitly_inactive")
                continue
            scope = metric(path("scope_confirmed"), "scope_confirmed")
            if scope.status is Status.NOT_APPLICABLE:
                finish(Status.NOT_APPLICABLE, scope.reason, (scope,))
                continue
            if scope.status is not Status.READY or scope.value is not True:
                reason = scope.reason if scope.status is not Status.READY else "scope_not_confirmed"
                finish(Status.INCOMPLETE, "stage_scope_" + reason, (scope,))
                continue
            if (selected["kind"] == "fine_tuned_model"
                    and selected["settings"].get("use_adapter") is not False):
                finish(Status.INCOMPLETE, "fine_tuned_serving_mode_unresolved")
                continue
            metrics = [metric(path("requests"), "requests", lambda value: Requests(**value)),
                       metric(path("peak_concurrency"), "peak_concurrency")]
            token_path = path("tokenizer_assumption")
            tokenizer = metric(token_path, "tokenizer_assumption")
            uses_input, generates_output = fact(path("input_uses_tokens")), fact(path("output_generates_tokens"))
            if uses_input is False and generates_output is False:
                tokenizer = replace(tokenizer, status=Status.NOT_APPLICABLE,
                                    reason="tokenizer_not_required_for_operation", value=None)
            elif tokenizer.status is Status.READY:
                value = tokenizer.value
                if value["basis"] == "model_native":
                    reference = {"id": selected.get("catalog_item_id"),
                                 "version": selected.get("catalog_item_version")}
                    reference_ok = Draft202012Validator({"$ref": "#/$defs/reference",
                                                        "$defs": SCHEMA["$defs"]}).is_valid(reference)
                    if selected["kind"] not in MODEL_KINDS or not reference_ok:
                        tokenizer = replace(tokenizer, status=Status.INCOMPLETE,
                                            reason="model_native_reference_unresolved", value=None)
                    else:
                        tokenizer = replace(tokenizer, reason="scoped_tokenizer_assumption",
                                            value=TokenizerAssumption("model_native", reference["id"], reference["version"]))
                else:
                    reference = value["reference"]
                    tokenizer = replace(tokenizer, reason="scoped_tokenizer_assumption",
                                        value=TokenizerAssumption(value["basis"], reference["id"], reference["version"]))
            elif tokenizer.status is Status.NOT_APPLICABLE:
                tokenizer = replace(tokenizer, status=Status.INCOMPLETE,
                                    reason="tokenizer_required_but_not_applicable")
            metrics.append(tokenizer)

            def length(field, unit):
                def convert(value):
                    maximum = Decimal(value["max"]) if unit in ("audio_seconds", "video_seconds") else value["max"]
                    return Length(Decimal(value["mean"]), maximum, unit)
                return metric(path(*field), "/".join(field), convert)

            for field, applicability in (("input_tokens", "input_uses_tokens"),
                                         ("output_tokens", "output_generates_tokens")):
                operation = metric(path(applicability), applicability)
                amount = length((field,), "tokens")
                if operation.status is not Status.READY:
                    amount = replace(amount, status=Status.INCOMPLETE,
                                     reason="token_operation_" + operation.reason, value=None)
                elif operation.value is False:
                    if amount.status is not Status.NOT_APPLICABLE:
                        amount = replace(amount, status=Status.INCOMPLETE,
                                         reason=("provided_tokens_conflict_with_operation" if amount.status is Status.READY
                                                 else amount.reason), value=None)
                elif amount.status is Status.NOT_APPLICABLE:
                    amount = replace(amount, status=Status.INCOMPLETE,
                                     reason="token_count_required_but_not_applicable")
                elif tokenizer.status is not Status.READY:
                    amount = replace(amount, status=Status.INCOMPLETE,
                                     reason="tokenizer_" + tokenizer.reason, value=None)
                metrics.append(amount)
            for direction in ("native_input_units", "native_output_units"):
                coverage = metric(path(direction + "_complete"), direction)
                if coverage.status is Status.READY and coverage.value is not True:
                    coverage = replace(coverage, status=Status.INCOMPLETE, reason="native_inventory_unconfirmed")
                elif coverage.status is Status.NOT_APPLICABLE:
                    coverage = replace(coverage, status=Status.INCOMPLETE, reason="native_inventory_not_confirmed")
                metrics.append(coverage)
                metrics.extend(length((direction, unit), unit) for unit in stage[direction])
            unresolved = any(item.status in (Status.INCOMPLETE, Status.REJECTED) for item in metrics)
            finish(Status.INCOMPLETE if unresolved else Status.READY,
                   "stage_inputs_unresolved" if unresolved else "stage_inputs_ready", metrics)
        if not results:
            status, reason = Status.INCOMPLETE, "no_stage_records"
        elif not complete or any(stage.status in (Status.REJECTED, Status.INCOMPLETE) for stage in results):
            status, reason = Status.INCOMPLETE, "scoped_inventory_unresolved"
        elif all(stage.status in (Status.INACTIVE, Status.NOT_APPLICABLE) for stage in results):
            status, reason = Status.INACTIVE, "all_declared_stages_inactive_or_not_applicable"
        else:
            status, reason = Status.READY, "scoped_stage_inputs_ready"
        return Result(status, reason, inventory, tuple(results),
                      tuple(deepcopy(self._answers).items()), tuple(eligibility.items()),
                      *(digest(raw) for raw in self._bytes))
