"""Test-only CD-7 presentation and declared-dependency evaluation boundary.

Every call inspects the actual pinned bytes through cd7-consumer-0.1. This
normalized local API is not a wire format, migration, source admission policy,
or substitute for a rule's reviewed complete dependency declaration. A retained
historical result is opaque: it is neither executed nor made current here.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
import re

from selection_quantifier_prototype import fact
import t0_cd7_consumer_prototype as consumer
from t0_historical_replay_prototype import ReplayResult

VERSION = "cd7-diagnostics-0.1"
IDENTIFIER = re.compile(r"[a-z][a-z0-9._:-]{2,119}")
RECORDS = ("catalog_snapshot", "pricebook")


class DiagnosticsError(ValueError):
    """An invalid local call, not an unknown compatibility result."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class Dependency:
    kind: str
    identity: str


@dataclass(frozen=True, slots=True)
class Diagnostic:
    record_kind: str
    record_id: str | None
    revision: int | None
    reason_code: str

    @property
    def message(self):
        record = self.record_kind
        if self.record_id is not None:
            record += " " + self.record_id
        if self.revision is not None:
            record += " revision " + str(self.revision)
        return "cannot be reproduced: " + record


@dataclass(frozen=True, slots=True)
class Inspection:
    proposal_version: str
    consumer_response_bytes: bytes = field(repr=False)
    diagnostics: tuple[Diagnostic, ...]
    historical_result: ReplayResult | None = field(repr=False)

    @property
    def qualification(self):
        return {"publication": "not_established", "source_use": "not_established",
                "current_compatibility": "not_established",
                "historical_authenticity": "not_established"}


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    severity: str
    dependencies: tuple[Dependency, ...]
    applies_when: Callable[[], bool | None]
    assertion: Callable[[], bool | None]


@dataclass(frozen=True, slots=True)
class RuleResult:
    rule_id: str
    severity: str
    outcome: str
    reason_code: str
    diagnostics: tuple[Diagnostic, ...] = ()
    disabled_dependencies: tuple[Dependency, ...] = ()


@dataclass(frozen=True, slots=True)
class Evaluation:
    inspection: Inspection
    rule_result: RuleResult


def _unique(values):
    return tuple(dict.fromkeys(values))


def _binding_diagnostic(kind, binding):
    if binding is None:
        return Diagnostic(kind, None, None, "pricebook_absent")
    return Diagnostic(kind, binding["id"], binding.get("revision"), binding["status"])


def _pair_diagnostic(packet):
    bindings = packet["bindings"]
    return Diagnostic("catalog_pricebook", "/".join(bindings[k]["id"] for k in RECORDS),
                      None, "rate_catalog_mismatch")


def _inspection(archive, request_bytes, build_bytes, sidecar_bytes, *,
                proposal_version, dispositions, historical_result):
    if type(proposal_version) is not str or proposal_version != VERSION:
        raise DiagnosticsError("unsupported_proposal_version")
    if historical_result is not None:
        if type(historical_result) is not ReplayResult:
            raise DiagnosticsError("invalid_historical_result")
        if (historical_result.original_build_bytes != build_bytes
                or historical_result.original_sidecar_bytes != sidecar_bytes):
            raise DiagnosticsError("historical_input_mismatch")
    # Do not accept an inspection dictionary or catch malformed inputs as
    # unresolved dependencies. The existing reader validates original bytes,
    # pins, identities, protocol, bounds and producer dispositions itself.
    response = consumer.inspect(archive, request_bytes, build_bytes, sidecar_bytes,
                                dispositions=dispositions)
    packet = consumer.wire(response, "x_t0_cd7_consumer_result")
    diagnostics = [
        _binding_diagnostic(kind, binding)
        for kind, binding in packet["bindings"].items()
        if binding is not None and binding["status"] != "resolved"
    ]
    diagnostics.extend(
        Diagnostic("selection", selected["selection_id"], None, selected["status"])
        for selected in packet["selections"]
        if selected["status"] not in {"resolved", "not_enabled", "snapshot_unresolved"}
    )
    if packet["pair"]["status"] == "rate_catalog_mismatch":
        diagnostics.append(_pair_diagnostic(packet))
    return Inspection(VERSION, response, _unique(diagnostics), historical_result), packet


def inspect(archive, request_bytes, build_bytes, sidecar_bytes=None, *,
            proposal_version, dispositions=None, historical_result=None):
    """Present specific record causes while preserving the original response.

    A missing optional Pricebook and a disabled selection are not global errors.
    Historical bytes/results remain available only in the caller's separately
    retained object; diagnostics contain identities and reason codes, not payloads.
    """
    result, _ = _inspection(archive, request_bytes, build_bytes, sidecar_bytes,
                            proposal_version=proposal_version, dispositions=dispositions,
                            historical_result=historical_result)
    return result


