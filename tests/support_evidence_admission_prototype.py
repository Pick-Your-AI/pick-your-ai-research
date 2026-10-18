"""Test-only dated source carrier for an exact CD-3 query and evidence cohort.

Source inspection, coverage/rank, rights and currency remain caller-established
facts. This wrapper checks their retained identity, not their truth. A matching
URI, revision, timestamp or digest never qualifies evidence on its own.
"""

from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

from scripts.validate_research import locator_parts, price_instant, public_source
from tests.support_membership_binding_prototype import (
    ELIGIBILITY, SCHEMA as BINDING_SCHEMA, SupportQueryRecord, decode, digest,
)


VERSION = "cd3-evidence-0.1"
MAX_EVIDENCE_BYTES = 64 * 1024
SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "support-evidence-admission.schema.json").read_text(encoding="utf-8"))
REGISTRY = Registry().with_resources([
    ("urn:pick-your-ai:cd3-binding:0.3", Resource.from_contents(BINDING_SCHEMA)),
    (SCHEMA["$id"], Resource.from_contents(SCHEMA)),
])
WIRE = Draft202012Validator(SCHEMA, registry=REGISTRY)
RESULT = Draft202012Validator({"$ref": SCHEMA["$id"] + "#/$defs/result"}, registry=REGISTRY)
DIGEST = Draft202012Validator(BINDING_SCHEMA["$defs"]["digest"])


def checked_shape(validator, value, code):
    try:
        validator.validate(value)
    except ValidationError:
        raise ValueError(code) from None


def fact(value):
    if value is not None and type(value) is not bool:
        raise ValueError("source_qualification_malformed")


def eligibility_inputs(value):
    if value is None:
        value = {}
    if type(value) is not dict or set(value) - set(ELIGIBILITY):
        raise ValueError("source_eligibility_inputs_malformed")
    for entry in value.values():
        fact(entry)
    return {key: value.get(key) for key in ELIGIBILITY}


class SupportEvidenceRecord:
    """Bind a normalized cohort's dated source register to original query bytes.

    Every registered source covers this exact already-normalized cohort scope.
    The caller must establish that coverage and the preceding rank resolution;
    this record does not attribute individual members to individual sources.
    """

    def __init__(self, evidence_raw, binding_raw, answers_raw):
        if type(evidence_raw) is not bytes:
            raise ValueError("source_evidence_requires_bytes")
        if len(evidence_raw) > MAX_EVIDENCE_BYTES:
            raise ValueError("source_evidence_size_unsupported")
        try:
            document = decode(evidence_raw)
        except (ValueError, UnicodeError, RecursionError):
            raise ValueError("source_evidence_json_malformed") from None
        checked_shape(WIRE, document, "source_evidence_shape_malformed")
        evidence = document["x_t0_support_evidence"]
        identities = set()
        for source in evidence["sources"]:
            identity = (source["id"], source["revision"])
            if identity in identities:
                raise ValueError("source_evidence_identity_duplicate")
            identities.add(identity)
            # Reuse conservative public-locator syntax. Stable query-free URLs
            # avoid carrying signed URL parameters; section fragments are kept.
            if not public_source(source["source_uri"]) or locator_parts(source["source_uri"]).query:
                raise ValueError("source_evidence_locator_unsupported")
            try:
                # Existing explicit profile checks real Gregorian dates and
                # preserves every supplied fractional digit without extras.
                price_instant(source["checked_at"])
            except (TypeError, ValueError):
                raise ValueError("source_evidence_timestamp_unsupported") from None

        query = SupportQueryRecord(binding_raw, answers_raw)
        proposal = decode(binding_raw)["x_t0_support_query"]
        if evidence["binding_sha256"] != digest(binding_raw):
            raise ValueError("source_evidence_binding_mismatch")
        if any(evidence[key] != proposal[key] for key in ("query", "scope", "cohort")):
            raise ValueError("source_evidence_context_mismatch")
        self._query = query
        self._evidence = deepcopy(evidence)
        self._evidence_bytes = evidence_raw

    @property
    def original_bytes(self):
        return self._evidence_bytes, *self._query.original_bytes

    @property
    def scope(self):
        return self._query.scope

    def evaluate(self, selected_scope, *, enabled, eligible_inputs=None,
                 cohort_checked_only=None, qualified_evidence_sha256=None,
                 source_qualified=None):
        """Use only the caller's qualification of these exact evidence bytes.

        Missing/mismatched receipts leave source qualification unresolved.
        Qualification is never retained from a previous invocation. No age or
        latest-version rule is inferred from the recorded source timestamps.
        """
        fact(source_qualified)
        requested = eligibility_inputs(eligible_inputs)
        if qualified_evidence_sha256 is not None:
            checked_shape(DIGEST, qualified_evidence_sha256, "source_receipt_digest_malformed")
        actual_digest = digest(self._evidence_bytes)
        if qualified_evidence_sha256 is None:
            reason, admitted = "source_receipt_missing", None
        elif qualified_evidence_sha256 != actual_digest:
            reason, admitted = "source_receipt_mismatch", None
        elif source_qualified is None:
            reason, admitted = "source_qualification_unresolved", None
        elif source_qualified is False:
            reason, admitted = "source_ineligible", False
        else:
            reason, admitted = "source_qualified", True
        effective = deepcopy(requested)
        if requested["cohort"] is False or admitted is False:
            effective["cohort"] = False
        elif requested["cohort"] is not True or admitted is not True:
            effective["cohort"] = None
        membership = self._query.evaluate(
            selected_scope, enabled=enabled, eligible_inputs=effective,
            cohort_checked_only=cohort_checked_only,
        )
        result = {"x_t0_support_evidence_result": {
            "proposal_version": VERSION,
            "evidence_sha256": actual_digest,
            "evidence": deepcopy(self._evidence),
            "admission": {
                "qualified_evidence_sha256": qualified_evidence_sha256,
                "source_qualified": source_qualified,
                "requested_eligible_inputs": requested,
                "reason": reason,
            },
            "membership": membership,
        }}
        checked_shape(RESULT, result, "source_evidence_result_malformed")
        return result

    def verify_result(self, raw, selected_scope, **context):
        """Recompute all evidence, caller context and membership result fields.

        Result whitespace/order may vary. Original evidence/query/answer bytes
        cannot be replaced, even when the replacement has the same verdict.
        This is consistency checking, not signature or publisher verification.
        """
        result = decode(raw)
        checked_shape(RESULT, result, "source_evidence_result_malformed")
        expected = self.evaluate(selected_scope, **context)
        if result != expected:
            raise ValueError("source_evidence_result_mismatch")
        return expected
