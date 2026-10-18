"""Synthetic CTX-01/02 experiment over normalized facts, not a contract reader."""

from dataclasses import dataclass
from enum import StrEnum


class Outcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"


class Semantics(StrEnum):
    SHARED = "shared"
    SEPARATE = "separate"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TokenRange:
    lower: int
    upper: int


@dataclass(frozen=True, slots=True)
class Budget:
    semantics: Semantics
    input_tokens: TokenRange | None
    reserved_output: int | None
    output_cap: int | None
    shared_cap: int | None = None
    input_cap: int | None = None
    policy_total_cap: int | None = None
    enabled: bool = True
    tuple_matches: bool = True


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    lower: Outcome
    upper: Outcome


@dataclass(frozen=True, slots=True)
class Result:
    outcome: Outcome
    may_not_fit: bool
    checks: tuple[Check, ...]


def compare(demand: int | None, limit: int | None) -> Outcome:
    if demand is None or limit is None:
        return Outcome.UNKNOWN
    return Outcome.PASS if demand <= limit else Outcome.FAIL


def combine(outcomes: tuple[Outcome, ...]) -> Outcome:
    applicable = set(outcomes) - {Outcome.SKIPPED}
    if Outcome.FAIL in applicable:
        return Outcome.FAIL
    if Outcome.UNKNOWN in applicable:
        return Outcome.UNKNOWN
    return Outcome.PASS if applicable else Outcome.SKIPPED


def evaluate(budget: Budget) -> Result:
    if not budget.enabled:
        return Result(Outcome.SKIPPED, False, ())
    if not budget.tuple_matches:
        return Result(Outcome.UNKNOWN, False, ())

    lower = budget.input_tokens.lower if budget.input_tokens is not None else None
    upper = budget.input_tokens.upper if budget.input_tokens is not None else None
    output = budget.reserved_output
    total_lower = lower + output if lower is not None and output is not None else None
    total_upper = upper + output if upper is not None and output is not None else None
    output_result = compare(output, budget.output_cap)
    checks = [Check("output", output_result, output_result)]

    match budget.semantics:
        case Semantics.SHARED:
            checks.append(
                Check(
                    "combined",
                    compare(total_lower, budget.shared_cap),
                    compare(total_upper, budget.shared_cap),
                )
            )
        case Semantics.SEPARATE:
            checks.append(Check("combined", Outcome.SKIPPED, Outcome.SKIPPED))
        case Semantics.UNKNOWN:
            checks.append(Check("combined", Outcome.UNKNOWN, Outcome.UNKNOWN))

    if budget.input_cap is not None or budget.semantics == Semantics.SEPARATE:
        checks.append(
            Check(
                "input",
                compare(lower, budget.input_cap),
                compare(upper, budget.input_cap),
            )
        )

    if budget.policy_total_cap is not None:
        checks.append(
            Check(
                "policy_total",
                compare(total_lower, budget.policy_total_cap),
                compare(total_upper, budget.policy_total_cap),
            )
        )
    outcome = combine(tuple(check.upper for check in checks))
    lower_outcome = combine(tuple(check.lower for check in checks))
    return Result(
        outcome,
        outcome == Outcome.FAIL and lower_outcome != Outcome.FAIL,
        tuple(checks),
    )


def effective_limit(
    native: int | None,
    *,
    extension: int | None = None,
    extension_evidenced: bool = False,
    runtime_ceiling: int | None = None,
) -> int | None:
    if native is None:
        return None
    limit = extension if extension_evidenced and extension is not None else native
    return min(limit, runtime_ceiling) if runtime_ceiling is not None else limit
