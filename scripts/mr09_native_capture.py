"""Validate/publish bounded native qualification captures, never runtime fit claims."""
import argparse
import csv
import io
import math
import hashlib
import json
from pathlib import Path
import re
from mr09_total_memory_setup import managed_snapshot_interval, strict_json, require_bindings

DIRECTORY=Path("research/market/measurements/native-qualification-2026-10-18")

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def loads(text):
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result: raise ValueError("duplicate native event key")
            result[k]=v
        return result
    def invalid(value): raise ValueError("non-finite native JSON number")
    def finite(value):
        number=float(value)
        if not math.isfinite(number): raise ValueError("overflowing native JSON number")
        return number
    return json.loads(text,object_pairs_hook=unique,parse_constant=invalid,parse_float=finite)

def validate_capture(record):
    if (type(record.get("exit_code")) is not int or record["exit_code"]!=0
            or record.get("status")!="native_initialization_completed"
            or type(record.get("generation_forwards")) is not int or record["generation_forwards"]!=0
            or record.get("warmup") is not False):
        raise ValueError("successful initialization-only qualification required")
    events=[loads(line) for line in record["stdout"].splitlines() if line.strip()]
    def one(key,value):
        found=[e for e in events if e.get(key)==value]
        if len(found)!=1: raise ValueError("missing/ambiguous native event: "+value)
        return found[0]
    probe=one("mr09_event","qualification")
    if probe["status"]!="probe_passed" or probe["device"]!="CUDA0" or probe["decode_api_loaded"] is not False or probe["graphs_disabled"] is not True:
        raise ValueError("CUDA/graph boundary not qualified")
    effective=one("mr09_event","effective")
    expected={"mr09_event":"effective","no_alloc":False,"context":512,"batch":256,"ubatch":256,"sequences":1,"generation_forwards":0,"warmup":False,"extra_buffer_types":False}
    if json.dumps(effective,sort_keys=True)!=json.dumps(expected,sort_keys=True):
        raise ValueError("effective native tuple drift")
    result=one("mr09_event","result")
    if result["status"]!="initialization_qualified": raise ValueError("incomplete cleanup/capture")
    caps=[e for e in events if e.get("mr09_event")=="cap"]
    if len(caps)!=3 or {e["stage"] for e in caps}!={"after_probe","before_capture","after_cleanup"}:
        raise ValueError("missing/duplicate native cap phase")
    if [e["stage"] for e in caps]!=["after_probe","before_capture","after_cleanup"]:
        raise ValueError("native phase ordering drift")
    caps={e["stage"]:e for e in caps}
    for c in caps.values():
        for key in ("cap_bytes","live_bytes","peak_admitted_bytes","admission_denials","native_allocator_calls","graph_denials"):
            if type(c[key]) is not int or c[key]<0: raise ValueError("invalid native cap counter")
        if c["cap_bytes"]!=2136809472 or c["cap_bytes"]>probe["driver_total_bytes"]//8: raise ValueError("expanded cap")
        if not c["live_bytes"]<=c["peak_admitted_bytes"]<=c["cap_bytes"]: raise ValueError("native cap exceeded")
        if c["admission_denials"]!=1 or c["graph_denials"]!=1: raise ValueError("unexpected allocation/graph attempt")
    if caps["after_probe"]["native_allocator_calls"]!=1 or caps["after_probe"]["live_bytes"]!=0 or caps["after_probe"]["peak_admitted_bytes"]!=8388608:
        raise ValueError("bounded 8 MiB probe not demonstrated")
    if any(caps[stage]["native_allocator_calls"]!=4 for stage in ("before_capture","after_cleanup")):
        raise ValueError("unexpected native allocation count")
    if caps["after_cleanup"]["live_bytes"]!=0: raise ValueError("native buffer cleanup incomplete")
    data=one("type","fit_memory_breakdown")["data"]
    interval=managed_snapshot_interval({**data,"metric":"managed_device_buffers_snapshot","no_alloc":effective["no_alloc"]})
    live=caps["before_capture"]["live_bytes"]
    if not interval[0]<=live<=interval[1]: raise ValueError("native reported buffers do not reconcile with admission ledger")
    if "offloaded 31/31 layers to GPU" not in record["stderr"]: raise ValueError("missing effective layer placement evidence")
    if "(load_mode = mmap)" not in record["stderr"] or "K (f16)" not in record["stderr"] or "V (f16)" not in record["stderr"]:
        raise ValueError("effective mmap/KV evidence missing")
    def output_setting(name,expected):
        matches=re.findall(r"^llama_context: "+name+r"\s*=\s*(\d+)\s*$",record["stderr"],re.MULTILINE)
        if matches!=[str(expected)]: raise ValueError("native output reservation drift")
        return expected
    outputs=output_setting("n_outputs_max",256)
    per_seq=output_setting("n_outputs_max_per_seq",1)
    return {"exact_admitted_live_buffer_bytes":live,"native_self_byte_interval":list(interval),
            "native_device_row":next(r for r in data["rows"] if r["kind"]=="device"),
            "cap_bytes":caps["before_capture"]["cap_bytes"],"peak_admitted_bytes":caps["before_capture"]["peak_admitted_bytes"],
            "initialization_graph_dispatches":caps["before_capture"]["graph_denials"]-caps["after_probe"]["graph_denials"],
            "cleanup_live_bytes":caps["after_cleanup"]["live_bytes"],
            "runtime_n_outputs_max":outputs,"runtime_n_outputs_max_per_seq":per_seq}

