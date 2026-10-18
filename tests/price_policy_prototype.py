"""Synthetic #41 price-policy experiment over normalized facts, not a quote API.

Source parsing, validity-boundary interpretation, rights review, unit conversion
and account-condition evidence happen before these fixtures. None means missing
evidence. In particular, a true refreshed_for_query is supplied only after an
actual successful source/scope recheck; it is never inferred from captured_on.
The authority cohort is limited to billing/overview documents from one publisher;
cross-publisher authority and partially overlapping scopes are outside this model.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import IntEnum, StrEnum


class Outcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class Authority(IntEnum):
    OVERVIEW = 1
    BILLING = 2


@dataclass(frozen=True)
class Scope:
    item_id: str | None
    version: str | None
    provider: str | None
    meter: str | None
    billing_class: str | None
    currency: str | None
    region: str | None
    conditions: tuple[tuple[str, str | None], ...] | None


@dataclass(frozen=True)
class Rate:
    rate_id: str
    scope: Scope
    amount: Decimal | None
    effective_on: date | None
    captured_on: date
    valid_for_query: bool | None
    refreshed_for_query: bool | None
    display_allowed: bool | None
    authority: Authority = Authority.BILLING
    explicitly_global: bool = False

    def __post_init__(self) -> None:
        if self.explicitly_global and self.scope.region is not None:
            raise ValueError(
                "explicit global coverage has no conflicting regional restriction"
            )


@dataclass(frozen=True)
class Trace:
    rate_id: str
    outcome: Outcome
    reason: str


@dataclass(frozen=True)
class Decision:
    amount: Decimal | None
    currency: str | None
    selected_rate_ids: tuple[str, ...]
    disputed: bool
    permitted_history: tuple[Rate, ...]
    trace: tuple[Trace, ...]


def match_scope(request: Scope, rate: Rate) -> Outcome:
    """All compared quantities/conditions must already use the same semantics."""
    comparisons: list[Outcome] = []
    for field in (
        "item_id",
        "version",
        "provider",
        "meter",
        "billing_class",
        "currency",
    ):
        actual, expected = getattr(request, field), getattr(rate.scope, field)
        comparisons.append(
            Outcome.UNKNOWN
            if actual is None or expected is None
            else Outcome.PASS
            if actual == expected
            else Outcome.FAIL
        )
    if request.region is None:
        comparisons.append(Outcome.UNKNOWN)
    elif rate.explicitly_global:
        comparisons.append(Outcome.PASS)
    elif rate.scope.region is None:
        comparisons.append(Outcome.UNKNOWN)
    else:
        comparisons.append(
            Outcome.PASS if request.region == rate.scope.region else Outcome.FAIL
        )

    if request.conditions is None or rate.scope.conditions is None:
        comparisons.append(Outcome.UNKNOWN)
    else:
        actual_conditions, expected_conditions = (
            dict(request.conditions),
            dict(rate.scope.conditions),
        )
        if len(actual_conditions) != len(request.conditions) or len(
            expected_conditions
        ) != len(rate.scope.conditions):
            raise ValueError("duplicate condition keys are not normalized evidence")
        for key in actual_conditions.keys() | expected_conditions.keys():
            actual, expected = actual_conditions.get(key), expected_conditions.get(key)
            comparisons.append(
                Outcome.UNKNOWN
                if actual is None or expected is None
                else Outcome.PASS
                if actual == expected
                else Outcome.FAIL
            )
    if Outcome.FAIL in comparisons:
        return Outcome.FAIL
    return Outcome.UNKNOWN if Outcome.UNKNOWN in comparisons else Outcome.PASS


def choose_current_rate(request: Scope, rates: tuple[Rate, ...]) -> Decision:
    """Choose only within this proposal's fully normalized, eligible cohort.

    A disputed amount is a conservative budget input, not a confirmed charge.
    Retained observations keep their original identity/dates; their presence
    does not select a historical build's pinned rate or make a current quote.
    """
    if len({rate.rate_id for rate in rates}) != len(rates):
        raise ValueError("duplicate rate identity")
    candidates: list[Rate] = []
    history: list[Rate] = []
    trace: list[Trace] = []
    for rate in rates:
        matched = match_scope(request, rate)
        if matched != Outcome.PASS:
            trace.append(Trace(rate.rate_id, matched, "scope"))
            continue
        if rate.display_allowed is not True:
            trace.append(
                Trace(
                    rate.rate_id,
                    Outcome.FAIL if rate.display_allowed is False else Outcome.UNKNOWN,
                    "display_rights",
                )
            )
            continue
        if rate.amount is None:
            trace.append(Trace(rate.rate_id, Outcome.UNKNOWN, "amount"))
            continue
        if not rate.amount.is_finite() or rate.amount < 0:
            raise ValueError("amount must be finite and nonnegative")
        history.append(rate)
        if rate.valid_for_query is not True:
            trace.append(
                Trace(
                    rate.rate_id,
                    Outcome.FAIL if rate.valid_for_query is False else Outcome.UNKNOWN,
                    "validity",
                )
            )
            continue
        if rate.refreshed_for_query is not True:
            trace.append(Trace(rate.rate_id, Outcome.UNKNOWN, "refresh"))
            continue
        if rate.effective_on is None:
            trace.append(Trace(rate.rate_id, Outcome.UNKNOWN, "effective_date"))
            continue
        candidates.append(rate)

    if not candidates:
        return Decision(None, request.currency, (), False, tuple(history), tuple(trace))

    # Scope before effective date before authority. This bounded prototype only
    # orders exact-region versus explicitly-global scope; it does not invent a
    # total order over partially overlapping regional/account/volume scopes.
    def rank(rate: Rate) -> tuple[bool, date, Authority]:
        if rate.effective_on is None:
            raise ValueError("eligible rate is missing its effective date")
        return (not rate.explicitly_global, rate.effective_on, rate.authority)

    best_rank = max(map(rank, candidates))
    winners = [rate for rate in candidates if rank(rate) == best_rank]
    amounts = {rate.amount for rate in winners}
    amount = max(value for value in amounts if value is not None)
    selected = tuple(sorted(rate.rate_id for rate in winners))
    trace.extend(
        Trace(
            rate.rate_id, Outcome.PASS, "selected" if rate in winners else "superseded"
        )
        for rate in candidates
    )
    return Decision(
        amount,
        request.currency,
        selected,
        len(amounts) > 1,
        tuple(history),
        tuple(trace),
    )
