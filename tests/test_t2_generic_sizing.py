"""Synthetic arithmetic regressions; no model load, GPU or measurement claim."""
import contextlib
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
import importlib.util
import io
import json
from pathlib import Path
import unittest


PATH = (Path(__file__).resolve().parents[1] / "research" /
        "T2-infrastructure" / "compute" / "sizing_generic.py")
SPEC = importlib.util.spec_from_file_location("t2_generic_sizing", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GenericSizing(unittest.TestCase):
    def size(self, **changes):
        # Every negative case overrides one field of an otherwise valid input.
        inputs = dict(total_size_bytes=8_000_000_000, quant="synthetic-post-quant",
                      ctx=16, concurrency=1, card_vram_gb=Decimal("24.5"),
                      runtime_overhead_gib=0, transfer_buffer_ratio=0,
                      layers=28, kv_heads=4, head_dim=128,
                      kv_element_bytes=2, block_tokens=16)
        inputs.update(changes)
        return MODULE.size_model(**inputs)

    def example(self, **changes):
        return self.size(layers=None, kv_heads=None, head_dim=None,
                         kv_element_bytes=None, block_tokens=None,
                         geometry_example=MODULE.QWEN_EXAMPLE, **changes)

    def test_pinned_named_example_matches_accepted_cache_arithmetic(self):
        short = self.example(ctx=8192)
        loaded = self.example(ctx=32768, concurrency=8)
        self.assertEqual(short["modeled_attention_kv_bytes"], 469_762_048)
        self.assertEqual(loaded["modeled_attention_kv_bytes"], 15_032_385_536)
        explicit = self.size(ctx=8192)
        self.assertEqual(short["geometry"], explicit["geometry"])
        self.assertEqual(short["modeled_per_device_bytes"], explicit["modeled_per_device_bytes"])

    def test_missing_or_partial_geometry_requires_an_explicit_choice(self):
        fields = ("layers", "kv_heads", "head_dim", "kv_element_bytes", "block_tokens")
        cases = [{field: None} for field in fields]
        cases += [{field: None for field in fields},
                  dict(layers=56, kv_heads=None, head_dim=None)]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "geometry"):
                self.size(**changes)

    def test_named_example_cannot_override_supplied_geometry(self):
        with self.assertRaisesRegex(ValueError, "combined"):
            self.size(geometry_example=MODULE.QWEN_EXAMPLE)
        for value in ("qwen", "", True, 1):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "geometry_example"):
                self.size(geometry_example=value)

    def test_complete_custom_geometry_and_cache_dtype_are_honored(self):
        baseline = self.size()["modeled_attention_kv_bytes"]
        self.assertEqual(baseline, 917_504)
        self.assertEqual(self.size(layers=56)["modeled_attention_kv_bytes"], 1_835_008)
        self.assertEqual(self.size(kv_heads=8)["modeled_attention_kv_bytes"], baseline * 2)
        self.assertEqual(self.size(head_dim=64)["modeled_attention_kv_bytes"], baseline // 2)
        self.assertEqual(self.size(kv_element_bytes=1)["modeled_attention_kv_bytes"], baseline // 2)

    def test_blocks_round_each_independent_reserved_sequence(self):
        self.assertEqual(self.size(ctx=1)["modeled_attention_kv_bytes"], 917_504)
        self.assertEqual(self.size(ctx=16)["modeled_attention_kv_bytes"], 917_504)
        self.assertEqual(self.size(ctx=17)["modeled_attention_kv_bytes"], 1_835_008)
        self.assertEqual(self.size(ctx=17, concurrency=3)["rounded_reserved_tokens"], 96)
        self.assertEqual(self.size(ctx=17, concurrency=3)["modeled_attention_kv_bytes"], 5_505_024)
        self.assertEqual(self.size(ctx=17, block_tokens=1)["rounded_reserved_tokens"], 17)

    def test_geometry_requires_positive_integer_dimensions(self):
        for field in ("layers", "kv_heads", "head_dim", "kv_element_bytes", "block_tokens"):
            for value in (0, -1, True, False, 1.0, 1.5, Decimal(1), "1"):
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                    self.size(**{field: value})

    def test_counts_reject_fractional_boolean_and_coercible_values(self):
        for field in ("ctx", "concurrency", "n_devices"):
            for value in (None, 0, -1, True, False, 16.0, 16.5, Decimal(16), "16"):
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                    self.size(**{field: value})

    def test_weight_bytes_reject_negative_fraction_and_non_integer_aliases(self):
        for value in (-0.5, -1, True, False, 8e9, Decimal(8), "8", None,
                      float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "total_size_bytes"):
                self.size(total_size_bytes=value)

    def test_finite_exact_quantities_have_field_specific_guards(self):
        for field in ("card_vram_gb", "runtime_overhead_gib", "transfer_buffer_ratio"):
            for value in (None, True, False, 1.0, "1", Decimal("NaN"), Decimal("sNaN"),
                          Decimal("Infinity"), Decimal("-Infinity"), float("nan"), float("inf")):
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, field):
                    self.size(**{field: value})
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                self.size(**{field: Decimal("-0.1")})

    def test_zero_is_distinct_from_missing_and_capacity_must_be_positive(self):
        result = self.size(total_size_bytes=0, runtime_overhead_gib=0, transfer_buffer_ratio=0)
        self.assertEqual(result["resident_weight_bytes"], 0)
        self.assertEqual(result["modeled_per_device_bytes"], (Fraction(917_504),))
        self.assertIsNone(result["host_ram_bytes"])
        self.assertIsNone(result["unmodeled_recurrent_state_bytes"])
        with self.assertRaisesRegex(ValueError, "card_vram_gb"):
            self.size(card_vram_gb=0)

    def test_decimal_capacity_retains_the_fraction_rejected_by_original_truncation(self):
        result = self.size(total_size_bytes=24_200_000_000, card_vram_gb=Decimal("24.5"))
        self.assertEqual(result["card_vram_gb"], Fraction(49, 2))
        self.assertEqual(result["modeled_bytes_exceed_card_capacity"], (False,))
        self.assertEqual(self.size(total_size_bytes=24_200_000_000,
                                   card_vram_gb=24)["modeled_bytes_exceed_card_capacity"], (True,))
        self.assertEqual(result["admission"], "unknown")

    def test_quant_label_does_not_requantize_weight_or_cache_bytes(self):
        first = self.size(quant="bf16")
        second = self.size(quant="Q4_K_M")
        for field in ("resident_weight_bytes", "modeled_attention_kv_bytes", "modeled_per_device_bytes"):
            self.assertEqual(first[field], second[field])
        self.assertEqual(second["quant"], "Q4_K_M")
        for value in (None, "", "  ", True, 4):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "quant"):
                self.size(quant=value)

    def test_full_moe_residency_never_substitutes_active_expert_count(self):
        dense = self.size(total_size_bytes=50_000_000_000)
        moe = self.size(total_size_bytes=50_000_000_000, is_moe=True)
        self.assertEqual(moe["resident_weight_bytes"], 50_000_000_000)
        self.assertEqual(dense["modeled_per_device_bytes"], moe["modeled_per_device_bytes"])
        self.assertEqual(moe["offloaded_expert_bytes"], 0)

    def test_explicit_offload_reduces_only_resident_weights_and_their_buffer(self):
        common = dict(total_size_bytes=50_000_000_000, is_moe=True,
                      transfer_buffer_ratio=Decimal("0.1"))
        resident = self.size(**common)
        offload = self.size(**common, offload_policy="experts_to_cpu",
                            offloaded_expert_bytes=16_000_000_000)
        self.assertEqual(offload["resident_weight_bytes"], 34_000_000_000)
        self.assertEqual(offload["modeled_attention_kv_bytes"], resident["modeled_attention_kv_bytes"])
        self.assertEqual(resident["modeled_pool_vram_gb"] - offload["modeled_pool_vram_gb"],
                         Fraction(88, 5))
        self.assertIsNone(offload["host_ram_bytes"])
        self.assertIsNone(offload["latency_ms"])

    def test_offload_guards_do_not_silently_discard_or_overstate_experts(self):
        for value in (None, -1, -0.5, True, 1.0, Decimal(1), "1", 8_000_000_001):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "offloaded_expert_bytes"):
                self.size(is_moe=True, offload_policy="experts_to_cpu", offloaded_expert_bytes=value)
        with self.assertRaisesRegex(ValueError, "is_moe"):
            self.size(offload_policy="experts_to_cpu", offloaded_expert_bytes=1)
        with self.assertRaisesRegex(ValueError, "requires experts_to_cpu"):
            self.size(is_moe=True, offloaded_expert_bytes=1)
        for value in (None, "other", True):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "offload_policy"):
                self.size(offload_policy=value)
        for value in (1, "true", None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "is_moe"):
                self.size(is_moe=value)

    def test_offload_zero_and_whole_weight_boundaries_are_explicit(self):
        zero = self.size(is_moe=True, offload_policy="experts_to_cpu", offloaded_expert_bytes=0)
        whole = self.size(is_moe=True, offload_policy="experts_to_cpu",
                          offloaded_expert_bytes=8_000_000_000)
        self.assertEqual(zero["resident_weight_bytes"], 8_000_000_000)
        self.assertEqual(whole["resident_weight_bytes"], 0)
        self.assertEqual(whole["modeled_per_device_bytes"], (Fraction(917_504),))
        self.assertEqual(whole["admission"], "unknown")

    def test_multi_device_requires_a_complete_exact_partition(self):
        for value in (None, (), (1,), (1, 0), (Decimal("0.4"), Decimal("0.4")),
                      (True, False), (0.5, 0.5), ("0.5", "0.5"),
                      (Decimal("NaN"), Decimal("0.5")), (Decimal("Infinity"), 1)):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "device_payload_fractions"):
                self.size(n_devices=2, device_payload_fractions=value)
        with self.assertRaisesRegex(ValueError, "device_payload_fractions"):
            self.size(device_payload_fractions=(True,))

    def test_runtime_overhead_is_replicated_instead_of_sharded_with_payload(self):
        result = self.size(total_size_bytes=98, ctx=1, layers=1, kv_heads=1, head_dim=1,
                           kv_element_bytes=1, block_tokens=1, runtime_overhead_gib=1,
                           n_devices=2, device_payload_fractions=(Fraction(3, 4), Fraction(1, 4)))
        self.assertEqual(result["modeled_per_device_bytes"], (2**30 + 75, 2**30 + 25))
        self.assertEqual(result["modeled_pool_vram_gb"], Fraction(2 * 2**30 + 100, 10**9))
        self.assertEqual(result["modeled_peak_per_device_vram_gb"], Fraction(2**30 + 75, 10**9))

    def test_payload_lower_bound_of_two_can_still_exceed_both_device_capacities(self):
        result = self.size(total_size_bytes=40_000_000_000, card_vram_gb=24,
                           runtime_overhead_gib=3, transfer_buffer_ratio=Decimal("0.1"),
                           n_devices=2, device_payload_fractions=(Fraction(1, 2), Fraction(1, 2)))
        self.assertEqual(result["modeled_payload_device_lower_bound"], 2)
        self.assertEqual(result["modeled_peak_per_device_vram_gb"], Fraction("25.2217300992"))
        self.assertEqual(result["modeled_bytes_exceed_card_capacity"], (True, True))
        self.assertEqual(result["admission"], "unknown")
        for misleading_field in ("fits", "needs_devices", "confidence", "scenario_range_gb"):
            self.assertNotIn(misleading_field, result)

    def test_partition_conserves_payload_and_is_order_independent(self):
        common = dict(n_devices=3, runtime_overhead_gib=2, transfer_buffer_ratio=Fraction(1, 7))
        shares = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
        first = self.size(**common, device_payload_fractions=shares)
        second = self.size(**common, device_payload_fractions=list(reversed(shares)))
        self.assertEqual(first["modeled_per_device_bytes"], tuple(reversed(second["modeled_per_device_bytes"])))
        self.assertEqual(first["modeled_pool_vram_gb"], second["modeled_pool_vram_gb"])
        self.assertEqual(first["modeled_peak_per_device_vram_gb"], second["modeled_peak_per_device_vram_gb"])
        payload = 8_000_917_504 * Fraction(8, 7)
        self.assertEqual(sum(first["modeled_per_device_bytes"]), payload + 6 * 2**30)
        shares[0] = Fraction(1)
        self.assertEqual(first["device_payload_fractions"][0], Fraction(1, 2))

    def test_exact_capacity_boundary_and_one_byte_excess(self):
        inputs = dict(ctx=1, layers=1, kv_heads=1, head_dim=1,
                      kv_element_bytes=1, block_tokens=1, card_vram_gb=Decimal("0.0000001"))
        self.assertEqual(self.size(total_size_bytes=98, **inputs)["modeled_bytes_exceed_card_capacity"], (False,))
        self.assertEqual(self.size(total_size_bytes=99, **inputs)["modeled_bytes_exceed_card_capacity"], (True,))

    def test_large_integer_and_decimal_context_cannot_round_away_excess(self):
        inputs = dict(total_size_bytes=2**53 + 1, ctx=1, layers=1, kv_heads=1,
                      head_dim=1, kv_element_bytes=1, block_tokens=1,
                      card_vram_gb=Fraction(2**53 + 2, 10**9))
        expected = self.size(**inputs)
        with localcontext() as context:
            context.prec = 2
            actual = self.size(**inputs)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["modeled_bytes_exceed_card_capacity"], (True,))
        self.assertEqual(actual["modeled_per_device_bytes"], (2**53 + 3,))

    def test_sensitivity_does_not_turn_low_live_arithmetic_into_admitted_fit(self):
        live = self.size(total_size_bytes=16_000_000_000, card_vram_gb=24,
                         runtime_overhead_gib=3, transfer_buffer_ratio=Decimal("0.1"))
        original = deepcopy(live)
        scenario = MODULE.capacity_sensitivity(live["modeled_per_device_bytes"],
                                                reserve_fraction=Decimal("0.2"))
        self.assertLess(live["modeled_peak_per_device_vram_gb"], 24)
        self.assertGreater(scenario["scenario_required_gb_per_device"][0], 24)
        self.assertEqual(live, original)
        self.assertEqual(live["admission"], "unknown")
        self.assertNotIn("confidence", scenario)
        self.assertNotIn("fits", scenario)

    def test_sensitivity_uses_exact_explicit_reserve_per_device(self):
        no_reserve = MODULE.capacity_sensitivity((100, 50), reserve_fraction=0)
        reserved = MODULE.capacity_sensitivity((100, 50), reserve_fraction=Fraction(1, 5))
        self.assertEqual(no_reserve["scenario_required_gb_per_device"],
                         (Fraction(100, 10**9), Fraction(50, 10**9)))
        self.assertEqual(reserved["scenario_required_gb_per_device"],
                         (Fraction(125, 10**9), Fraction(125, 2 * 10**9)))
        reserve = Decimal("0.0000000000000000000000000000000000000001")
        with localcontext() as context:
            context.prec = 2
            tiny = MODULE.capacity_sensitivity((100,), reserve_fraction=reserve)
        self.assertGreater(tiny["scenario_required_gb_per_device"][0], Fraction(100, 10**9))

    def test_sensitivity_rejects_missing_nonfinite_and_out_of_domain_inputs(self):
        for reserve in (None, True, 0.1, "0.1", -1, 1, Decimal("1.1"),
                        Decimal("NaN"), Decimal("Infinity")):
            with self.subTest(reserve=reserve), self.assertRaisesRegex(ValueError, "reserve_fraction"):
                MODULE.capacity_sensitivity((100,), reserve_fraction=reserve)
        for values in (None, (), [], (None,), (-1,), (True,), (1.0,), (Decimal("NaN"),)):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, "per_device_modeled_bytes"):
                MODULE.capacity_sensitivity(values, reserve_fraction=0)
        self.assertEqual(MODULE.capacity_sensitivity((0,), reserve_fraction=0)["scenario_required_pool_gb"], 0)

    def test_reported_scenarios_are_unverified_demonstrations_without_peak_pairs(self):
        rows = MODULE.reported_scenario_demonstrations()
        self.assertEqual([row["reported_scenario_id"] for row in rows],
                         ["M1_dense_fit", "M2_moe_offload", "M3_multigpu"])
        for row in rows:
            self.assertFalse(row["eligible_peak_measurement_pair"])
            self.assertIsNone(row["model_artifact_pin"])
            self.assertIsNone(row["engine_build_pin"])
            self.assertIn("unverified", row["input_basis"])
            value = row["arithmetic"]
            self.assertEqual(value["admission"], "unknown")
            self.assertEqual(value["assumed_runtime_bytes_per_device"], 3 * 2**30)
            for field in ("runtime_peak_allocated_bytes", "runtime_peak_reserved_bytes",
                          "unmodeled_recurrent_state_bytes", "host_ram_bytes", "latency_ms"):
                self.assertIsNone(value[field])

    def test_hybrid_demo_uses_an_asserted_aggregate_without_invented_expert_geometry(self):
        value = MODULE.reported_scenario_demonstrations()[1]["arithmetic"]
        self.assertEqual(value["offloaded_expert_bytes"], 19_769_655_296)
        self.assertEqual(value["resident_weight_bytes"], 2_544_159_232)
        self.assertEqual(value["modeled_attention_kv_bytes"], 20_971_520)
        self.assertIsNone(value["unmodeled_recurrent_state_bytes"])
        self.assertNotIn("expert_bytes", value)

    def test_two_device_demo_uses_a_hypothetical_partition_not_fitted_observations(self):
        rows = MODULE.reported_scenario_demonstrations()
        one, two = rows[0]["arithmetic"], rows[2]["arithmetic"]
        self.assertEqual(two["device_payload_fractions"], (Fraction(1, 2), Fraction(1, 2)))
        self.assertEqual(two["modeled_pool_vram_gb"] - one["modeled_pool_vram_gb"], Fraction(3 * 2**30, 10**9))
        self.assertEqual(two["modeled_per_device_bytes"][0], two["modeled_per_device_bytes"][1])

    def test_main_prints_only_labeled_arithmetic_demonstrations(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            MODULE.main()
        rows = json.loads(output.getvalue())
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["eligible_peak_measurement_pair"] is False for row in rows))
        self.assertTrue(all(row["arithmetic"]["admission"] == "unknown" for row in rows))
        self.assertNotIn("PREDICTED-vs-MEASURED", output.getvalue())


if __name__ == "__main__":
    unittest.main()
