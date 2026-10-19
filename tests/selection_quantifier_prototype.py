"""Synthetic CD-13 experiment over normalized facts, not a contract/DSL reader.

Identity and role checks precede rule execution. Predicates receive each enabled
selection of the requested kind; they never resolve a single arbitrary match.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Outcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"


class SelectionIdentity(Protocol):
    """Only the identity fields consumed by the shared preflight."""

    @property
    def id(self) -> str: ...

    @property
    def kind(self) -> str: ...

    @property
    def role(self) -> str: ...


@dataclass(frozen=True, slots=True)
class Selection:
    id: str
    kind: str
    role: str
    enabled: bool = True


Predicate = Callable[[Selection], bool | None]


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    kind: str
    severity: str
    applies_when: Predicate
    assertion: Predicate


@dataclass(frozen=True, slots=True)
class Finding:
    selection_id: str
    outcome: Outcome
    reason: str


@dataclass(frozen=True, slots=True)
class Result:
    rule_id: str
    severity: str
    outcome: Outcome
    reason: str
    findings: tuple[Finding, ...]


class IdentityPreflightError(ValueError):
    """A typed identity rejection; historical ValueError callers still work.

    The diagnostic fields contain only the conflicting normalized identity.
    Exception messages remain diagnostic text, never a result parsing API.
    """

    def __init__(
        self,
        message: str,
        *,
        reason_code: str,
        selection_id: str | None = None,
        kind: str | None = None,
        role: str | None = None,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.selection_id = selection_id
        self.kind = kind
        self.role = role


def validate_identities(selections: tuple[SelectionIdentity, ...]) -> None:
    """Apply the frozen protocol's build-wide identity/role precondition.

    Disabled entries still have identities and roles. Disabling one must not
    hide an ambiguous build that becomes ambiguous again when it is enabled.
    This is only the identity slice, not full schema/referential validation.
    """
    identities: set[str] = set()
    roles: set[tuple[str, str]] = set()
    for selection in selections:
        if selection.id in identities:
            raise IdentityPreflightError(
                f"duplicate selection id: {selection.id}",
                reason_code="duplicate_selection_id",
                selection_id=selection.id,
            )
        identities.add(selection.id)
        key = (selection.kind, selection.role)
        if key in roles:
            raise IdentityPreflightError(
                f"ambiguous kind/role: {selection.kind}/{selection.role}",
                reason_code="ambiguous_selection_role",
                kind=selection.kind,
                role=selection.role,
            )
        roles.add(key)


def fact(value: bool | None) -> bool | None:
    """Do not coerce strings, numbers or missing evidence into true/false."""
    if value is not True and value is not False and value is not None:
        raise ValueError("predicate must return a normalized bool or None")
    return value


def evaluate(selections: tuple[Selection, ...], rule: Rule) -> Result:
    validate_identities(selections)
    selected = sorted(
        (s for s in selections if s.enabled and s.kind == rule.kind),
        key=lambda s: s.id,
    )
    findings = []
    for selection in selected:
        applicable = fact(rule.applies_when(selection))
        if applicable is False:
            outcome, reason = Outcome.SKIPPED, "not_applicable"
        elif applicable is None:
            outcome, reason = Outcome.UNKNOWN, "applicability_unknown"
        else:
            assertion = fact(rule.assertion(selection))
            if assertion is None:
                outcome, reason = Outcome.UNKNOWN, "eligible_evidence_missing"
            elif assertion is False:
                outcome, reason = Outcome.FAIL, "assertion_false"
            else:
                outcome, reason = Outcome.PASS, "assertion_true"
        findings.append(Finding(selection.id, outcome, reason))

    outcomes = {finding.outcome for finding in findings}
    if Outcome.FAIL in outcomes:
        outcome, reason = Outcome.FAIL, "counterexample"
    elif Outcome.UNKNOWN in outcomes:
        outcome, reason = Outcome.UNKNOWN, "unresolved_selection"
    elif Outcome.PASS in outcomes:
        outcome, reason = Outcome.PASS, "all_applicable_pass"
    elif findings:
        outcome, reason = Outcome.SKIPPED, "none_applicable"
    else:
        outcome, reason = Outcome.SKIPPED, "no_enabled_selections"
    return Result(rule.id, rule.severity, outcome, reason, tuple(findings))
