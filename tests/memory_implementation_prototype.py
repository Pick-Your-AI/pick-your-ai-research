"""Versioned synthetic M1/W-R11 evaluation over caller-qualified memory facts.

This normalized Python interface is not a frozen Build reader, wire format,
catalog resolver or evidence authenticator. The caller must validate the full
Build/references, establish the complete selection inventory, resolve source
conflicts, and qualify each fact for the exact declared configuration and
recovery requirement. No kind or backing label supplies a recovery fact.

The existential implementation requirement is separate from all-enabled
selection rules, authorization, retention and deletion checks. Its pass is
only a witness for the stated recovery scope, never a whole-build verdict.
"""

from dataclasses import dataclass

from tests.selection_quantifier_prototype import Outcome, Selection, validate_identities
from tests.t0_answer_state_prototype import (
    Answer,
    AnswerRule,
    AnswerRuleResult,
    PredicateResult,
    RulePolicy,
    State,
    evaluate_answer_rule,
    pointer_tokens,
)


PROPOSAL_VERSION = "memory-implementation/0.1.0"


def _text(value, label):
    if type(value) is not str or not value or value != value.strip():
        raise ValueError(label + " must be nonempty exact text")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise ValueError(label + " must contain valid Unicode scalars") from error
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(label + " must not contain control characters")


def _answer(value, label, check_value):
    if type(value) is not Answer or type(value.state) is not State:
        raise ValueError(label + " must retain a typed Answer")
    if value.source is not None:
        _text(value.source, label + " source")
    if value.source_path is not None:
        _text(value.source_path, label + " path")
        pointer_tokens(value.source_path)
    if value.state is State.PROVIDED:
        check_value(value.value)
    elif value.value is not None:
        raise ValueError(label + " cannot retain an unresolved answer value")


def _predicate(value, label):
    if type(value) is not PredicateResult:
        raise ValueError(label + " must retain a typed PredicateResult")
    if value.source_path is not None:
        _text(value.source_path, label + " path")
        pointer_tokens(value.source_path)


@dataclass(frozen=True, slots=True)
class RecoveryEvidence:
    """One conflict-resolved fact, bound to exact caller-reviewed identities.

    The implementation, actual owner and need class are bound explicitly.
    Keys identify the requirement (including purpose/subject/recovery boundary
    and revision), selected configuration and retained-layer inventory. They
    are not content, URLs or a declaration that the evidence is authentic.
    Eligibility is separately qualified by the caller; the evidence identifier
    alone supplies no eligibility. A negative fact may be a scoped
    counterexample without a complete layer inventory; a positive needs one.
    """

    implementation_id: str
    owner_selection_id: str | None
    memory_need: str
    requirement_key: str
    configuration_key: str
    layer_inventory_key: str
    evidence_id: str
    eligible: PredicateResult
    supports_recovery: PredicateResult

    def __post_init__(self):
        for name in (
            "implementation_id", "requirement_key", "configuration_key",
            "layer_inventory_key", "evidence_id"
        ):
            _text(getattr(self, name), "recovery " + name)
        if self.owner_selection_id is not None:
            _text(self.owner_selection_id, "recovery owner selection")
        if type(self.memory_need) is not str or self.memory_need not in {"session", "persistent"}:
            raise ValueError("recovery memory need must be session or persistent")
        _predicate(self.eligible, "recovery eligibility")
        _predicate(self.supports_recovery, "recovery support")


@dataclass(frozen=True, slots=True)
class MemoryImplementation:
    """A declared path, with actual selected owner only where one exists.

    Application-owned implementations have no invented selection. Framework
    and store owners bind an exact selection of that kind. Related resources
    belong in the reviewed configuration identity; M2/authorization and other
    per-selection checks are independent of this requirement witness.
    """

    id: str
    via: str
    owner_selection_id: str | None
    configuration: Answer
    layer_inventory: Answer
    layers_complete: PredicateResult
    recovery: RecoveryEvidence | None

    def __post_init__(self):
        _text(self.id, "implementation id")
        if type(self.via) is not str or self.via not in {
            "application", "agent_framework", "memory_store"
        }:
            raise ValueError("implementation via must name a declared implementation path")
        if self.via == "application":
            if self.owner_selection_id is not None:
                raise ValueError("application memory must not invent an owner selection")
        else:
            _text(self.owner_selection_id, "implementation owner selection")
        _answer(self.configuration, "configuration", lambda x: _text(x, "configuration key"))
        _answer(self.layer_inventory, "layer inventory", lambda x: _text(x, "layer inventory key"))
        _predicate(self.layers_complete, "layer completeness")
        if self.recovery is not None and type(self.recovery) is not RecoveryEvidence:
            raise ValueError("recovery must be a scoped RecoveryEvidence record or missing")


