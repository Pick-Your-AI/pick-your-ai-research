"""Explicit synthetic CD-13 identity-rejection result proposal.

This boundary receives normalized records, not untrusted Build/answer bytes. It
keeps the strict build-wide identity policy and delegates evaluated findings to
the existing universal reducer. It is neither a production wire reader nor a
source, schema, reference, evidence or inventory-completeness validator.
"""

from tests.selection_quantifier_prototype import (
    IdentityPreflightError,
    Rule,
    Selection,
    evaluate,
    validate_identities,
)


PROPOSAL_VERSION = "cd13-result-0.1"
IDENTITY_POLICY = "strict_build_wide"


def _normalized_arguments(selections: tuple[Selection, ...], rule: Rule) -> None:
    """Check this Python API's shape, not canonical Build or evidence validity."""
    if type(selections) is not tuple or any(type(s) is not Selection for s in selections):
        raise ValueError("result boundary requires a tuple of normalized Selection records")
    if type(rule) is not Rule:
        raise ValueError("result boundary requires a normalized Rule record")
    for value in (rule.id, rule.kind):
        if type(value) is not str or not value or value != value.strip():
            raise ValueError("rule identity must be nonempty normalized text")
    if type(rule.severity) is not str or rule.severity not in ("info", "warning", "error"):
        raise ValueError("rule severity must be info, warning or error")
    if not callable(rule.applies_when) or not callable(rule.assertion):
        raise ValueError("rule predicates must be callable")
    for selection in selections:
        for value in (selection.id, selection.kind, selection.role):
            if type(value) is not str or not value or value != value.strip():
                raise ValueError("selection identity must be nonempty normalized text")
        if type(selection.enabled) is not bool:
            raise ValueError("selection activation must be an exact Boolean")


def evaluate_structured(
    selections: tuple[Selection, ...],
    rule: Rule,
    *,
    proposal_version: str,
) -> dict:
    """Return one explicit rejection or the unchanged evaluated rule result.

    Callers must separately supply normalized Selection/Rule records and all
    required schema/reference/eligibility preconditions. Unsupported or omitted
    proposal versions and programming/predicate failures are not reclassified
    as identity rejection. No exception text or partial findings are published.
    """
    if type(proposal_version) is not str or proposal_version != PROPOSAL_VERSION:
        raise ValueError("unsupported CD-13 result proposal version")
    _normalized_arguments(selections, rule)

    # Catch only this completed preflight, before invoking any rule callback.
    # Keeping evaluate() outside the handler is intentional: even a callback
    # raising IdentityPreflightError remains an execution error.
    try:
        validate_identities(selections)
    except IdentityPreflightError as error:
        if error.reason_code == "duplicate_selection_id":
            diagnostic = {
                "reason_code": error.reason_code,
                "selection_id": error.selection_id,
            }
        elif error.reason_code == "ambiguous_selection_role":
            diagnostic = {
                "reason_code": error.reason_code,
                "kind": error.kind,
                "role": error.role,
            }
        else:
            # An unrecognized future preflight cannot acquire an invented code.
            raise
        return {
            "proposal_version": PROPOSAL_VERSION,
            "identity_policy": IDENTITY_POLICY,
            "status": "rejected",
            "phase": "identity_preflight",
            "rule_id": rule.id,
            "severity": rule.severity,
            "rejection": diagnostic,
        }

    result = evaluate(selections, rule)
    return {
        "proposal_version": PROPOSAL_VERSION,
        "identity_policy": IDENTITY_POLICY,
        "status": "evaluated",
        "result": {
            "rule_id": result.rule_id,
            "severity": result.severity,
            "outcome": result.outcome.value,
            "reason": result.reason,
            "findings": [
                {
                    "selection_id": finding.selection_id,
                    "outcome": finding.outcome.value,
                    "reason": finding.reason,
                }
                for finding in result.findings
            ],
        },
    }
