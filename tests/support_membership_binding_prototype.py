"""Synthetic CD-3 query/result binding over exact CD-1 answer bytes.

The caller establishes selection activation, exact catalog/configuration scope
and separately eligible applicability, requirements and evidence. Recorded
hashes and source labels do not authenticate any of those facts. This wrapper
uses the corrected requested-set completeness reducer and separately qualified
checked-only provenance; frozen v1 is unchanged.
"""

from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_research import intake_json
from tests.support_membership_prototype import Decision, Evidence, Outcome, Requirement, evaluate
from tests.t0_answer_state_prototype import AnswerIndex, pointer_tokens


SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "support-membership-binding.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(SCHEMA)


def definition(name):
    return {"$ref": "#/$defs/" + name, "$defs": SCHEMA["$defs"]}


RESULT = Draft202012Validator(definition("result"))
SCOPE = Draft202012Validator(definition("scope"))
FIELDS = {
    "applies_when": {"type": "boolean"},
    "requested": definition("requirement_values"),
    "requested_complete": {"type": "boolean"},
    "supported": definition("values"),
    "unsupported": definition("values"),
    "exhaustive": {"type": "boolean"},
}
ELIGIBILITY = ("applies_when", "requested", "requested_complete", "cohort")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError("CD-3 retained inputs must be UTF-8 bytes")
    value = intake_json(raw.decode("utf-8"))
    # Reject escaped lone surrogates too, including in unrelated CD-1 records.
    # This checks Unicode scalars without reserializing the bytes we bind.
    json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return value


def validate(validator, value, label):
    try:
        validator.validate(value)
    except ValidationError as error:
        raise ValueError(f"invalid {label}: {error.message}") from error


def answer_path(proposal, field):
    """Literal RFC 6901 tokens bind selection, query and evidence-cohort version."""
    tokens = ("support_checks", proposal["scope"]["selection_id"],
              proposal["query"]["id"], proposal["query"]["version"],
              proposal["cohort"]["id"], proposal["cohort"]["version"], field)
    return "/" + "/".join(token.replace("~", "~0").replace("/", "~1")
                          for token in tokens)


def answer_wire(answer):
    value = {"state": answer.state.value}
    if answer.provided:
        value["value"] = deepcopy(answer.value)
        if answer.source is not None:
            value["source"] = answer.source
    if answer.source_path is not None:
        value["source_path"] = answer.source_path
    return value


