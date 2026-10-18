"""Synthetic CD-4 isolation inventory bound to complete Build and CD-1 bytes.

This is an offline research predicate, not a firewall, network probe, source
resolver, deployment authorizer or released contract reader. Each consumed
answer requires separately established eligibility for this exact scope.
"""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_research import SCHEMAS, intake_json, schema_errors
from tests.selection_quantifier_prototype import Outcome, Selection, validate_identities
from tests.t0_answer_state_prototype import Answer, AnswerIndex


WIRE_SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                          "isolation-binding.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(WIRE_SCHEMA)
BOOL = {"type": "boolean"}
IDENTITY = WIRE_SCHEMA["$defs"]["identity"]
INVENTORIES = ("runtime_endpoints", "connections", "runtime_artifacts")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError("CD-4 retained inputs must be UTF-8 bytes")
    return intake_json(raw.decode("utf-8"))


def answer_path(boundary_id, *tokens):
    return "/" + "/".join(token.replace("~", "~0").replace("/", "~1")
                          for token in ("isolation", boundary_id, *tokens))


def inventory_path(boundary_id, selection_id, inventory, entries):
    """Bind a completeness answer to its exact declared inventory membership.

    Descriptor order is immaterial. The specified UTF-8 canonical encoding has
    sorted object keys and no insignificant whitespace; these descriptors have
    strings/arrays/objects only. No original Build or CD-1 bytes are normalized.
    """
    ordered = sorted(entries, key=lambda entry: entry if isinstance(entry, str) else entry["id"])
    payload = ("cd4-0.1:" + inventory + "\n" +
               json.dumps(ordered, sort_keys=True, separators=(",", ":"), ensure_ascii=False)).encode("utf-8")
    return answer_path(boundary_id, "components", selection_id, inventory, digest(payload), "complete")


def inventory_entries(component, inventory):
    return component["runtime_endpoint_ids" if inventory == "runtime_endpoints" else inventory]


@dataclass(frozen=True)
class Check:
    selection_id: str
    subject: str
    outcome: Outcome
    reason: str


@dataclass(frozen=True)
class Result:
    outcome: Outcome
    reason: str
    checks: tuple[Check, ...]
    answers: tuple[tuple[str, Answer], ...]
    eligibility: tuple[tuple[str, bool | None], ...]
    rule_id: str = "W-R8"
    rule_version: str = "cd4-0.1"
    severity: str = "error"
    on_unknown: str = "block"


