"""Run pinned read-only estimators; compare only the native two-byte KV payload.

No GPU inference, artifact downloads, estimator-source rewrites or total-peak
calibration. See the dated estimator comparison note for eligibility boundaries.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
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

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")

def payload_bytes(value):
    """Normalize a positive integral byte count without accepting booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("positive finite integral payload bytes required")
    if value <= 0 or (isinstance(value, float)
                      and (not math.isfinite(value) or not value.is_integer())):
        raise ValueError("positive finite integral payload bytes required")
    return int(value)

def kv_component(plan):
    """This exact llmfit field is GiB despite its _gb label; never scale totals."""
    rows = [r for r in plan["kv_alternatives"] if r["kv_quant"] == "fp16"]
    if len(rows) != 1 or plan["model_name"] != MODEL or plan["kv_quant"] != "fp16":
        raise ValueError("exact native KV component required")
    value = rows[0]["kv_cache_gb"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("positive finite KV size required")
    return payload_bytes(value * GIB)

def compare_payload(plan, run, point):
    """Validate the four-field geometry and storage width, not runtime fit."""
    if run["status"] != "success" or run["model_id"] != MODEL or run["revision"] != REVISION:
        raise ValueError("wrong measured model or unsuccessful observation")
    config, geometry, actual = run["configuration"], run["model_geometry"], run["actual_tokens"]
    if (config["kv_cache"] != "bf16" or actual["active_sequences"] != 1
            or (geometry["layers"], geometry["kv_heads"], geometry["head_dim"]) != (30, 3, 64)):
        raise ValueError("only single-sequence native two-byte KV is eligible")
    if point == "prefill":
        context, measured = actual["prompt_per_sequence"], run["native_kv_prefill_payload"]["measured_bytes"]
    elif point == "terminal":
        context, measured = actual["cache_tokens_per_sequence"], run["native_kv_steady_payload_bytes"]
    else:
        raise ValueError("unknown payload observation point")
    if plan["context"] != context or plan["quantization"] != "BF16":
        raise ValueError("context or requested weight precision differs")
    estimate = kv_component(plan)
    measured = payload_bytes(measured)
    signed = estimate - measured
    return {"point": point, "context": context, "estimated_payload_bytes": estimate,
            "measured_payload_bytes": measured, "signed_bytes": signed,
            "absolute_bytes": abs(signed), "signed_relative_percent": 100 * signed / measured,
            "quantity": "native two-byte full-attention KV tensor payload only",
            "scope": "storage-width/layout check; FP16 estimate versus BF16 tensors; no whole-runtime pair"}

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
    for name, expected in PINS.items():
        if digest(args.artifact_dir / name) != expected:
            parser.error("external artifact hash mismatch: " + name)
    catalog = json.loads((args.artifact_dir / "hf_models.json").read_text(encoding="utf-8"))
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
    for context, kv in ((256,"fp16"),(288,"fp16"),(2048,"fp16"),(2080,"fp16"),(2048,"q4_0"),(2080,"q4_0")):
        argv = ["--no-dashboard", "plan", MODEL, "--context", str(context), "--quant", "BF16", "--kv-quant", kv, "--json"]
        result = subprocess.run([str(args.artifact_dir / "llmfit.exe"), *argv], capture_output=True, text=True, timeout=90)
        name = f"llmfit-{context}-{kv}.json"
        if result.returncode != 0:
            write(args.output_dir / name,{"status":"estimator_rejection", "exit_code":result.returncode, "stdout":result.stdout, "stderr":result.stderr})
            raise RuntimeError("estimator failed; preserve output and stop")
        plan = json.loads(result.stdout)
        write(args.output_dir / name,plan)
        plans[(context,kv)] = plan
        ledger["estimator_executions"].append({"file":name, "sha256":digest(args.output_dir/name), "argv":["$LLMFIT",*argv], "exit_code":0,
            "whole_runtime_disposition":"mismatch: planning requirement, unpinned artifact/runtime; q4_0 is not Quanto INT4" if kv == "q4_0" else "mismatch: planning requirement, unpinned artifact/runtime"})
    for cell in ("D1","D2"):
        for rep in (1,2,3):
            name = f"mr09-{cell}-r{rep}.json"
            path = args.measurements / name
            run = json.loads(path.read_text(encoding="utf-8"))
            for point, context in (("prefill",run["actual_tokens"]["prompt_per_sequence"]),("terminal",run["actual_tokens"]["cache_tokens_per_sequence"])):
                pair = compare_payload(plans[(context,"fp16")],run,point)
                pair.update({"measurement_file":name,"measurement_sha256":digest(path),"estimator_file":f"llmfit-{context}-fp16.json"})
                ledger["component_pairs"].append(pair)
    run = json.loads((args.measurements / "mr09-D1-r1.json").read_text())
    # Feed the recorded capacity, in explicit decimal GB, rather than today's hardware.
    result = subprocess.run([args.node,"--input-type=module","-e",NODE_AUDIT,str((args.artifact_dir/"engine.mjs").resolve()),str(run["hardware"]["driver_total_bytes"]/1e9)],capture_output=True,text=True,check=True,timeout=30)
    modelfit = json.loads(result.stdout)
    write(args.output_dir / "modelfit-audit.json",modelfit)
    ledger["modelfit"] = {"file":"modelfit-audit.json","sha256":digest(args.output_dir/"modelfit-audit.json"),"status":"missing_inputs_or_model", "limits":["no exact catalog model match", "API has no artifact revision, runtime, context, cache layout or admitted concurrency arguments"], "engine_argv":["$NODE","--input-type=module","-e","NODE_AUDIT in recorded script","$ARTIFACT_DIR/engine.mjs","recorded driver_total_bytes / 1e9"]}
    ledger["component_pair_count"] = len(ledger["component_pairs"])
    ledger["independent_workload_cells"] = 2
    ledger["finished_utc"] = datetime.now(timezone.utc).isoformat()
    write(args.output_dir / "comparison.json",ledger)
    print(json.dumps({"component_pairs":len(ledger["component_pairs"]),"whole_runtime_pairs":0,"modelfit_exact_matches":len(modelfit["exactModelMatches"])}))

if __name__ == "__main__":
    main()
