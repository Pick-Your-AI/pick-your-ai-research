"""Synthetic CD-3 evidence labels; source qualification is supplied by the caller.

The unchanged membership reducer decides outcomes. This successor annotates only
actual member claims from an eligible cohort explicitly qualified as checked-only.
No label means this experiment makes no grade assertion; it never means verified.
Historical cd3-0.2 results remain readable through their original reader.
"""

from dataclasses import dataclass
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from tests.support_membership_binding_prototype import (
    SupportQueryRecord, decode, validate,
)
from tests.support_membership_prototype import (
    Decision, Evidence, Outcome, Requirement, evaluate as reduce_membership,
    normalized_fact,
)


@dataclass(frozen=True, slots=True)
class EvidenceFinding:
    value: str
    outcome: Outcome
    reason: str
    disputed: bool
    evidence_label: str | None


@dataclass(frozen=True, slots=True)
class EvidenceDecision:
    outcome: Outcome
    reason: str
    source_id: str
    findings: tuple[EvidenceFinding, ...]
    disputed: bool
    evidence_label: str | None


CLAIM_REASONS = frozenset((
    "documented_member", "explicit_unsupported", "exhaustive_absence",
    "opposite_equal_rank_claims",
))


def label_decision(decision: Decision, *, cohort_checked_only: bool | None) -> EvidenceDecision:
    """Qualify retained claims without turning missing evidence into a grade.

    True qualifies the entire normalized cohort as source-checked only. False
    or unresolved does not identify another grade. Unknown aggregate verdicts
    have no label; any checked-only member claims remain labeled individually.
    """
    normalized_fact(cohort_checked_only)
    findings = tuple(EvidenceFinding(
        finding.value, finding.outcome, finding.reason, finding.disputed,
        "unverified" if cohort_checked_only is True and finding.reason in CLAIM_REASONS else None,
    ) for finding in decision.findings)
    # A definitive verdict must actually rest on a qualified member witness or
    # counterexample. The label never comes from the legacy aggregate default.
    label = ("unverified" if decision.outcome in (Outcome.PASS, Outcome.FAIL)
             and any(finding.outcome == decision.outcome and
                     finding.evidence_label == "unverified" for finding in findings)
             else None)
    return EvidenceDecision(decision.outcome, decision.reason, decision.source_id,
                            findings, decision.disputed, label)


def evaluate(
    requested: frozenset[str] | None,
    evidence: Evidence,
    requirement: Requirement = Requirement.ANY,
    *,
    applicable: bool | None = True,
    requested_complete: bool | None = None,
    cohort_checked_only: bool | None = None,
) -> EvidenceDecision:
    """Explicit successor profile; eligibility alone never supplies a grade."""
    normalized_fact(cohort_checked_only)
    decision = reduce_membership(requested, evidence, requirement,
                                 applicable=applicable, requested_complete=requested_complete)
    return label_decision(decision, cohort_checked_only=cohort_checked_only)


SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "support-membership-evidence.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(SCHEMA)
RESULT = Draft202012Validator({"$ref": "#/$defs/result", "$defs": SCHEMA["$defs"]})


class SupportEvidenceQueryRecord(SupportQueryRecord):
    """Opt-in cd3-0.3 binding with a separate caller-established cohort grade.

    The caller's checked-only qualification is per invocation and independent
    of all four eligibility inputs. Neither input source strings nor a prior
    result can qualify themselves. This consistency reader admits no real
    sources, signatures, independent verification or production rule adapter.
    """

    _wire_validator = WIRE
    _result_validator = RESULT
    _proposal_version = "cd3-0.3"

    def evaluate(self, selected_scope, *, enabled, eligible_inputs=None,
                 cohort_checked_only=None):
        normalized_fact(cohort_checked_only)
        eligible, decision = self._evaluate_decision(
            selected_scope, enabled=enabled, eligible_inputs=eligible_inputs)
        labeled = label_decision(decision, cohort_checked_only=cohort_checked_only)
        return self._result_for(labeled, {
            "enabled": enabled, "selected_scope": selected_scope,
            "eligible_inputs": eligible, "cohort_checked_only": cohort_checked_only,
        })

    def verify_result(self, raw, selected_scope, *, enabled, eligible_inputs=None,
                      cohort_checked_only=None):
        """Recompute every label against the caller's current qualification."""
        result = decode(raw)
        validate(RESULT, result, "CD-3 result")
        expected = self.evaluate(selected_scope, enabled=enabled, eligible_inputs=eligible_inputs,
                                 cohort_checked_only=cohort_checked_only)
        if result != expected:
            raise ValueError("support result does not match retained inputs and caller context")
        return expected