@dataclass(frozen=True, slots=True)
class MemoryRequirementRecord:
    """Explicit version and normalized inputs; no defaults assert completeness.

    Provided need is none/session/persistent. Provided requirement is an exact
    caller-reviewed recovery-scope key. Provided declaration is a tuple of
    MemoryImplementation records; only an independently qualified complete
    declaration can prove that an absent witness cannot exist outside it.
    """

    proposal_version: str
    need: Answer
    requirement: Answer
    declaration: Answer
    declaration_complete: PredicateResult
    selections: tuple[Selection, ...]
    selection_inventory_complete: bool


@dataclass(frozen=True, slots=True)
class ImplementationFinding:
    implementation_id: str
    owner_selection_id: str | None
    outcome: Outcome
    reason: str
    answer_state: State
    source_path: str | None
    evidence_id: str | None = None


@dataclass(frozen=True, slots=True)
class MemoryRequirementResult:
    proposal_version: str
    rule: AnswerRuleResult
    on_unknown: str
    reason: str
    responsible_state: State
    source_path: str | None
    findings: tuple[ImplementationFinding, ...]

    def __bool__(self):
        raise TypeError("memory results have no implicit Boolean value; inspect rule.outcome")


def _preflight(record):
    if type(record) is not MemoryRequirementRecord:
        raise ValueError("expected a normalized MemoryRequirementRecord")
    if type(record.proposal_version) is not str or record.proposal_version != PROPOSAL_VERSION:
        raise ValueError("unsupported memory implementation proposal version")
    if record.selection_inventory_complete is not True:
        raise ValueError("memory evaluation requires a complete validated selection inventory")
    if type(record.selections) is not tuple or any(
        type(selection) is not Selection for selection in record.selections
    ):
        raise ValueError("selection inventory must be a tuple of Selection records")
    for selection in record.selections:
        for field in ("id", "kind", "role"):
            _text(getattr(selection, field), "selection " + field)
        if type(selection.enabled) is not bool:
            raise ValueError("selection enabled must be an exact Boolean")
    # This deliberately includes disabled and unrelated selections.
    validate_identities(record.selections)
    by_id = {selection.id: selection for selection in record.selections}

    def need(value):
        if type(value) is not str or value not in {"none", "session", "persistent"}:
            raise ValueError("provided memory need must be none, session or persistent")

    def declaration(value):
        if type(value) is not tuple or any(type(item) is not MemoryImplementation for item in value):
            raise ValueError("provided declaration must be a tuple of MemoryImplementation records")
        ids = set()
        for item in value:
            if item.id in ids:
                raise ValueError("duplicate memory implementation id: " + item.id)
            ids.add(item.id)
            if item.owner_selection_id is not None:
                owner = by_id.get(item.owner_selection_id)
                if owner is None or owner.kind != item.via:
                    raise ValueError("implementation owner must resolve to its exact selected kind")

    _answer(record.need, "memory need", need)
    _answer(record.requirement, "recovery requirement", lambda x: _text(x, "requirement key"))
    _answer(record.declaration, "memory declaration", declaration)
    _predicate(record.declaration_complete, "declaration completeness")
    return by_id


def _unknown(state, path):
    # An N/A implementation/configuration/evidence answer cannot waive a known
    # required implementation. Retain its original state in the detailed result;
    # the derived required assertion remains unresolved at the typed boundary.
    return PredicateResult(
        State.PROVIDED if state is State.NOT_APPLICABLE else state, None, path
    )


def _finding(item, outcome, reason, fact, evidence_id=None):
    return ImplementationFinding(
        item.id, item.owner_selection_id, outcome, reason,
        fact.state, fact.source_path, evidence_id,
    )


def _evaluate_implementation(item, need, requirement, by_id):
    if item.owner_selection_id is not None and not by_id[item.owner_selection_id].enabled:
        return _finding(
            item, Outcome.SKIPPED, "owner_selection_disabled",
            PredicateResult(State.PROVIDED, False),
        )
    for field, answer in (
        ("configuration", item.configuration), ("layer_inventory", item.layer_inventory)
    ):
        if answer.state is not State.PROVIDED:
            return _finding(item, Outcome.UNKNOWN, field + "_unresolved", answer)
    evidence = item.recovery
    if evidence is None:
        return _finding(
            item, Outcome.UNKNOWN, "recovery_evidence_missing",
            PredicateResult(State.MISSING, None),
        )
    if (
        evidence.implementation_id != item.id
        or evidence.owner_selection_id != item.owner_selection_id
        or evidence.memory_need != need
        or evidence.requirement_key != requirement
        or evidence.configuration_key != item.configuration.value
        or evidence.layer_inventory_key != item.layer_inventory.value
    ):
        return _finding(
            item, Outcome.UNKNOWN, "recovery_evidence_scope_mismatch",
            PredicateResult(State.PROVIDED, None, evidence.eligible.source_path),
            evidence.evidence_id,
        )
    if evidence.eligible.compatibility_value() is not True:
        return _finding(
            item, Outcome.UNKNOWN, "recovery_evidence_not_eligible",
            evidence.eligible, evidence.evidence_id,
        )
    support = evidence.supports_recovery
    if support.compatibility_value() is False:
        return _finding(
            item, Outcome.FAIL, "recovery_scope_not_supported", support, evidence.evidence_id
        )
    if support.compatibility_value() is not True:
        return _finding(
            item, Outcome.UNKNOWN, "recovery_support_unresolved", support, evidence.evidence_id
        )
    if item.layers_complete.compatibility_value() is not True:
        return _finding(
            item, Outcome.UNKNOWN, "layer_inventory_not_complete",
            item.layers_complete, evidence.evidence_id,
        )
    return _finding(
        item, Outcome.PASS, "recovery_scope_supported", support, evidence.evidence_id
    )


