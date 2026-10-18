"""Synthetic T4-B6/CD-6 projection; presence facts never contain or resolve secrets."""

from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

SelectionId = NewType("SelectionId", str)


class Source(StrEnum):
    DIRECT = "direct"
    INTEGRATION = "integration"
    MODEL_PROVIDER = "model_provider"
    NONE = "none"


class Kind(StrEnum):
    INTEGRATION = "integration"
    MODEL_PROVIDER = "model_provider"
    OTHER = "other"


class Outcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class Binding:
    source: Source
    auth_choice_supported: bool | None
    target_id: SelectionId | None = None


@dataclass(frozen=True, slots=True)
class Connection:
    id: SelectionId
    kind: Kind
    enabled: bool = True
    version_resolved: bool = True
    serves_operation: bool | None = True
    auth_supported: bool | None = True
    credential_present: bool | None = True


@dataclass(frozen=True, slots=True)
class Case:
    bindings: tuple[Binding, ...]
    connections: tuple[Connection, ...] = ()
    provided_by_targets: tuple[SelectionId, ...] = ()
    tool_enabled: bool = True
    local_credential_present: bool | None = False
    provider_hosted: bool | None = None


def requirement(fact: bool | None) -> Outcome:
    match fact:
        case True:
            return Outcome.PASS
        case False:
            return Outcome.FAIL
        case None:
            return Outcome.UNKNOWN


def combine(results: tuple[Outcome, ...]) -> Outcome:
    if Outcome.FAIL in results:
        return Outcome.FAIL
    return Outcome.UNKNOWN if Outcome.UNKNOWN in results else Outcome.PASS


def evaluate(case: Case) -> Outcome:
    if not case.tool_enabled:
        return Outcome.SKIPPED
    if len(case.bindings) != 1:
        return Outcome.UNKNOWN
    binding = case.bindings[0]
    # A direct or unauthenticated choice cannot simultaneously select inherited
    # credential provenance. Do not silently prefer one source over the other.
    if binding.source in (Source.DIRECT, Source.NONE) and binding.target_id is not None:
        return Outcome.UNKNOWN
    # A no-auth choice does not prove that a configured or uninspected local
    # reference can be disregarded; require an explicit conflict resolution.
    if binding.source is Source.NONE and case.local_credential_present is not False:
        return Outcome.UNKNOWN
    match binding.source:
        case Source.DIRECT:
            return combine(
                (
                    requirement(binding.auth_choice_supported),
                    requirement(case.local_credential_present),
                )
            )
        case Source.NONE:
            return requirement(binding.auth_choice_supported)
        case Source.INTEGRATION | Source.MODEL_PROVIDER:
            if case.local_credential_present is not False:
                return Outcome.UNKNOWN
            if binding.target_id is None:
                return Outcome.UNKNOWN
            targets = tuple(c for c in case.connections if c.id == binding.target_id)
            if len(targets) > 1:
                return Outcome.UNKNOWN
            if not targets:
                return Outcome.FAIL
            target = targets[0]
            expected_kind = {
                Source.INTEGRATION: Kind.INTEGRATION,
                Source.MODEL_PROVIDER: Kind.MODEL_PROVIDER,
            }[binding.source]
            checks = (
                requirement(binding.auth_choice_supported),
                requirement(target.kind == expected_kind),
                requirement(target.enabled),
                requirement(True if target.version_resolved else None),
                requirement(binding.target_id in case.provided_by_targets),
                requirement(target.serves_operation),
                requirement(target.auth_supported),
                requirement(target.credential_present),
                requirement(
                    {
                        Source.INTEGRATION: True,
                        Source.MODEL_PROVIDER: case.provider_hosted,
                    }[binding.source]
                ),
            )
            return combine(checks)
