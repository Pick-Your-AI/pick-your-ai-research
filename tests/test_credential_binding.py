"""Synthetic credential-source research cases, without secret locators or values."""

import unittest
from dataclasses import replace
from typing import Final

from tests.credential_binding_prototype import (
    Binding,
    Case,
    Connection,
    Kind,
    Outcome,
    SelectionId,
    Source,
    evaluate,
)

CONNECTION_ID: Final = SelectionId("fixture.integration")
CONNECTION: Final = Connection(CONNECTION_ID, Kind.INTEGRATION)
INHERITED: Final = Case(
    (Binding(Source.INTEGRATION, True, CONNECTION_ID),), (CONNECTION,), (CONNECTION_ID,)
)


class CredentialBindingCases(unittest.TestCase):
    def test_direct_source_checks_its_own_reference(self) -> None:
        for present, expected in (
            (True, Outcome.PASS),
            (False, Outcome.FAIL),
            (None, Outcome.UNKNOWN),
        ):
            with self.subTest(present=present):
                case = Case(
                    (Binding(Source.DIRECT, True),), local_credential_present=present
                )
                self.assertEqual(evaluate(case), expected)

    def test_explicit_shared_connection_needs_no_tool_local_copy(self) -> None:
        self.assertEqual(evaluate(INHERITED), Outcome.PASS)

    def test_provider_hosted_tool_uses_exact_provider_binding(self) -> None:
        provider_id = SelectionId("fixture.provider")
        case = Case(
            (Binding(Source.MODEL_PROVIDER, True, provider_id),),
            (Connection(provider_id, Kind.MODEL_PROVIDER),),
            (provider_id,),
            provider_hosted=True,
        )
        self.assertEqual(evaluate(case), Outcome.PASS)

    def test_provider_execution_location_must_be_established(self) -> None:
        provider_id = SelectionId("fixture.provider")
        provider = Case(
            (Binding(Source.MODEL_PROVIDER, True, provider_id),),
            (Connection(provider_id, Kind.MODEL_PROVIDER),),
            (provider_id,),
        )
        for hosted, expected in ((None, Outcome.UNKNOWN), (False, Outcome.FAIL)):
            with self.subTest(hosted=hosted):
                self.assertEqual(
                    evaluate(replace(provider, provider_hosted=hosted)), expected
                )

    def test_disabled_missing_wrong_kind_or_unlinked_target_fails(self) -> None:
        cases = (
            replace(INHERITED, connections=()),
            replace(INHERITED, connections=(replace(CONNECTION, enabled=False),)),
            replace(INHERITED, connections=(replace(CONNECTION, kind=Kind.OTHER),)),
            replace(INHERITED, provided_by_targets=()),
            replace(
                INHERITED, connections=(replace(CONNECTION, credential_present=False),)
            ),
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(evaluate(case), Outcome.FAIL)

    def test_unresolved_version_operation_or_auth_remains_unknown(self) -> None:
        for connection in (
            replace(CONNECTION, version_resolved=False),
            replace(CONNECTION, serves_operation=None),
            replace(CONNECTION, auth_supported=None),
            replace(CONNECTION, credential_present=None),
        ):
            with self.subTest(connection=connection):
                self.assertEqual(
                    evaluate(replace(INHERITED, connections=(connection,))),
                    Outcome.UNKNOWN,
                )

    def test_known_unsupported_method_or_operation_fails(self) -> None:
        for connection in (
            replace(CONNECTION, serves_operation=False),
            replace(CONNECTION, auth_supported=False),
        ):
            with self.subTest(connection=connection):
                self.assertEqual(
                    evaluate(replace(INHERITED, connections=(connection,))),
                    Outcome.FAIL,
                )

    def test_competing_bindings_and_local_inherited_conflict_are_unknown(self) -> None:
        for case in (
            replace(INHERITED, bindings=INHERITED.bindings * 2),
            replace(INHERITED, local_credential_present=True),
            replace(INHERITED, local_credential_present=None),
            replace(INHERITED, connections=(CONNECTION, CONNECTION)),
        ):
            with self.subTest(case=case):
                self.assertEqual(evaluate(case), Outcome.UNKNOWN)

    def test_absent_legacy_binding_is_not_guessed_from_available_connection(
        self,
    ) -> None:
        self.assertEqual(evaluate(replace(INHERITED, bindings=())), Outcome.UNKNOWN)

    def test_missing_auth_choice_or_target_identity_is_unknown(self) -> None:
        for case in (
            replace(
                INHERITED, bindings=(Binding(Source.INTEGRATION, None, CONNECTION_ID),)
            ),
            replace(INHERITED, bindings=(Binding(Source.INTEGRATION, True),)),
            Case((Binding(Source.DIRECT, None),), local_credential_present=True),
            Case((Binding(Source.NONE, None),)),
        ):
            with self.subTest(case=case):
                self.assertEqual(evaluate(case), Outcome.UNKNOWN)

    def test_explicit_target_is_not_confused_with_other_available_connections(
        self,
    ) -> None:
        unrelated = Connection(SelectionId("fixture.unrelated"), Kind.INTEGRATION)
        case = replace(INHERITED, connections=(unrelated, CONNECTION))
        self.assertEqual(evaluate(case), Outcome.PASS)

    def test_explicit_none_requires_evidenced_unauthenticated_choice(self) -> None:
        for supported, expected in (
            (True, Outcome.PASS),
            (False, Outcome.FAIL),
            (None, Outcome.UNKNOWN),
        ):
            with self.subTest(supported=supported):
                self.assertEqual(
                    evaluate(Case((Binding(Source.NONE, supported),))), expected
                )

    def test_disabled_tool_is_not_applicable(self) -> None:
        self.assertEqual(
            evaluate(replace(INHERITED, tool_enabled=False)), Outcome.SKIPPED
        )


if __name__ == "__main__":
    _ = unittest.main()
