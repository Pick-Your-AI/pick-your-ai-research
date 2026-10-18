"""Run pinned read-only estimators; compare only the native two-byte KV payload.

No GPU inference, artifact downloads, estimator-source rewrites or total-peak
calibration. See the dated estimator comparison note for eligibility boundaries.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess

MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
REVISION = "12fd25f77366fa6b3b4b768ec3050bf629380bac"
PINS = {
    "llmfit.exe": "3c5c783dd85cd78d2f91c9ac2809967a47b13708a9cc72112ed4a02c9d6cc981",
    "engine.mjs": "d6cdbde9a75cc160609bb0bced91d82dac0ec874316ccc7fa1f799c9feaa83f1",
    "data/models.json": "e8d88ff38cffa51cfc84ec7c3f80017580835ba06d31d4e936876903dfa523a6",
    "hf_models.json": "49d3ec213f38a18e7e3495cfe8d3e64e136db4b26e68aad851afc35498de0a16",
}
GIB = 2**30
NATIVE_CONTEXTS = {"D1": (256, 288), "D2": (2048, 2080)}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")

def input_json(text, *, exact_numbers=True):
    """Keep comparison number values exact after the existing finite-range gate.

    Catalog and Node-audit metadata explicitly retain their ordinary float view.
    JSON integer tokens remain integers; a decimal/exponent count cannot acquire
    that identity merely because its mathematical value is whole.
    """
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key: {key!r}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("JSON number exceeds finite numeric range")
        if not exact_numbers:
            return number
        try:
            exact = Decimal(value)
        except InvalidOperation as error:
            raise ValueError("JSON number exceeds exact decimal range") from error
        if not exact.is_finite():
            raise ValueError("JSON number exceeds exact decimal range")
        return exact

    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)

def payload_bytes(value):
    """Normalize a positive integral byte count without accepting booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, Fraction)):
        raise ValueError("positive finite integral payload bytes required")
    if (isinstance(value, (float, Decimal)) and not math.isfinite(value)) or value <= 0:
        raise ValueError("positive finite integral payload bytes required")
    if value != int(value):
        raise ValueError("positive finite integral payload bytes required")
    return int(value)

def kv_component(plan):
    """This exact llmfit field is GiB despite its _gb label; never scale totals."""
    rows = [r for r in plan["kv_alternatives"] if r["kv_quant"] == "fp16"]
    if len(rows) != 1 or plan["model_name"] != MODEL or plan["kv_quant"] != "fp16":
        raise ValueError("exact native KV component required")
    value = rows[0]["kv_cache_gb"]
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("positive finite KV size required")
    if isinstance(value, (float, Decimal)) and not math.isfinite(value):
        raise ValueError("positive finite KV size required")
    # A magnitude below 1e-10 GiB cannot contain one byte. Check the decimal
    # exponent before constructing a potentially enormous rational denominator.
    # This uses neither binary multiplication nor the caller's Decimal context.
    if isinstance(value, Decimal) and value.adjusted() < -10:
        raise ValueError("positive finite integral payload bytes required")
    return payload_bytes(Fraction(value) * GIB)

def measured_payload(run, point):
    """Admit exact integer native counts, geometry and two-byte storage only."""
    if run["status"] != "success" or run["model_id"] != MODEL or run["revision"] != REVISION:
        raise ValueError("wrong measured model or unsuccessful observation")
    config, geometry, actual = run["configuration"], run["model_geometry"], run["actual_tokens"]
    shape = (geometry["layers"], geometry["kv_heads"], geometry["head_dim"])
    if (config["kv_cache"] != "bf16" or type(config["active_sequences"]) is not int
            or config["active_sequences"] != 1 or type(actual["active_sequences"]) is not int
            or actual["active_sequences"] != 1
            or any(type(value) is not int for value in shape) or shape != (30, 3, 64)):
        raise ValueError("only single-sequence native two-byte KV is eligible")
    if point == "prefill":
        context, measured = actual["prompt_per_sequence"], run["native_kv_prefill_payload"]["measured_bytes"]
    elif point == "terminal":
        context, measured = actual["cache_tokens_per_sequence"], run["native_kv_steady_payload_bytes"]
    else:
        raise ValueError("unknown payload observation point")
    if type(context) is not int or context <= 0:
        raise ValueError("positive integer observed context required")
    return context, payload_bytes(measured)