def summarize(directory):
    build=strict_json(directory/"build-loader-v2.json")
    observations=[];cohort=None
    for rep in (1,2,3):
        path=directory/f"init-r{rep}.json";record=strict_json(path)
        require_bindings(record, {
            "argv":["$NATIVE_INIT","$RUNTIME_DIR","2136809472","$GGUF_FILE"],
            "harness_sha256":"07c2f8587b58a6dbe557d7e7f395f765ec03c18122386f6456333338f832f09e",
            "harness_git_ref":"7805816b3b59f973ec9e87a03b8c807511641700",
            "launcher_sha256":"6a645f212c3b947789345dc739d88d554f3e083021db3cc0f7abfebc8ff1f8b8",
            "model_sha256":"f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57",
            "runtime_artifact_ledger_sha256":"d788e18ba59ab6f210c1ceb61599f39269440a774664c8f515ffca9a7041cfcd",
            "preflight_file":f"init-r{rep}-preflight.json",
        }, "native capture pins")
        if type(record["repetition"]) is not int or record["repetition"]!=rep: raise ValueError("wrong repetition")
        if record["harness_sha256"]!=build["executables"]["native-init.exe"]: raise ValueError("wrong native executable")
        if sha(directory/record["preflight_file"])!=record["preflight_sha256"]: raise ValueError("preflight hash mismatch")
        if not all(strict_json(directory/record["preflight_file"])["guards"].values()): raise ValueError("failed native preflight")
        if sha(directory/"runtime-artifacts.json")!=record["runtime_artifact_ledger_sha256"]: raise ValueError("runtime artifact drift")
        hardware_rows=list(csv.DictReader(io.StringIO(record["driver_csv"])))
        if len(hardware_rows)!=1: raise ValueError("single system GPU record required")
        hardware={k.strip():v.strip() for k,v in hardware_rows[0].items()}
        hardware_pin=tuple(hardware[k] for k in ("name","driver_version","memory.total [MiB]"))
        signature=tuple(record[k] for k in ("harness_sha256","harness_git_ref","launcher_sha256","model_sha256","runtime_artifact_ledger_sha256"))+hardware_pin
        if cohort is not None and cohort!=signature: raise ValueError("mixed qualification cohort")
        cohort=signature
        observations.append({"file":path.name,"sha256":sha(path),"repetition":rep,**validate_capture(record)})
    return {"classification":"three real native initialization qualification trials; receiving review outstanding",
            "runtime_commit":"620d2225cc436ab0b001e3200e590e3b286ef9ab","harness_sha256":cohort[0],
            "qualified_scope":["CUDA0 initialization and 8 MiB clear/release","pre-call managed-buffer cap for pinned initialization-only interface","native capture reconciles with exact admitted-buffer ledger"],
            "not_qualified":["graph execution/VMM scratch pools","opaque CUDA/library allocations or physical process-wide cap","inference/throughput/whole-process peaks","accepted estimator scope/error tolerance"],
            "initialization_trials":3,"accepted_estimator_pairs":0,"whole_process_peak_pairs":0,"observations":observations}

def publish(directory,archive):
    # Validate all records before publication; no failed/partial cohort is rewritten.
    originals={p:p.read_bytes() for p in [directory/f"init-r{r}.json" for r in (1,2,3)]}
    summarize(directory)
    if any("publication" in loads(raw.decode("utf-8")) for raw in originals.values()):
        raise ValueError("already published; preserve the original publication receipt")
    repo=Path(__file__).resolve().parents[1]
    if archive.exists() or archive.resolve().is_relative_to(repo): raise ValueError("fresh external archive directory required")
    archive.mkdir()
    for path,raw in originals.items():
        (archive/path.name).write_bytes(raw)
        record=loads(raw.decode("utf-8"))
        pattern=r"^llama_graph_n_input_tensors: input tensor .* is used by node .*"
        lines=record["stderr"].splitlines(keepends=True)
        retained=[line for line in lines if not re.fullmatch(pattern,line.rstrip("\n\r"))]
        record["publication"]={"omitted_diagnostic_pattern":pattern,"omitted_lines":len(lines)-len(retained),
            "original_sanitized_stderr_sha256":hashlib.sha256(record["stderr"].encode()).hexdigest(),
            "scope":"omit repetitive input-tensor graph diagnostics only; retain events, phase counters, placement, errors and warnings"}
        record["stderr"]="".join(retained)
        preflight=directory/record["preflight_file"]
        preflight.write_text(json.dumps(strict_json(preflight),indent=2)+"\n",encoding="utf-8",newline="\n")
        record["preflight_sha256"]=sha(preflight)
        path.write_text(json.dumps(record,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    summary=summarize(directory)
    (directory/"qualification-summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n")
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory",type=Path,default=DIRECTORY)
    p.add_argument("--publish-archive",type=Path)
    args=p.parse_args()
    result=publish(args.directory,args.publish_archive) if args.publish_archive else summarize(args.directory)
    print(json.dumps({"initialization_trials":result["initialization_trials"],"accepted_estimator_pairs":0,"exact_live_buffer_bytes":[o["exact_admitted_live_buffer_bytes"] for o in result["observations"]]}))

if __name__=="__main__":main()
