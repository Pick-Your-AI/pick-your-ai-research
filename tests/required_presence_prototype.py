"""Synthetic CD-13 required-presence mode over normalized activation facts.

The caller supplies the complete, independently validated selection inventory
and eligible True/False/None activation for each entry. An explicit completeness
declaration is required; this module cannot establish completeness or evidence
eligibility from that declaration. It is not a Build reader, activation planner,
general predicate DSL, wire format or replacement for frozen v1.
"""

from dataclasses import dataclass

from tests.selection_quantifier_prototype import Outcome, validate_identities


def _text(value: str, label: str) -> None:
    if type(value) is not str or not value or value != value.strip():
        raise ValueError(label + " must be nonempty normalized text")


@dataclass(frozen=True, slots=True)
class PresenceSelection:
    """A selection identity with explicit, already-qualified activation.

    None means unresolved activation, never a disabled or absent selection.
    Full canonical schema/reference validation remains a caller precondition.
    """

    id: str
    kind: str
    role: str
    active: bool | None

    def __post_init__(self) -> None:
        for label in ("id", "kind", "role"):
            _text(getattr(self, label), "selection " + label)
        if self.active is not True and self.active is not False and self.active is not None:
            raise ValueError("activation must be exact True, False or None")


@dataclass(frozen=True, slots=True)
class PresenceRule:
    """Always require a kind, with an explicit exact role or any-role scope.

    This mode has no optional applicability or assertion callbacks. A known
    active matching selection witnesses presence, not compatibility or fitness.
    """

    id: str
    kind: str
    role: str | None
    severity: str

    def __post_init__(self) -> None:
        for label in ("id", "kind"):
            _text(getattr(self, label), "rule " + label)
        if self.role is not None:
            _text(self.role, "rule role")
        if type(self.severity) is not str or self.severity not in ("info", "warning", "error"):
            raise ValueError("rule severity must be info, warning or error")


@dataclass(frozen=True, slots=True)
class ActivationFinding:
    selection_id: str
    active: bool | None


@dataclass(frozen=True, slots=True)
class PresenceResult:
    rule_id: str
    kind: str
    role: str | None
    severity: str
    outcome: Outcome
    reason: str
    activations: tuple[ActivationFinding, ...]


def evaluate_required_presence(
    selections: tuple[PresenceSelection, ...],
    rule: PresenceRule,
    *,
    inventory_complete: bool,
) -> PresenceResult:
    """Check required presence without reusing a universal empty-scope skip.

    Malformed or undeclared/incomplete inventories are precondition errors,
    rather than evidence of absence. The True completeness declaration does
    not authenticate an inventory; callers must establish it independently.
    The existing strict identity/role policy applies to the entire inventory,
    including inactive, unresolved and unrelated-kind selections, before scope
    filtering. The disabled-alternative policy remains a separate decision.
    """
    if type(selections) is not tuple or any(type(s) is not PresenceSelection for s in selections):
        raise ValueError("presence inventory must be a tuple of PresenceSelection records")
    if type(rule) is not PresenceRule:
        raise ValueError("required presence needs a PresenceRule")
    if inventory_complete is not True:
        raise ValueError("required presence needs an explicitly complete normalized inventory")
    validate_identities(selections)
    activations = tuple(
        ActivationFinding(selection.id, selection.active)
        for selection in sorted(selections, key=lambda item: item.id)
        if selection.kind == rule.kind and (rule.role is None or selection.role == rule.role)
    )
    if any(finding.active is True for finding in activations):
        outcome, reason = Outcome.PASS, "selected"
    elif any(finding.active is None for finding in activations):
        outcome, reason = Outcome.UNKNOWN, "not_selected"
    else:
        outcome, reason = Outcome.FAIL, "not_selected"
    return PresenceResult(
        rule.id, rule.kind, rule.role, rule.severity, outcome, reason, activations
    )