def _validate_rule(rule):
    if (type(rule) is not Rule or type(rule.id) is not str
            or not IDENTIFIER.fullmatch(rule.id)
            or type(rule.severity) is not str
            or rule.severity not in {"info", "warning", "error"}
            or type(rule.dependencies) is not tuple
            or not callable(rule.applies_when) or not callable(rule.assertion)):
        raise DiagnosticsError("invalid_rule")
    for dependency in rule.dependencies:
        if (type(dependency) is not Dependency or type(dependency.kind) is not str
                or type(dependency.identity) is not str):
            raise DiagnosticsError("invalid_dependency")
        if dependency.kind == "record":
            valid = dependency.identity in RECORDS
        elif dependency.kind == "selection":
            valid = bool(IDENTIFIER.fullmatch(dependency.identity))
        elif dependency.kind == "pair":
            valid = dependency.identity == "catalog_pricebook"
        else:
            valid = False
        if not valid:
            raise DiagnosticsError("invalid_dependency")
    if len(set(rule.dependencies)) != len(rule.dependencies):
        raise DiagnosticsError("duplicate_dependency")


def _dependency_state(dependency, packet):
    """Return exact unresolved causes and an independent known-disabled flag."""
    bindings = packet["bindings"]
    if dependency.kind == "record":
        binding = bindings[dependency.identity]
        if binding is not None and binding["status"] == "resolved":
            return (), False
        return (_binding_diagnostic(dependency.identity, binding),), False
    if dependency.kind == "selection":
        selected = next((s for s in packet["selections"]
                         if s["selection_id"] == dependency.identity), None)
        if selected is None:
            raise DiagnosticsError("unknown_selection_dependency")
        status = selected["status"]
        if status == "resolved":
            return (), False
        if status == "not_enabled":
            return (), True
        if status == "snapshot_unresolved":
            catalog = bindings["catalog_snapshot"]
            if catalog["status"] == "resolved":
                raise DiagnosticsError("inconsistent_inspection")
            return (_binding_diagnostic("catalog_snapshot", catalog),), False
        return (Diagnostic("selection", dependency.identity, None, status),), False
    status = packet["pair"]["status"]
    if status == "resolved":
        return (), False
    if status == "pricebook_absent":
        # The consumer's pair label describes optional absence first. A rule
        # explicitly requiring the pair still depends on the catalog too.
        return tuple(_binding_diagnostic(kind, binding)
                     for kind, binding in bindings.items()
                     if binding is None or binding["status"] != "resolved"), False
    if status == "rate_catalog_mismatch":
        return (_pair_diagnostic(packet),), False
    causes = tuple(_binding_diagnostic(kind, binding)
                   for kind, binding in bindings.items()
                   if binding is not None and binding["status"] != "resolved")
    if status != "incomplete" or not causes:
        raise DiagnosticsError("inconsistent_inspection")
    return causes, False


def evaluate(archive, request_bytes, build_bytes, sidecar_bytes=None, *,
             proposal_version, rule, dispositions=None, historical_result=None):
    """Inspect actual bytes, then gate both callbacks on declared dependencies.

    Unknown dependencies dominate known-disabled dependencies. A fully known
    disabled scope skips. An empty tuple is an explicitly independent rule;
    resolving the tuple alone never supplies a pass or default assertion.
    Callback failures propagate as execution errors, including DiagnosticsError.
    """
    _validate_rule(rule)
    inspection, packet = _inspection(
        archive, request_bytes, build_bytes, sidecar_bytes,
        proposal_version=proposal_version, dispositions=dispositions,
        historical_result=historical_result,
    )
    causes, disabled = [], []
    for dependency in rule.dependencies:
        diagnostics, not_enabled = _dependency_state(dependency, packet)
        causes.extend(diagnostics)
        if not_enabled:
            disabled.append(dependency)
    if causes:
        result = RuleResult(rule.id, rule.severity, "unknown", "dependency_unresolved",
                            _unique(causes), tuple(disabled))
    elif disabled:
        result = RuleResult(rule.id, rule.severity, "skipped", "not_enabled",
                            disabled_dependencies=tuple(disabled))
    else:
        applicable = fact(rule.applies_when())
        if applicable is False:
            outcome, reason = "skipped", "not_applicable"
        elif applicable is None:
            outcome, reason = "unknown", "applicability_unknown"
        else:
            assertion = fact(rule.assertion())
            if assertion is None:
                outcome, reason = "unknown", "eligible_evidence_missing"
            elif assertion is False:
                outcome, reason = "fail", "assertion_false"
            else:
                outcome, reason = "pass", "assertion_true"
        result = RuleResult(rule.id, rule.severity, outcome, reason)
    return Evaluation(inspection, result)
