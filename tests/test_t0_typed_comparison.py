"""Hand-chosen synthetic semantics for a separately named comparison profile."""

from copy import deepcopy
from decimal import Inexact, ROUND_UP, Rounded, localcontext
import hashlib
import json
from pathlib import Path
import unittest

import t0_typed_comparison_prototype as typed


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/t0-typed-comparison-0.1.json"
FIXTURE_SHA256 = "a8a1e4cc8e80d5b45424e38b023cee46f394a8d55fd776b4ff267df2386b1554"
REFERENCE = ROOT / "contracts/v1/reference/evaluate.py"
REFERENCE_SHA256 = "092c8a99495f9b5ae960df40b27e33f15eefe6d1a7cd80119658fdc79ada1a5a"
CASE_COUNT = 104
TOP_KEYS = {"fixture_version", "profile", "classification", "frozen_reference_sha256", "cases"}
CASE_KEYS = {"name", "operator", "left_json", "right_json", "expected"}
EXPECTED_OPERATORS = {"eq", "ne", "lt", "lte", "gt", "gte", "in", "contains", "intersects", "subset_of"}


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_fixture_key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("non_finite_fixture_value")


def validate_fixture(document):
    """No Python assert: the same corpus gate applies under optimization."""
    if type(document) is not dict or set(document) != TOP_KEYS:
        raise ValueError("fixture_fields")
    if (document["fixture_version"] != "0.1" or
            document["profile"] != "typed-comparison/0.1" or
            document["classification"] != "synthetic_test_only" or
            document["frozen_reference_sha256"] != REFERENCE_SHA256):
        raise ValueError("fixture_identity")
    cases = document["cases"]
    if type(cases) is not list or len(cases) != CASE_COUNT:
        raise ValueError("fixture_case_count")
    names = set()
    for case in cases:
        if type(case) is not dict or set(case) != CASE_KEYS:
            raise ValueError("fixture_case_fields")
        name = case["name"]
        if type(name) is not str or not name or name in names:
            raise ValueError("fixture_case_name")
        names.add(name)
        if type(case["operator"]) is not str or case["operator"] not in EXPECTED_OPERATORS:
            raise ValueError("fixture_operator")
        if type(case["expected"]) is not str or case["expected"] not in {"true", "false", "unknown"}:
            raise ValueError("fixture_outcome")
        for field in ("left_json", "right_json"):
            if case[field] is not None and type(case[field]) is not str:
                raise ValueError("fixture_operand")
    return cases


