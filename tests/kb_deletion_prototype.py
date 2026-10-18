"""Synthetic KB-02 examples over normalized receipts; no connector or wire API."""

from dataclasses import dataclass
from enum import StrEnum


class State(StrEnum):
    TOMBSTONED = "tombstoned"
    EXCLUDED = "excluded_from_serving"
    SERVING = "still_serving"
    BACKUP = "separately_governed_nonserving_backup"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Receipt:
    edge_id: str
    state: State
    matches_event: bool | None = None


@dataclass(frozen=True)
class Result:
    outcome: str
    reason: str
    severity: str = "error"


def evaluate(event_applies: bool | None, lineage_complete: bool | None,
             receipts: tuple[Receipt, ...]) -> Result:
    """Project KB-02 only. Completeness/event identity are supplied evidence.

    Each receipt represents one derived-destination lineage edge. The caller has
    already established the protected source, tenant, deletion/revocation event,
    destination identity and trustworthy observation. This does not discover a
    graph, authenticate receipts, delete data, or establish backup erasure.
    """
    if event_applies is False:
        return Result("skipped", "no_applicable_event")
    if event_applies is not True:
        return Result("unknown", "event_applicability_unknown")
    ids = [r.edge_id for r in receipts]
    # An unambiguous current stale edge fails even if unrelated identities are
    # unresolved. A duplicated serving identity itself is not trusted.
    if any(isinstance(r.edge_id, str) and r.edge_id.strip()
           and ids.count(r.edge_id) == 1
           and r.matches_event is True and r.state == State.SERVING
           for r in receipts):
        return Result("fail", "known_stale_serving_copy")
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        return Result("unknown", "ambiguous_lineage_identity")
    if lineage_complete is not True:
        return Result("unknown", "lineage_incomplete")
    safe = {State.TOMBSTONED, State.EXCLUDED, State.BACKUP}
    if any(r.matches_event is not True or r.state not in safe for r in receipts):
        return Result("unknown", "current_destination_receipt_missing")
    return Result("pass", "serving_scope_accounted_for")
