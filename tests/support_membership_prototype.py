"""Synthetic CD-3 support-list mechanics over a normalized evidence cohort.

Source reading, exact tuple/version/condition matching and authority ordering
happen before this experiment. `eligible` must describe that actual scoped
review; a list or completeness marker does not establish eligibility by itself.
Opposite claims retained here have equal rank after that review. These records
and reason strings are not a contract extension or a catalog source reader.
"""

from dataclasses import dataclass
from enum import StrEnum


class Outcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"


class Requirement(StrEnum):
    ANY = "any"
    ALL = "all"


@dataclass(frozen=True, slots=True)
class Evidence:
    source_id: str
    eligible: bool | None
    supported: frozenset[str] | None
    exhaustive: bool | None = None
    unsupported: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class Finding:
    value: str
    outcome: Outcome
    reason: str
    disputed: bool = False


@dataclass(frozen=True, slots=True)
class Decision:
    outcome: Outcome
    reason: str
    source_id: str
    findings: tuple[Finding, ...] = ()
    disputed: bool = False
    evidence_label: str = "unverified"


def normalized_fact(value: bool | None) -> bool | None:
    if value is not True and value is not False and value is not None:
        raise ValueError("evidence markers must be normalized bool or None")
    return value


def member(value: str, evidence: Evidence) -> Finding:
    positive = evidence.supported is not None and value in evidence.supported
    explicit_negative = value in evidence.unsupported
    if positive and explicit_negative:
        return Finding(value, Outcome.UNKNOWN, "opposite_equal_rank_claims", True)
    if positive:
        return Finding(value, Outcome.PASS, "documented_member")
    if explicit_negative:
        return Finding(value, Outcome.FAIL, "explicit_unsupported")
    if evidence.supported is None:
        return Finding(value, Outcome.UNKNOWN, "support_list_missing")
    if evidence.exhaustive is True:
        return Finding(value, Outcome.FAIL, "exhaustive_absence")
    return Finding(value, Outcome.UNKNOWN, "unmarked_absence")


def evaluate(
    requested: frozenset[str] | None,
    evidence: Evidence,
    requirement: Requirement = Requirement.ANY,
    *,
    applicable: bool | None = True,
) -> Decision:
    normalized_fact(applicable)
    normalized_fact(evidence.eligible)
    normalized_fact(evidence.exhaustive)
    if requirement not in (Requirement.ANY, Requirement.ALL):
        raise ValueError("requirement must be any or all")
    if applicable is False:
        return Decision(Outcome.SKIPPED, "not_applicable", evidence.source_id)
    if applicable is None:
        return Decision(Outcome.UNKNOWN, "applicability_unknown", evidence.source_id)
    if requested is None:
        return Decision(Outcome.UNKNOWN, "requirement_unknown", evidence.source_id)
    if not requested:
        raise ValueError("an applicable membership query needs a nonempty requirement")
    if evidence.eligible is not True:
        return Decision(Outcome.UNKNOWN, "no_eligible_evidence", evidence.source_id)

    findings = tuple(member(value, evidence) for value in sorted(requested))
    outcomes = {finding.outcome for finding in findings}
    if requirement == Requirement.ANY:
        outcome = (
            Outcome.PASS
            if Outcome.PASS in outcomes
            else Outcome.UNKNOWN
            if Outcome.UNKNOWN in outcomes
            else Outcome.FAIL
        )
    else:
        outcome = (
            Outcome.FAIL
            if Outcome.FAIL in outcomes
            else Outcome.UNKNOWN
            if Outcome.UNKNOWN in outcomes
            else Outcome.PASS
        )
    return Decision(
        outcome,
        f"{requirement}_membership",
        evidence.source_id,
        findings,
        any(finding.disputed for finding in findings),
    )