def load_fixture(raw):
    document = json.loads(raw, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    cases = validate_fixture(document)
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise ValueError("fixture_digest")
    return cases


def operand(text):
    return None if text is None else text.encode("utf-8")


class TypedComparisonTests(unittest.TestCase):
    def assertRejected(self, code, left, right=b"0", operator="eq", **kwargs):
        with self.assertRaises(typed.ComparisonError) as rejected:
            typed.compare(typed.PROFILE, operator, left, right, **kwargs)
        self.assertEqual(rejected.exception.code, code)
        self.assertEqual(str(rejected.exception), code)

    def test_named_immutable_semantic_vectors(self):
        cases = load_fixture(FIXTURE.read_bytes())
        self.assertEqual({case["operator"] for case in cases}, EXPECTED_OPERATORS)
        self.assertEqual({case["expected"] for case in cases}, {"true", "false", "unknown"})
        for case in cases:
            with self.subTest(case=case["name"]):
                actual = typed.compare("typed-comparison/0.1", case["operator"],
                                       operand(case["left_json"]), operand(case["right_json"]))
                self.assertIs(type(actual), typed.Outcome)
                self.assertEqual(actual.value, case["expected"])

    def test_removed_renamed_reordered_or_changed_case_cannot_redefine_policy(self):
        for mutation in ("remove", "rename", "reorder", "expected", "operand", "extra"):
            document = json.loads(FIXTURE.read_bytes())
            if mutation == "remove":
                document["cases"].pop()
            elif mutation == "rename":
                document["cases"][0]["name"] = "replacement-case"
            elif mutation == "reorder":
                document["cases"].reverse()
            elif mutation == "expected":
                document["cases"][0]["expected"] = "true"
            elif mutation == "operand":
                document["cases"][0]["left_json"] = "1"
            else:
                document["cases"][0]["note"] = "silently added"
            raw = (json.dumps(document, indent=2) + "\n").encode()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                load_fixture(raw)

    def test_fixture_structure_is_strict_independently_of_digest(self):
        original = json.loads(FIXTURE.read_bytes())
        changes = (
            ("root-field", lambda d: d.update(extra=True)),
            ("version", lambda d: d.update(fixture_version="0.2")),
            ("profile", lambda d: d.update(profile="frozen-v1-reference-py312-decimal28")),
            ("classification", lambda d: d.update(classification="measured")),
            ("reference-pin", lambda d: d.update(frozen_reference_sha256="0" * 64)),
            ("duplicate-name", lambda d: d["cases"][1].update(name=d["cases"][0]["name"])),
            ("empty-name", lambda d: d["cases"][0].update(name="")),
            ("operator", lambda d: d["cases"][0].update(operator="equals")),
            ("outcome", lambda d: d["cases"][0].update(expected=True)),
            ("decoded-operand", lambda d: d["cases"][0].update(left_json=True)),
            ("case-field", lambda d: d["cases"][0].pop("right_json")),
        )
        for name, change in changes:
            document = deepcopy(original)
            change(document)
            with self.subTest(change=name), self.assertRaises(ValueError):
                validate_fixture(document)
        for raw in (b'{"profile":"one","profile":"two"}', b'{"cases":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                load_fixture(raw)

    def test_profile_is_mandatory_exact_and_never_falls_back(self):
        for profile in (None, "", "typed-comparison/0.2", "typed-comparison/0.1 ",
                        "frozen-v1-reference-py312-decimal28",
                        "local-retained-frozen-v1-no-external-evidence/1"):
            with self.subTest(profile=profile), self.assertRaisesRegex(
                    typed.ComparisonError, "^unsupported_profile$"):
                typed.compare(profile, "eq", b"1", b"1")
        for operator in (None, "EQ", "eq ", "all"):
            with self.subTest(operator=operator), self.assertRaisesRegex(
                    typed.ComparisonError, "^unsupported_operator$"):
                typed.compare(typed.PROFILE, operator, b"1", b"1")

    def test_raw_bytes_api_rejects_host_numbers_and_decoded_values_in_either_position(self):
        for supplied in (1.0, 1, True, "1", [], {}, bytearray(b"1")):
            for left, right in ((supplied, None), (None, supplied)):
                with self.subTest(type=type(supplied).__name__, left=left is supplied):
                    self.assertRejected("operand_bytes_required", left, right)

    def test_malformed_original_bytes_reject_without_echoing_input(self):
        invalid = (
            (b"", "invalid_json"), (b"1 2", "invalid_json"),
            (b"[1,]", "invalid_json"), (b"01", "invalid_json"),
            (b'"private\ntext"', "invalid_json"), (b"\xef\xbb\xbf1", "invalid_json"),
            (b"\xff", "invalid_utf8"), (b'"\xed\xa0\x80"', "invalid_utf8"),
            (b'"\\ud800"', "invalid_unicode"), (b'{"\\udfff":0}', "invalid_unicode"),
            (b'{"a":1,"a":2}', "duplicate_key"),
            (b'{"a":1,"\\u0061":2}', "duplicate_key"),
            (b"NaN", "non_finite"), (b"Infinity", "non_finite"),
            (b"-Infinity", "non_finite"), (b"[0,NaN]", "non_finite"),
        )
        for raw, code in invalid:
            for left, right in ((raw, None), (None, raw)):
                with self.subTest(code=code, raw=raw, position="left" if left is raw else "right"):
                    self.assertRejected(code, left, right)

    def test_every_supplied_member_is_admitted_before_known_results(self):
        cases = (
            ("eq", b"[]", b'["\\ud800"]', "invalid_unicode"),
            ("contains", b'[1,"\\ud800"]', b"1", "invalid_unicode"),
            ("contains", b'[{"a":1},{"b":NaN}]', b'{"c":0}', "non_finite"),
            ("subset_of", b"[]", b'[{"a":1,"a":2}]', "duplicate_key"),
            ("intersects", b"[]", b"[Infinity]", "non_finite"),
            ("contains", b"[]", b"1e1001", "number_limit"),
            ("contains", b'[1,{"extra":"' + b"x" * 4097 + b'"}]', b"1", "string_limit"),
        )
        for operator, left, right, code in cases:
            with self.subTest(operator=operator, code=code):
                self.assertRejected(code, left, right, operator)

    def test_byte_ceiling_applies_per_operand_including_whitespace(self):
        exact = b"0" + b" " * (typed.MAX_BYTES - 1)
        self.assertIs(typed.compare(typed.PROFILE, "eq", exact, b"0"), typed.Outcome.TRUE)
        self.assertRejected("byte_limit", exact + b" ")
        self.assertRejected("byte_limit", None, exact + b" ")

    def test_depth_ceiling_ignores_quoted_brackets_but_counts_every_container(self):
        exact = b"[" * 32 + b"0" + b"]" * 32
        self.assertIs(typed.compare(typed.PROFILE, "eq", exact, exact), typed.Outcome.UNKNOWN)
        self.assertRejected("depth_limit", b"[" + exact + b"]")
        quoted = json.dumps('\\"' + "[" * 50 + "]" * 50).encode()
        self.assertIs(typed.compare(typed.PROFILE, "eq", quoted, quoted), typed.Outcome.TRUE)

    def test_node_ceiling_counts_object_keys_and_array_members(self):
        exact = b"[" + b",".join([b"0"] * 9999) + b"]"
        self.assertIs(typed.compare(typed.PROFILE, "eq", exact, b"[]"), typed.Outcome.UNKNOWN)
        self.assertRejected("node_limit", exact[:-1] + b",0]")
        self.assertIs(typed.compare(typed.PROFILE, "eq", b'{"a":0}', b"0",
                                   limits=typed.Limits(max_nodes=3)), typed.Outcome.UNKNOWN)
        self.assertRejected("node_limit", b'{"a":0}', limits=typed.Limits(max_nodes=2))

    def test_string_ceiling_counts_unicode_scalars_and_includes_object_keys(self):
        exact = json.dumps("x" * 4096).encode()
        self.assertIs(typed.compare(typed.PROFILE, "eq", exact, exact), typed.Outcome.TRUE)
        self.assertRejected("string_limit", json.dumps("x" * 4097).encode())
        self.assertRejected("string_limit", json.dumps({"x" * 4097: 0}).encode())
        supplementary = '"𝄞𝄞"'.encode()
        self.assertIs(typed.compare(typed.PROFILE, "eq", supplementary, supplementary,
                                   limits=typed.Limits(max_string_chars=2)), typed.Outcome.TRUE)
        self.assertRejected("string_limit", supplementary, limits=typed.Limits(max_string_chars=1))

    def test_number_character_ceiling_covers_tokens_and_canonical_numeric_strings(self):
        exact = b"9" * 128
        self.assertIs(typed.compare(typed.PROFILE, "eq", exact, b'"' + exact + b'"'),
                      typed.Outcome.TRUE)
        for too_long in (exact + b"9", b'"' + exact + b'9"'):
            with self.subTest(quoted=too_long.startswith(b'"')):
                self.assertRejected("number_limit", too_long)
        self.assertIs(typed.compare(typed.PROFILE, "eq", b"1.00", b"1",
                                   limits=typed.Limits(max_number_chars=4)), typed.Outcome.TRUE)
        self.assertRejected("number_limit", b"1.00", limits=typed.Limits(max_number_chars=3))

    def test_exponent_ceiling_covers_original_exponent_and_resulting_scale(self):
        for raw in (b"1e1001", b"1e-1001", b"0e1001", b"0.1e-1000"):
            with self.subTest(raw=raw):
                self.assertRejected("number_limit", raw)
        no_exponents = typed.Limits(max_abs_exponent=0)
        self.assertIs(typed.compare(typed.PROFILE, "eq", b"1e0", b"1", limits=no_exponents),
                      typed.Outcome.TRUE)
        self.assertRejected("number_limit", b"1.0", limits=no_exponents)
        self.assertRejected("number_limit", b'"1.0"', limits=no_exponents)

    def test_work_budget_includes_original_whitespace_and_escaped_spellings(self):
        limits = typed.Limits(max_work=32)
        self.assertIs(typed.compare(typed.PROFILE, "eq", b"0", b"0", limits=limits),
                      typed.Outcome.TRUE)
        self.assertRejected("work_limit", b" " * 33 + b"0", limits=limits)
        self.assertRejected("work_limit", b'"' + b"\\u0078" * 6 + b'"', limits=limits)

    def test_comparison_work_exhaustion_rejects_a_preflighted_known_match(self):
        left = b"[" + b",".join([b"1"] * 300) + b"]"
        # Parsing these small valid arrays fits; their full Cartesian membership
        # comparisons exceed the fixed budget even though the first pair matches.
        self.assertRejected("work_limit", left, left, "intersects")
        self.assertIs(typed.compare(typed.PROFILE, "eq", left, left), typed.Outcome.UNKNOWN)

    def test_substring_work_is_reserved_before_a_known_match_or_empty_needle(self):
        self.assertRejected("work_limit", b'"' + b"x" * 1000 + b'"',
                            b'"' + b"x" * 1000 + b'"', "contains")
        self.assertRejected("work_limit", b'"' + b"x" * 20 + b'"', b'""', "contains",
                            limits=typed.Limits(max_work=50))
        self.assertIs(typed.compare(typed.PROFILE, "contains", b'"abc"', b'""'),
                      typed.Outcome.TRUE)

    def test_limits_only_tighten_and_are_revalidated_at_entry(self):
        for field, cap in vars(typed.Limits()).items():
            for invalid in (cap + 1, -1, True, 1.0):
                with self.subTest(field=field, invalid=invalid), self.assertRaisesRegex(
                        typed.ComparisonError, "^invalid_limits$"):
                    typed.Limits(**{field: invalid})
            if field != "max_abs_exponent":
                with self.subTest(field=field, invalid=0), self.assertRaisesRegex(
                        typed.ComparisonError, "^invalid_limits$"):
                    typed.Limits(**{field: 0})
        limits = typed.Limits()
        object.__setattr__(limits, "max_bytes", typed.MAX_BYTES + 1)
        self.assertRejected("invalid_limits", b"0", limits=limits)
        self.assertRejected("invalid_limits", b"0", limits={})

    def test_exact_comparison_does_not_depend_on_ambient_decimal_context(self):
        cases = load_fixture(FIXTURE.read_bytes())
        with localcontext() as context:
            context.prec = 2
            context.rounding = ROUND_UP
            context.Emin = -9
            context.Emax = 9
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            for case in cases:
                with self.subTest(case=case["name"]):
                    result = typed.compare(typed.PROFILE, case["operator"],
                                           operand(case["left_json"]), operand(case["right_json"]))
                    self.assertEqual(result.value, case["expected"])

    def test_frozen_reference_bytes_and_four_historical_outcomes_remain_intact(self):
        raw = REFERENCE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), REFERENCE_SHA256)
        namespace = {"__name__": "frozen_typed_comparison_control", "__file__": str(REFERENCE)}
        # Only fixed, locally verified repository source is executed. No operand,
        # archive, fixture or caller-provided path is executable authority.
        exec(compile(raw, str(REFERENCE), "exec"), namespace)
        historical = namespace["Evaluator"]({"selections": []}, {"items": []}, {"rules": []})
        cases = load_fixture(FIXTURE.read_bytes())
        residuals = [case for case in cases if case["name"].startswith("residual-")]
        self.assertEqual({case["name"] for case in residuals}, {
            "residual-bool-equality", "residual-nested-container-equality",
            "residual-nested-containment", "residual-subset"})
        for case in residuals:
            with self.subTest(case=case["name"]):
                self.assertIs(historical.compare(case["operator"], json.loads(case["left_json"]),
                                                  json.loads(case["right_json"])), True)
                self.assertIs(typed.compare(typed.PROFILE, case["operator"], operand(case["left_json"]),
                                            operand(case["right_json"])), typed.Outcome.UNKNOWN)
        self.assertIs(historical.compare("contains", [["1"]], [1]), False)
        with self.assertRaises(TypeError):
            historical.compare("subset_of", [[]], [[]])


if __name__ == "__main__":
    unittest.main()
