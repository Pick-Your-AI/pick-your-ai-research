"""Research-only arithmetic for #10's explicit-headroom proposal.

Inputs are scenario assertions, not evidence verified by this helper. No hardware
probe, workload, ResourceEstimate, calibration or executable #40 rule is produced.
Byte bounds must cover the same per-device/admission domain. Runtime/workspace,
adapters, co-residency and demand-versus-pool accounting are resolved upstream.
"""

from decimal import Decimal
from fractions import Fraction


def screen_memory(*, live_upper_bytes, capacity_lower_bytes, headroom,
                  capacity_basis, confidence_eligible, same_domain):
    """Compare conservative byte bounds with an explicitly stated reserve.

    capacity_basis is before_reserve or after_reserve. An already reduced engine
    pool is compared directly; reserve is never subtracted twice. headroom remains
    required for traceability in either basis. Booleans assert caller-provided
    confidence eligibility/domain agreement, not independent verification.
    Fraction arithmetic avoids binary float and Decimal-context boundary errors.
    """
    for name, value in (("live_upper_bytes", live_upper_bytes),
                        ("capacity_lower_bytes", capacity_lower_bytes)):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"{name} must be a nonnegative integer byte count")
    if capacity_lower_bytes == 0:
        raise ValueError("capacity_lower_bytes must be positive")
    if headroom is not None and (not isinstance(headroom, Decimal)
            or not headroom.is_finite() or not Decimal(0) <= headroom < Decimal(1)):
        raise ValueError("headroom must be a finite Decimal in [0, 1)")
    if capacity_basis not in (None, "before_reserve", "after_reserve"):
        raise ValueError("capacity_basis must explicitly identify reserve accounting")
    for value in (confidence_eligible, same_domain):
        if value is not None and type(value) is not bool:
            raise ValueError("eligibility and domain assertions must be bool or None")

    missing = [name for name, value in (
        ("live_upper_bytes", live_upper_bytes),
        ("capacity_lower_bytes", capacity_lower_bytes),
        ("headroom", headroom), ("capacity_basis", capacity_basis)) if value is None]
    if confidence_eligible is not True:
        missing.append("confidence eligibility not established")
    if same_domain is not True:
        missing.append("matching capacity/demand domain not established")
    result = {"classification": "conditional research arithmetic; not measured fit"}
    if missing:
        return {**result, "outcome": "unknown", "reasons": missing}

    capacity = Fraction(capacity_lower_bytes)
    budget = (capacity * (1 - Fraction(headroom))
              if capacity_basis == "before_reserve" else capacity)
    fits = Fraction(live_upper_bytes) <= budget
    return {**result, "outcome": "pass" if fits else "fail",
            "budget_bytes_exact": str(budget),
            "reason": ("clears the stated upper-bound screen" if fits
                       else "may not fit under the stated bounds and reserve")}