def compare_payload(plan, run, point):
    """Validate the four-field geometry and storage width, not runtime fit."""
    context, measured = measured_payload(run, point)
    if (type(plan["context"]) is not int or plan["context"] != context
            or plan["quantization"] != "BF16"):
        raise ValueError("context or requested weight precision differs")
    estimate = kv_component(plan)
    signed = estimate - measured
    return {"point": point, "context": context, "estimated_payload_bytes": estimate,
            "measured_payload_bytes": measured, "signed_bytes": signed,
            "absolute_bytes": abs(signed), "signed_relative_percent": 100 * signed / measured,
            "quantity": "native two-byte full-attention KV tensor payload only",
            "scope": "storage-width/layout check; FP16 estimate versus BF16 tensors; no whole-runtime pair"}

def read_measurements(directory):
    """Check all retained input bytes before creating output or running a tool."""
    runs = {}
    for cell, contexts in NATIVE_CONTEXTS.items():
        for rep in (1, 2, 3):
            name = f"mr09-{cell}-r{rep}.json"
            raw = (directory / name).read_bytes()
            run = input_json(raw.decode("utf-8"))
            if (run["cell"] != cell or type(run["repetition"]) is not int
                    or run["repetition"] != rep):
                raise ValueError("measurement identity differs from expected file: " + name)
            for point, expected in zip(("prefill", "terminal"), contexts):
                context, _ = measured_payload(run, point)
                if context != expected:
                    raise ValueError("observed context differs from retained cell: " + name)
            configured = run["configuration"]
            declared_counts = (configured["prompt_tokens_per_sequence"],
                               configured["decode_forwards_per_sequence"],
                               run["actual_tokens"]["decode_forwards_per_sequence"])
            expected_counts = (contexts[0], contexts[1] - contexts[0], contexts[1] - contexts[0])
            if (any(type(value) is not int for value in declared_counts)
                    or declared_counts != expected_counts):
                raise ValueError("declared context counts differ from retained cell: " + name)
            runs[name] = (run, hashlib.sha256(raw).hexdigest())
    return runs