class SupportQueryRecord:
    """Read one typed, scoped membership query and retain every operand state.

    A provided unsupported list, including [], means the normalized cohort's
    explicit negative claims were recorded. Missing/withheld/nonapplicable data
    cannot stand in for that empty list. This readiness gate is distinct from
    vendor inventory exhaustiveness and the caller's evidence eligibility.
    """

    def __init__(self, binding_raw, answers_raw):
        binding = decode(binding_raw)
        validate(WIRE, binding, "CD-3 query")
        proposal = binding["x_t0_support_query"]
        pointer_tokens(proposal["scope"]["property"])
        if type(answers_raw) is not bytes or digest(answers_raw) != proposal["answer_states_sha256"]:
            raise ValueError("answer bytes do not match the support query")
        decode(answers_raw)
        index = AnswerIndex(answers_raw)
        # Validate every provided scoped field before activation, applicability
        # or eligibility can short-circuit. Unrelated fields retain CD-1's scope.
        self._answers = {field: index.read(answer_path(proposal, field), schema)
                         for field, schema in FIELDS.items()}
        self._proposal = deepcopy(proposal)
        self._binding_bytes = binding_raw
        self._answer_bytes = answers_raw

    @property
    def original_bytes(self):
        return self._binding_bytes, self._answer_bytes

    @property
    def scope(self):
        return deepcopy(self._proposal["scope"])

    def evaluate(self, selected_scope, *, enabled, eligible_inputs=None, cohort_checked_only=None):
        """Return a closed result over this invocation's caller-established scope.

        Eligibility omission is unresolved. Neither source strings nor a prior
        call supply eligibility; each input group is qualified independently.
        A false applicability value can skip only when its eligibility is true.
        Checked-only provenance is separately established for this exact cohort;
        it cannot be supplied by an answer's source string or result flags.
        """
        if cohort_checked_only is not None and type(cohort_checked_only) is not bool:
            raise ValueError("checked-only qualification must be an exact Boolean or unresolved")
        if enabled is not None and type(enabled) is not bool:
            raise ValueError("enabled must be an exact Boolean or unresolved")
        if selected_scope is not None:
            validate(SCOPE, selected_scope, "selected support scope")
            pointer_tokens(selected_scope["property"])
            json.dumps(selected_scope, ensure_ascii=False).encode("utf-8")
        if eligible_inputs is None:
            eligible_inputs = {}
        if type(eligible_inputs) is not dict or set(eligible_inputs) - set(ELIGIBILITY):
            raise ValueError("eligibility must name only applicability, requested values/completeness or cohort inputs")
        if any(value is not None and type(value) is not bool for value in eligible_inputs.values()):
            raise ValueError("eligibility must be exact Boolean or unresolved")
        eligible = {field: eligible_inputs.get(field) for field in ELIGIBILITY}
        proposal = self._proposal

        def known(field):
            answer = self._answers[field]
            return answer.value if answer.provided else None

        def uncertain(reason, outcome=Outcome.UNKNOWN):
            return Decision(outcome, reason, proposal["cohort"]["id"])

        def eligibility_failure(field):
            return uncertain(field + ("_evidence_unresolved" if eligible[field] is None
                                      else "_evidence_ineligible"))

        if enabled is False:
            decision = uncertain("selection_not_enabled", Outcome.SKIPPED)
        elif enabled is None:
            decision = uncertain("selection_activation_unknown")
        elif selected_scope is None:
            decision = uncertain("selection_scope_missing")
        elif selected_scope != proposal["scope"]:
            decision = uncertain("support_scope_mismatch")
        elif eligible["applies_when"] is not True:
            decision = eligibility_failure("applies_when")
        elif known("applies_when") is None:
            decision = uncertain("applicability_unknown")
        elif known("applies_when") is False:
            decision = uncertain("not_applicable", Outcome.SKIPPED)
        elif eligible["requested"] is not True:
            decision = eligibility_failure("requested")
        elif known("requested") is None:
            decision = uncertain("requirement_unknown")
        elif not known("requested"):
            decision = uncertain("requirement_empty")
        elif eligible["cohort"] is not True:
            decision = eligibility_failure("cohort")
        elif known("unsupported") is None:
            decision = uncertain("unsupported_claims_unresolved")
        else:
            supported = known("supported")
            decision = evaluate(
                frozenset(known("requested")),
                Evidence(proposal["cohort"]["id"], True,
                         None if supported is None else frozenset(supported),
                         known("exhaustive"), frozenset(known("unsupported")),
                         checked_only=cohort_checked_only),
                Requirement(proposal["query"]["requirement"]),
                requested_complete=(known("requested_complete")
                                    if eligible["requested_complete"] is True else None),
            )
        result = {"x_t0_support_result": {
            "proposal_version": "cd3-0.3",
            "binding_sha256": digest(self._binding_bytes),
            "answer_states_sha256": digest(self._answer_bytes),
            "query": deepcopy(proposal["query"]),
            "scope": deepcopy(proposal["scope"]),
            "cohort": deepcopy(proposal["cohort"]),
            "evaluation": {"enabled": enabled, "selected_scope": deepcopy(selected_scope),
                           "eligible_inputs": eligible, "cohort_checked_only": cohort_checked_only},
            "inputs": {field: answer_wire(answer) for field, answer in self._answers.items()},
            "decision": asdict(decision),
        }}
        # Use JSON's list/string vocabulary; dataclass tuples and StrEnums do
        # not escape into the transport object. This is not input canonicalization.
        result = json.loads(json.dumps(result, ensure_ascii=False, allow_nan=False))
        validate(RESULT, result, "CD-3 result")
        return result

    def verify_result(self, raw, selected_scope, *, enabled, eligible_inputs=None, cohort_checked_only=None):
        """Recompute against caller context; never trust a result's own flags.

        Result JSON whitespace/order can differ, but the complete original
        query/answer hashes and every computed field must agree. This verifies
        consistency only, not a signature, source truth or caller authority.
        """
        result = decode(raw)
        validate(RESULT, result, "CD-3 result")
        expected = self.evaluate(selected_scope, enabled=enabled, eligible_inputs=eligible_inputs,
                                 cohort_checked_only=cohort_checked_only)
        if result != expected:
            raise ValueError("support result does not match retained inputs and caller context")
        return expected
