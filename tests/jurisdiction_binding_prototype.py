"""Synthetic CD-9 containment and provider-region mapping experiment.

All descriptors and CD-1 answers are retained; every consumed fact requires
external, exact-scope evidence eligibility. No geography, provider mapping,
source rights, legal compliance or complete build data-flow inventory is
discovered here. This is not a released contract or deployment authorizer.
"""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_research import intake_json
from tests.selection_quantifier_prototype import Outcome
from tests.t0_answer_state_prototype import Answer, AnswerIndex


SCHEMA = json.loads((Path(__file__).with_name("fixtures") /
                     "jurisdiction-binding.schema.json").read_text(encoding="utf-8"))
WIRE = Draft202012Validator(SCHEMA)
CONSTRAINT = {"$defs": SCHEMA["$defs"], **SCHEMA["$defs"]["constraint"]}
BOOL = {"type": "boolean"}
IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")
COLLECTIONS = {"jurisdiction": "jurisdictions", "group": "groups",
               "disjoint": "disjoint_pairs", "region": "regions", "query": "queries"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor_digest(value):
    """Exact ordered descriptor encoding; never normalize original input bytes.

    Descriptors contain strings, arrays and objects only. Array order is part
    of this candidate's identity, so even reordering an inventory requires its
    own scoped evidence keys. Object key order and JSON whitespace are not.
    """
    return digest(("cd9-0.1\n" + json.dumps(value, ensure_ascii=False,
                   sort_keys=True, separators=(",", ":"))).encode("utf-8"))


def fact_path(kind, record, *tokens):
    return "/" + "/".join(("cd9", kind, record["id"], descriptor_digest(record), *tokens))


def constraint_path(dimension):
    return "/workload/residency/" + dimension


def _identities(value):
    """Schema regex '$' may accept a final LF; enforce the entire identifier."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "id" or key.endswith("_id"):
                if type(child) is not str or IDENTITY.fullmatch(child) is None:
                    raise ValueError("CD-9 identity must match the whole ASCII string")
            elif key.endswith("_ids"):
                for identity in child:
                    if type(identity) is not str or IDENTITY.fullmatch(identity) is None:
                        raise ValueError("CD-9 identity must match the whole ASCII string")
            elif key.endswith("_sha256"):
                if type(child) is not str or re.fullmatch(r"[a-f0-9]{64}", child) is None:
                    raise ValueError("CD-9 digest must be exactly 64 lowercase hexadecimal characters")
            _identities(child)
    elif isinstance(value, list):
        for child in value:
            _identities(child)


@dataclass(frozen=True)
class Membership:
    allowed_kind: str
    allowed_id: str
    outcome: Outcome
    reason: str
    witness: tuple[str, ...] = ()
    members: tuple[tuple[str, Outcome, str], ...] = ()
    disjoint_witnesses: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = ()


@dataclass(frozen=True)
class Check:
    subject: str
    outcome: Outcome
    reason: str
    comparisons: tuple[Membership, ...] = ()


@dataclass(frozen=True)
class QueryResult:
    query_id: str
    subject_id: str
    context_id: str
    dimension: str
    outcome: Outcome
    reason: str
    checks: tuple[Check, ...]
    rule_id: str = "D-R6"
    rule_version: str = "cd9-0.1"
    severity: str = "error"
    on_unknown: str = "review"


@dataclass(frozen=True)
class Result:
    queries: tuple[QueryResult, ...]
    answers: tuple[tuple[str, Answer], ...]
    eligibility: tuple[tuple[str, bool | None], ...]
    binding_sha256: str
    answer_states_sha256: str


class JurisdictionRecord:
    """Evaluate explicitly requested subjects/dimensions, never a whole build.

    A descriptor declares candidate facts. It proves none of them. Positive
    edges, disjointness, node identities, group members, mapped/subject locations
    and inventory completeness have separate CD-1 Boolean/eligibility keys.
    Keys include their entire owner descriptor, including service, condition
    context and processing/storage dimension for a provider-region mapping.
    """

    def __init__(self, binding_raw, answers_raw):
        if type(binding_raw) is not bytes or type(answers_raw) is not bytes:
            raise ValueError("CD-9 retained inputs must be UTF-8 bytes")
        binding = intake_json(binding_raw.decode("utf-8"))
        try:
            WIRE.validate(binding)
        except ValidationError as error:
            raise ValueError("invalid CD-9 binding: " + error.message) from error
        proposal = binding["x_t0_jurisdiction"]
        if digest(answers_raw) != proposal["answer_states_sha256"]:
            raise ValueError("answer bytes do not match the CD-9 binding")
        _identities(proposal)
        records = {}
        for kind, collection in COLLECTIONS.items():
            values = proposal[collection]
            by_id = {record["id"]: deepcopy(record) for record in values}
            if len(by_id) != len(values):
                raise ValueError("duplicate CD-9 " + kind + " identity")
            records[kind] = by_id
        scopes = [tuple(record[key] for key in
                        ("provider_id", "service_id", "region_id", "context_id", "dimension"))
                  for record in records["region"].values()]
        if len(scopes) != len(set(scopes)):
            raise ValueError("duplicate provider-region mapping scope")
        query_scopes = [(record["subject_id"], record["context_id"], record["dimension"])
                        for record in records["query"].values()]
        if len(query_scopes) != len(set(query_scopes)):
            raise ValueError("duplicate subject/context/dimension query")
        pairs = set()
        for record in records["disjoint"].values():
            pair = frozenset((record["left_id"], record["right_id"]))
            if len(pair) != 2:
                raise ValueError("a jurisdiction cannot be disjoint from itself")
            if pair in pairs:
                raise ValueError("duplicate unordered disjoint pair")
            pairs.add(pair)

        # Multiple explicit parents are valid. Cycles are malformed input even
        # when a fact is ineligible or a query is currently unconstrained.
        visited, visiting = set(), set()

        def visit(identity):
            if identity in visiting:
                raise ValueError("cyclic jurisdiction containment descriptors")
            if identity in visited or identity not in records["jurisdiction"]:
                return
            visiting.add(identity)
            for parent in records["jurisdiction"][identity]["parent_ids"]:
                visit(parent)
            visiting.remove(identity)
            visited.add(identity)

        for identity in records["jurisdiction"]:
            visit(identity)

        index = AnswerIndex(answers_raw)
        answers = {}

        def read(path, schema=BOOL):
            answer = index.read(path, schema)
            if answer.provided:
                _identities(answer.value)
            answers[path] = answer

        for dimension in ("processing", "storage"):
            read(constraint_path(dimension), CONSTRAINT)
        for identity, record in sorted(records["jurisdiction"].items()):
            read(fact_path("jurisdiction", record, "exists"))
            read(fact_path("jurisdiction", record, "parents_complete"))
            for parent in record["parent_ids"]:
                read(fact_path("jurisdiction", record, "parent", parent))
        for record in records["group"].values():
            read(fact_path("group", record, "members_complete"))
            for member in record["member_ids"]:
                read(fact_path("group", record, "member", member))
        for record in records["disjoint"].values():
            read(fact_path("disjoint", record, "confirmed"))
        for record in records["region"].values():
            read(fact_path("region", record, "locations_complete"))
            for identity in record["jurisdiction_ids"]:
                read(fact_path("region", record, "location", identity))
        for record in records["query"].values():
            read(fact_path("query", record, "locations_complete"))
            for location in record["location_refs"]:
                read(fact_path("query", record, "location", descriptor_digest(location)))
        self._bytes = binding_raw, answers_raw
        self._records = records
        self._answers = answers

    @property
    def original_bytes(self):
        return self._bytes

    @property
    def answer_paths(self):
        return tuple(self._answers)

    def evaluate(self, eligible_answers=None):
        eligible_answers = {} if eligible_answers is None else eligible_answers
        if type(eligible_answers) is not dict or set(eligible_answers) - set(self._answers):
            raise ValueError("eligibility must use this record's exact scoped answer paths")
        if any(value is not None and type(value) is not bool for value in eligible_answers.values()):
            raise ValueError("eligibility must be exact Boolean or unresolved")
        eligibility = {path: eligible_answers.get(path) for path in self._answers}

        def fact(path):
            answer = self._answers[path]
            return answer.value if answer.provided and eligibility[path] is True else None

        def confirmed(kind, record, *tokens):
            return fact(fact_path(kind, record, *tokens)) is True

        nodes = self._records["jurisdiction"]
        ancestry_cache = {}

        def ancestry(identity):
            if identity in ancestry_cache:
                return ancestry_cache[identity]
            record = nodes.get(identity)
            if record is None or not confirmed("jurisdiction", record, "exists"):
                return {}, False
            paths = {identity: (identity,)}
            complete = confirmed("jurisdiction", record, "parents_complete")
            for parent in sorted(record["parent_ids"]):
                if not confirmed("jurisdiction", record, "parent", parent):
                    complete = False
                    continue
                parent_paths, parent_complete = ancestry(parent)
                complete = complete and parent_complete
                for ancestor, path in parent_paths.items():
                    paths.setdefault(ancestor, (identity, *path))
            ancestry_cache[identity] = paths, complete
            return paths, complete

        def jurisdiction_member(location, allowed):
            paths, complete = ancestry(location)
            allowed_paths, allowed_complete = ancestry(allowed)
            if not paths or not allowed_paths:
                return Outcome.UNKNOWN, "jurisdiction_identity_unknown", (), ()
            conflicts = (*ancestry_conflicts(paths), *ancestry_conflicts(allowed_paths))
            if conflicts:
                return Outcome.UNKNOWN, "disputed_jurisdiction_ancestry", (), tuple(conflicts)
            witness = paths.get(allowed, ())
            exclusions = []
            for pair in sorted(self._records["disjoint"].values(), key=lambda item: item["id"]):
                if not confirmed("disjoint", pair, "confirmed"):
                    continue
                left, right = pair["left_id"], pair["right_id"]
                for source, target in ((left, right), (right, left)):
                    if source in paths and target in allowed_paths:
                        exclusions.append((pair["id"], paths[source], allowed_paths[target]))
            if witness and exclusions:
                return Outcome.UNKNOWN, "disputed_containment_and_disjointness", witness, tuple(exclusions)
            if exclusions:
                return Outcome.FAIL, "explicit_disjoint_scope", (), tuple(exclusions)
            if witness:
                return Outcome.PASS, "explicit_containment_path", witness, ()
            # Non-containment is not disjointness. A country-level source may
            # be too coarse for an allowed subdivision; overlapping scopes or
            # different roots cannot be excluded by name or ancestry absence.
            reason = ("location_scope_coarser_than_constraint" if location in allowed_paths else
                      "no_disjointness_evidence" if complete and allowed_complete else
                      "ancestry_incomplete")
            return Outcome.UNKNOWN, reason, (), ()

        def ancestry_conflicts(paths):
            conflicts = []
            for pair in sorted(self._records["disjoint"].values(), key=lambda item: item["id"]):
                left, right = pair["left_id"], pair["right_id"]
                if left in paths and right in paths and confirmed("disjoint", pair, "confirmed"):
                    conflicts.append((pair["id"], paths[left], paths[right]))
            return tuple(conflicts)

        def membership(location, allowed):
            kind, identity = allowed["kind"], allowed["id"]
            target = self._records[kind].get(identity)
            if target is None:
                return Membership(kind, identity, Outcome.UNKNOWN, "allowed_reference_missing")
            if allowed.get("descriptor_sha256") != descriptor_digest(target):
                return Membership(kind, identity, Outcome.UNKNOWN, "allowed_reference_unbound")
            if kind == "jurisdiction":
                outcome, reason, witness, exclusions = jurisdiction_member(location, identity)
                return Membership(kind, identity, outcome, reason, witness,
                                  disjoint_witnesses=exclusions)
            group = target
            conflicts = ancestry_conflicts(ancestry(location)[0])
            if conflicts:
                return Membership(kind, identity, Outcome.UNKNOWN, "disputed_jurisdiction_ancestry",
                                  disjoint_witnesses=conflicts)
            rows, witness, exclusions = [], (), []
            for member in sorted(group["member_ids"]):
                if confirmed("group", group, "member", member):
                    outcome, reason, path, pairs = jurisdiction_member(location, member)
                    exclusions.extend(pairs)
                    if outcome is Outcome.PASS and not witness:
                        witness = path
                else:
                    outcome, reason = Outcome.UNKNOWN, "group_member_unconfirmed"
                rows.append((member, outcome, reason))
            outcomes = {row[1] for row in rows}
            if Outcome.PASS in outcomes:
                outcome, reason = Outcome.PASS, "explicit_group_member_contains_location"
            elif (Outcome.UNKNOWN not in outcomes
                  and confirmed("group", group, "members_complete")
                  and ancestry(location)[0]):
                outcome, reason = Outcome.FAIL, "complete_group_excludes_location"
            else:
                outcome, reason = Outcome.UNKNOWN, "group_or_containment_incomplete"
            return Membership(kind, identity, outcome, reason, witness, tuple(rows), tuple(exclusions))

        query_results = []
        for query in sorted(self._records["query"].values(), key=lambda item: item["id"]):
            checks = []
            constraint = fact(constraint_path(query["dimension"]))

            def add(subject, outcome, reason, comparisons=()):
                checks.append(Check(subject, outcome, reason, comparisons))

            def check_location(subject, location):
                comparisons = tuple(membership(location, allowed) for allowed in constraint["allowed"])
                outcomes = {comparison.outcome for comparison in comparisons}
                if Outcome.PASS in outcomes:
                    outcome, reason = Outcome.PASS, "allowed_alternative_contains_location"
                elif Outcome.UNKNOWN in outcomes:
                    outcome, reason = Outcome.UNKNOWN, "location_membership_unknown"
                else:
                    outcome, reason = Outcome.FAIL, "all_allowed_alternatives_exclude_location"
                add(subject, outcome, reason, comparisons)

            if constraint is None:
                outcome, reason = Outcome.UNKNOWN, "residency_constraint_unknown"
            elif constraint["mode"] == "unconstrained":
                outcome, reason = Outcome.SKIPPED, "dimension_unconstrained"
            else:
                complete = confirmed("query", query, "locations_complete")
                add("locations", Outcome.PASS if complete else Outcome.UNKNOWN,
                    "subject_locations_complete" if complete else "subject_location_coverage_unknown")
                if not query["location_refs"]:
                    add("locations", Outcome.UNKNOWN, "subject_locations_empty")
                for ref in query["location_refs"]:
                    subject = ref["kind"] + ":" + ref["id"]
                    if not confirmed("query", query, "location", descriptor_digest(ref)):
                        add(subject, Outcome.UNKNOWN, "subject_location_unconfirmed")
                        continue
                    target_kind = "region" if ref["kind"] == "provider_region" else "jurisdiction"
                    target = self._records[target_kind].get(ref["id"])
                    if target is None:
                        add(subject, Outcome.UNKNOWN, "location_reference_missing")
                        continue
                    if ref.get("descriptor_sha256") != descriptor_digest(target):
                        add(subject, Outcome.UNKNOWN, "location_reference_unbound")
                        continue
                    if ref["kind"] == "jurisdiction":
                        check_location(subject, ref["id"])
                        continue
                    region = target
                    if (region["context_id"] != query["context_id"]
                            or region["dimension"] != query["dimension"]):
                        add(subject, Outcome.UNKNOWN, "provider_region_mapping_scope_mismatch")
                        continue
                    complete = confirmed("region", region, "locations_complete")
                    add(subject, Outcome.PASS if complete else Outcome.UNKNOWN,
                        "mapped_locations_complete" if complete else "mapped_location_coverage_unknown")
                    if not region["jurisdiction_ids"]:
                        add(subject, Outcome.UNKNOWN, "mapped_locations_empty")
                    for location in region["jurisdiction_ids"]:
                        scoped = subject + "/" + location
                        if confirmed("region", region, "location", location):
                            check_location(scoped, location)
                        else:
                            add(scoped, Outcome.UNKNOWN, "mapped_location_unconfirmed")
                outcomes = {check.outcome for check in checks}
                if Outcome.FAIL in outcomes:
                    outcome, reason = Outcome.FAIL, "residency_counterexample"
                elif Outcome.UNKNOWN in outcomes:
                    outcome, reason = Outcome.UNKNOWN, "residency_evidence_incomplete"
                else:
                    outcome, reason = Outcome.PASS, "all_declared_locations_contained"
            query_results.append(QueryResult(query["id"], query["subject_id"], query["context_id"],
                                             query["dimension"], outcome, reason, tuple(checks)))
        return Result(tuple(query_results), tuple(deepcopy(self._answers).items()),
                      tuple(eligibility.items()), digest(self._bytes[0]), digest(self._bytes[1]))