NODE_AUDIT = r"""
const {pathToFileURL} = await import('node:url');
const {DATASET, getRecommendations, ramBudgetRatio} = await import(pathToFileURL(process.argv[1]));
const input = {deviceType:'PC', chip:'NVIDIA GeForce RTX 5070 Ti', ramGb:Number(process.argv[2]), priority:'Balanced', useCase:'General'};
const rows = getRecommendations(input);
console.log(JSON.stringify({input, ratio:ramBudgetRatio(input.ramGb), budget:input.ramGb*ramBudgetRatio(input.ramGb), datasetRecords:DATASET.length, exactModelMatches:rows.filter(m=>m.name==='HuggingFaceTB/SmolLM2-135M-Instruct'||m.name==='SmolLM2 135M'), relatedNames:rows.filter(m=>/smollm2/i.test(m.name)).map(m=>m.name)}));
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, default=Path("research/market/measurements"))
    parser.add_argument("--node", default="node")
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("fresh output directory required; never overwrite evidence")
    runs = read_measurements(args.measurements)
    for name, expected in PINS.items():
        if digest(args.artifact_dir / name) != expected:
            parser.error("external artifact hash mismatch: " + name)
    catalog = input_json((args.artifact_dir / "hf_models.json").read_text(encoding="utf-8"), exact_numbers=False)
    model = next(row for row in catalog if row["name"] == MODEL)
    geometry = {k:model[k] for k in ("parameters_raw", "num_hidden_layers", "num_key_value_heads", "head_dim", "format", "quantization")}
    if (geometry["num_hidden_layers"], geometry["num_key_value_heads"], geometry["head_dim"]) != (30, 3, 64):
        parser.error("catalog geometry mismatch")
    args.output_dir.mkdir(parents=True)
    ledger = {"classification":"real estimator execution against existing real runtime records; bounded component comparison", "started_utc":datetime.now(timezone.utc).isoformat(),
              "script_sha256":digest(Path(__file__)), "artifact_sha256":PINS, "catalog_geometry":geometry,
              "llmfit_version":subprocess.check_output([str(args.artifact_dir / "llmfit.exe"), "--version"], text=True).strip(),
              "node_version":subprocess.check_output([args.node, "--version"],text=True).strip(),
              "estimator_executions":[], "component_pairs":[], "whole_runtime_pairs":0,
              "approved_tolerance":None, "fit_verdict":"unavailable; quantities/runtime do not match"}
    plans = {}
    # Four native-cache snapshots plus two explicit non-equivalent INT4 probes.
    native_plans = [(context, "fp16") for contexts in NATIVE_CONTEXTS.values() for context in contexts]
    for context, kv in [*native_plans, (2048, "q4_0"), (2080, "q4_0")]:
        argv = ["--no-dashboard", "plan", MODEL, "--context", str(context), "--quant", "BF16", "--kv-quant", kv, "--json"]
        result = subprocess.run([str(args.artifact_dir / "llmfit.exe"), *argv], capture_output=True, text=True, timeout=90)
        name = f"llmfit-{context}-{kv}.json"
        if result.returncode != 0:
            write(args.output_dir / name,{"status":"estimator_rejection", "exit_code":result.returncode, "stdout":result.stdout, "stderr":result.stderr})
            raise RuntimeError("estimator failed; preserve output and stop")
        plan = input_json(result.stdout)
        # Retain the validated captured JSON; reserializing Decimal values as
        # floats would lose the very source precision used by the comparison.
        (args.output_dir / name).write_text(result.stdout, encoding="utf-8", newline="\n")
        plans[(context,kv)] = plan
        ledger["estimator_executions"].append({"file":name, "sha256":digest(args.output_dir/name), "argv":["$LLMFIT",*argv], "exit_code":0,
            "whole_runtime_disposition":"mismatch: planning requirement, unpinned artifact/runtime; q4_0 is not Quanto INT4" if kv == "q4_0" else "mismatch: planning requirement, unpinned artifact/runtime"})
    for cell in ("D1","D2"):
        for rep in (1,2,3):
            name = f"mr09-{cell}-r{rep}.json"
            run, measurement_sha256 = runs[name]
            for point, context in (("prefill",run["actual_tokens"]["prompt_per_sequence"]),("terminal",run["actual_tokens"]["cache_tokens_per_sequence"])):
                pair = compare_payload(plans[(context,"fp16")],run,point)
                pair.update({"measurement_file":name,"measurement_sha256":measurement_sha256,"estimator_file":f"llmfit-{context}-fp16.json"})
                ledger["component_pairs"].append(pair)
    run = runs["mr09-D1-r1.json"][0]
    # Feed the recorded capacity, in explicit decimal GB, rather than today's hardware.
    capacity_bytes = run["hardware"]["driver_total_bytes"]
    # This audit-only metadata retains the former JSON float view; payload
    # comparisons above continue to use the exact original number values.
    if isinstance(capacity_bytes, Decimal):
        capacity_bytes = float(capacity_bytes)
    result = subprocess.run([args.node,"--input-type=module","-e",NODE_AUDIT,str((args.artifact_dir/"engine.mjs").resolve()),str(capacity_bytes/1e9)],capture_output=True,text=True,check=True,timeout=30)
    modelfit = input_json(result.stdout, exact_numbers=False)
    write(args.output_dir / "modelfit-audit.json",modelfit)
    ledger["modelfit"] = {"file":"modelfit-audit.json","sha256":digest(args.output_dir/"modelfit-audit.json"),"status":"missing_inputs_or_model", "limits":["no exact catalog model match", "API has no artifact revision, runtime, context, cache layout or admitted concurrency arguments"], "engine_argv":["$NODE","--input-type=module","-e","NODE_AUDIT in recorded script","$ARTIFACT_DIR/engine.mjs","recorded driver_total_bytes / 1e9"]}
    ledger["component_pair_count"] = len(ledger["component_pairs"])
    ledger["independent_workload_cells"] = 2
    ledger["finished_utc"] = datetime.now(timezone.utc).isoformat()
    write(args.output_dir / "comparison.json",ledger)
    print(json.dumps({"component_pairs":len(ledger["component_pairs"]),"whole_runtime_pairs":0,"modelfit_exact_matches":len(modelfit["exactModelMatches"])}))

if __name__ == "__main__":
    main()