class IsolationRecord:
    """Read one boundary's explicitly enumerated selection footprints.

    An omitted component or unconfirmed inventory is unknown. Empty inventory
    arrays acquire completeness only from an eligible explicit true answer.
    Disabled selections retain input validation but do not enter the rule.
    """

    def __init__(self, binding_raw, build_raw, answers_raw):
        binding = decode(binding_raw)
        try:
            WIRE.validate(binding)
        except ValidationError as error:
            raise ValueError("invalid CD-4 binding: " + error.message) from error
        proposal = binding["x_t0_isolation"]
        for label, raw in (("build", build_raw), ("answer_states", answers_raw)):
            if type(raw) is not bytes or digest(raw) != proposal[label + "_sha256"]:
                raise ValueError(label + " bytes do not match the isolation binding")
        build = decode(build_raw)
        errors = schema_errors(build, SCHEMAS["build.schema.json"])
        if errors:
            raise ValueError("invalid retained build: " + errors[0])
        if type(build["revision"]) is not int:
            raise ValueError("build revision must use a JSON integer")
        selections = tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                           for s in build["selections"])
        for selection in selections:
            # Frozen regexes end in $, which can match before a terminal LF.
            # IDs at this new pointer boundary must match the complete text.
            for value, pattern in (
                    (selection.id, SCHEMAS["common.schema.json"]["$defs"]["selection_id"]["pattern"]),
                    (selection.role, SCHEMAS["selection.schema.json"]["properties"]["role"]["pattern"])):
                if re.fullmatch(pattern, value) is None:
                    raise ValueError("selection identity/role must match the whole string")
        validate_identities(selections)
        selection_ids = {selection.id for selection in selections}
        endpoints = set(proposal["endpoint_ids"])
        components = {}
        for component in proposal["components"]:
            sid = component["selection_id"]
            if sid not in selection_ids:
                raise ValueError("isolation component references an unknown selection")
            if sid in components:
                raise ValueError("duplicate isolation component selection")
            if set(component["runtime_endpoint_ids"]) - endpoints:
                raise ValueError("runtime endpoint reference is absent from the boundary inventory")
            for field in ("connections", "runtime_artifacts"):
                ids = [entry["id"] for entry in component[field]]
                if len(ids) != len(set(ids)):
                    raise ValueError("duplicate " + field + " identity within a component")
            components[sid] = deepcopy(component)

        boundary = proposal["boundary_id"]
        index = AnswerIndex(answers_raw)
        answers = {}

        def read(path, schema):
            answers[path] = index.read(path, schema)
            return answers[path]

        read("/workload/network", {"enum": ["online", "private_network", "air_gapped"]})
        read("/workload/isolation_boundary_id", IDENTITY)
        for endpoint in sorted(endpoints):
            read(answer_path(boundary, "endpoints", endpoint, "inside_boundary"), BOOL)
        # Validate provided facts even for disabled selections and inapplicable
        # workloads. A short circuit must not hide malformed or stale identities.
        for sid, component in sorted(components.items()):
            for inventory in INVENTORIES:
                read(inventory_path(boundary, sid, inventory,
                                    inventory_entries(component, inventory)), BOOL)
            for connection in sorted(component["connections"], key=lambda item: item["id"]):
                path = ("components", sid, "connections", connection["id"])
                destination = read(answer_path(boundary, *path, "destination_id"), IDENTITY)
                if destination.provided and destination.value not in endpoints:
                    raise ValueError("connection destination is absent from the boundary inventory")
                read(answer_path(boundary, *path, "lifecycle"),
                     {"enum": ["provisioning", "runtime"]})
                read(answer_path(boundary, *path, "state"), {"enum": ["enabled", "disabled"]})
            for artifact in sorted(component["runtime_artifacts"], key=lambda item: item["id"]):
                # The presence assertion is scoped to the declared exact digest,
                # not merely a same-named artifact or an available download URL.
                read(answer_path(boundary, "components", sid, "runtime_artifacts",
                                 artifact["id"], artifact["sha256"], "present_inside_boundary"), BOOL)
        self._bytes = binding_raw, build_raw, answers_raw
        self._boundary = boundary
        self._components = components
        self._selections = tuple(sorted(selections, key=lambda selection: selection.id))
        self._answers = answers

    @property
    def original_bytes(self):
        return self._bytes

    @property
    def answer_paths(self):
        return tuple(self._answers)

    def evaluate(self, eligible_answers=None):
        """Per-path eligibility is external evidence admission, never inferred.

        A provided answer, its source label or a matching digest cannot establish
        eligibility. Missing/false/unresolved eligibility yields an unknown fact.
        Network/isolation requirements, inventory coverage, endpoint membership,
        connection state/lifecycle and artifact presence each have their own key.
        """
        eligible_answers = {} if eligible_answers is None else eligible_answers
        if type(eligible_answers) is not dict or set(eligible_answers) - set(self._answers):
            raise ValueError("eligibility must be keyed only by scoped answer paths")
        if any(value is not None and type(value) is not bool for value in eligible_answers.values()):
            raise ValueError("answer eligibility must be exact Boolean or unresolved")
        eligibility = {path: eligible_answers.get(path) for path in self._answers}
        checks = []

        def fact(path):
            answer = self._answers[path]
            return answer.value if answer.provided and eligibility[path] is True else None

        def finish(outcome, reason):
            return Result(outcome, reason, tuple(checks),
                          tuple(deepcopy(self._answers).items()), tuple(eligibility.items()))

        enabled = [selection for selection in self._selections if selection.enabled]
        if not enabled:
            return finish(Outcome.SKIPPED, "no_enabled_selections")
        network = fact("/workload/network")
        if network is None:
            return finish(Outcome.UNKNOWN, "network_requirement_unknown")
        if network != "air_gapped":
            return finish(Outcome.SKIPPED, "air_gap_not_requested")
        selected_boundary = fact("/workload/isolation_boundary_id")
        if selected_boundary is None:
            return finish(Outcome.UNKNOWN, "isolation_boundary_unknown")
        if selected_boundary != self._boundary:
            return finish(Outcome.UNKNOWN, "isolation_boundary_mismatch")

        def add(sid, subject, outcome, reason):
            checks.append(Check(sid, subject, outcome, reason))

        for selection in enabled:
            sid = selection.id
            component = self._components.get(sid)
            if component is None:
                add(sid, "component", Outcome.UNKNOWN, "component_inventory_missing")
                continue
            for inventory in INVENTORIES:
                complete = fact(inventory_path(self._boundary, sid, inventory,
                                               inventory_entries(component, inventory)))
                add(sid, inventory, Outcome.PASS if complete is True else Outcome.UNKNOWN,
                    "inventory_complete" if complete is True else "inventory_coverage_unknown")
            for endpoint in sorted(component["runtime_endpoint_ids"]):
                inside = fact(answer_path(self._boundary, "endpoints", endpoint, "inside_boundary"))
                add(sid, "endpoint:" + endpoint,
                    Outcome.PASS if inside is True else Outcome.FAIL if inside is False else Outcome.UNKNOWN,
                    "runtime_endpoint_inside" if inside is True else
                    "runtime_endpoint_outside" if inside is False else "endpoint_membership_unknown")
            for connection in sorted(component["connections"], key=lambda item: item["id"]):
                prefix = ("components", sid, "connections", connection["id"])
                state = fact(answer_path(self._boundary, *prefix, "state"))
                lifecycle = fact(answer_path(self._boundary, *prefix, "lifecycle"))
                destination = fact(answer_path(self._boundary, *prefix, "destination_id"))
                inside = (fact(answer_path(self._boundary, "endpoints", destination, "inside_boundary"))
                          if destination is not None else None)
                if state == "disabled":
                    outcome, reason = Outcome.SKIPPED, "connection_disabled"
                elif lifecycle == "provisioning":
                    outcome, reason = Outcome.SKIPPED, "provisioning_only_connection"
                elif inside is True:
                    outcome, reason = Outcome.PASS, "connection_stays_inside"
                elif state == "enabled" and lifecycle == "runtime" and inside is False:
                    outcome, reason = Outcome.FAIL, "enabled_runtime_egress"
                else:
                    outcome, reason = Outcome.UNKNOWN, "connection_scope_or_state_unknown"
                add(sid, "connection:" + connection["id"], outcome, reason)
            for artifact in sorted(component["runtime_artifacts"], key=lambda item: item["id"]):
                present = fact(answer_path(self._boundary, "components", sid, "runtime_artifacts",
                                           artifact["id"], artifact["sha256"], "present_inside_boundary"))
                add(sid, "artifact:" + artifact["id"],
                    Outcome.PASS if present is True else Outcome.FAIL if present is False else Outcome.UNKNOWN,
                    "exact_runtime_artifact_ready" if present is True else
                    "exact_runtime_artifact_not_ready" if present is False else "artifact_readiness_unknown")
        outcomes = {check.outcome for check in checks}
        if Outcome.FAIL in outcomes:
            return finish(Outcome.FAIL, "isolation_counterexample")
        if Outcome.UNKNOWN in outcomes:
            return finish(Outcome.UNKNOWN, "isolation_evidence_incomplete")
        return finish(Outcome.PASS, "all_enabled_footprints_inside")