def evaluate_memory_requirement(record, *, policy):
    """Evaluate a scoped existential requirement, retaining every path finding.

    W-R11's recommendation skips an unresolved need answer. M1's compatibility
    check retains it as unknown. Once the need is known, required inputs remain
    unknown instead of becoming a recommendation skip. Known complete absence
    fails before an unrelated missing recovery-scope operand. Positive witness
    does not require exhaustive alternative paths; negative absence does.
    """
    by_id = _preflight(record)
    if type(policy) is not RulePolicy:
        raise ValueError("memory evaluation must declare a typed rule policy")
    rule_id, severity, on_unknown = (
        ("W-R11", "warning", "defer")
        if policy is RulePolicy.RECOMMENDATION
        else ("rule.t4.memory.persistence.required", "error", "review")
    )
    findings = ()
    reason = "not_evaluated"
    responsible_state, source_path = record.need.state, record.need.source_path

    def applicable():
        return PredicateResult(
            record.need.state,
            record.need.value in {"session", "persistent"} if record.need.provided else None,
            record.need.source_path,
        )

    def assertion():
        nonlocal findings, reason, responsible_state, source_path

        def unresolved(why, fact):
            nonlocal reason, responsible_state, source_path
            reason, responsible_state, source_path = why, fact.state, fact.source_path
            return _unknown(fact.state, fact.source_path)

        declaration = record.declaration
        if declaration.state is not State.PROVIDED:
            return unresolved("memory_declaration_unresolved", declaration)
        items = tuple(sorted(declaration.value, key=lambda item: item.id))
        active = tuple(
            item for item in items
            if item.owner_selection_id is None or by_id[item.owner_selection_id].enabled
        )
        complete = record.declaration_complete.compatibility_value() is True
        if not active:
            findings = tuple(
                _finding(
                    item, Outcome.SKIPPED, "owner_selection_disabled",
                    PredicateResult(State.PROVIDED, False),
                )
                for item in items
            )
            if not complete:
                return unresolved("implementation_inventory_not_complete", record.declaration_complete)
            reason = "memory_implementation_missing"
            responsible_state, source_path = State.PROVIDED, declaration.source_path
            return PredicateResult(State.PROVIDED, False, source_path)
        if record.requirement.state is not State.PROVIDED:
            findings = tuple(
                _finding(
                    item, Outcome.SKIPPED, "owner_selection_disabled",
                    PredicateResult(State.PROVIDED, False),
                )
                if item.owner_selection_id is not None and not by_id[item.owner_selection_id].enabled
                else _finding(
                    item, Outcome.UNKNOWN, "required_recovery_scope_unresolved",
                    record.requirement,
                )
                for item in items
            )
            return unresolved("required_recovery_scope_unresolved", record.requirement)
        findings = tuple(
            _evaluate_implementation(item, record.need.value, record.requirement.value, by_id)
            for item in items
        )
        witness = next((item for item in findings if item.outcome is Outcome.PASS), None)
        if witness is not None:
            reason = "memory_implementation_witness"
            responsible_state, source_path = witness.answer_state, witness.source_path
            return PredicateResult(State.PROVIDED, True, source_path)
        unresolved_finding = next(
            (item for item in findings if item.outcome is Outcome.UNKNOWN), None
        )
        if unresolved_finding is not None:
            reason = "memory_implementation_unknown"
            responsible_state = unresolved_finding.answer_state
            source_path = unresolved_finding.source_path
            return _unknown(responsible_state, source_path)
        if not complete:
            return unresolved("implementation_inventory_not_complete", record.declaration_complete)
        reason = "memory_capability_mismatch"
        responsible_state, source_path = State.PROVIDED, declaration.source_path
        return PredicateResult(State.PROVIDED, False, source_path)

    terminal = evaluate_answer_rule(AnswerRule(rule_id, severity, policy, applicable, assertion))
    if terminal.position == "applies_when":
        reason = terminal.reason
        responsible_state, source_path = terminal.answer_state, terminal.source_path
    return MemoryRequirementResult(
        PROPOSAL_VERSION, terminal, on_unknown, reason,
        responsible_state, source_path, findings,
    )
