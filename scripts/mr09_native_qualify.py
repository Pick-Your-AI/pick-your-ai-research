"""Run one pinned, guarded native initialization qualification in a fresh process.

No decoder, warmup, token-generation or generic GPU-command interface exists.
Historical setup execution stays disabled; qualification is a separate record.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from mr09_native_capture import driver_readback

MODEL = "SmolLM2-135M-Instruct-f16.gguf"
MODEL_SHA = "f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57"
DIRECTORY = Path("research/market/measurements/native-qualification-2026-10-18")
DRIVER_QUERY_TIMEOUT_SECONDS = 10

def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024**2),b""): h.update(b)
    return h.hexdigest()

def write(path,value):
    # A failed later update must not truncate the already retained child result.
    serialized=json.dumps(value,indent=2,allow_nan=False)+"\n"
    descriptor,temporary=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(descriptor,"w",encoding="utf-8",newline="\n") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        Path(temporary).unlink(missing_ok=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temporary-dir",type=Path,required=True)
    parser.add_argument("--repetition",type=int,choices=(1,2,3),required=True)
    args=parser.parse_args()
    output=DIRECTORY/f"init-r{args.repetition}.json"
    preflight=DIRECTORY/f"init-r{args.repetition}-preflight.json"
    if output.exists() or preflight.exists(): parser.error("preserve observations; existing repetition cannot be overwritten")
    build=json.loads((DIRECTORY/"build-loader-v2.json").read_text())
    exe=args.temporary_dir/"native-init.exe"
    runtime=args.temporary_dir/"runtime"
    model=args.temporary_dir/MODEL
    harness_sha=checksum(exe)
    if harness_sha!=build["executables"]["native-init.exe"]: parser.error("native executable hash mismatch")
    if model.stat().st_size!=270885952 or checksum(model)!=MODEL_SHA: parser.error("model size/hash mismatch")
    manifest=json.loads((DIRECTORY/"runtime-artifacts.json").read_text())
    for item in manifest["files"]:
        if checksum(runtime/item["file"])!=item["sha256"]: parser.error("runtime artifact drift: "+item["file"])
    subprocess.run([sys.executable,"scripts/mr09_preflight.py","--profile","granite31","--temporary-dir",str(args.temporary_dir),"--output",str(preflight)],check=True,capture_output=True,text=True)
    screen=json.loads(preflight.read_text())
    if not all(screen["guards"].values()): raise RuntimeError("fresh spare-capacity guard failed; no launch")
    # Freeze the admitted identities before execution, so later file/telemetry
    # errors cannot prevent retention of a completed or timed-out child.
    identities={"harness_sha256":harness_sha,"harness_git_ref":build["harness_git_ref"],
                "launcher_sha256":checksum(Path(__file__)),"model_sha256":MODEL_SHA,
                "runtime_artifact_ledger_sha256":checksum(DIRECTORY/"runtime-artifacts.json"),
                "preflight_file":preflight.name,"preflight_sha256":checksum(preflight)}
    started=datetime.now(timezone.utc).isoformat()
    argv=[str(exe),str(runtime),"2136809472",str(model)]
    timed_out=False
    try:
        result=subprocess.run(argv,cwd=runtime,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=90)
        code,stdout,stderr=result.returncode,result.stdout,result.stderr
    except subprocess.TimeoutExpired as error:
        timed_out=True
        code=-1
        stdout=error.stdout or ""
        stderr=error.stderr or ""
        if isinstance(stdout,bytes): stdout=stdout.decode("utf-8",errors="replace")
        if isinstance(stderr,bytes): stderr=stderr.decode("utf-8",errors="replace")
        stderr+="\nQualification timed out; child killed; stop without retry."
    finished=datetime.now(timezone.utc).isoformat()
    def sanitized(value):
        for path,label in ((model,"$GGUF_FILE"),(runtime,"$RUNTIME_DIR"),(args.temporary_dir,"$TASK_TEMP"),(Path.home(),"$USER_HOME")):
            value=value.replace(str(path),label).replace(str(path).replace("\\","/"),label)
        return value
    record={"classification":"real native initialization qualification, not accepted estimator calibration or process-wide peak", "repetition":args.repetition,
            "started_utc":started,"finished_utc":finished,"exit_code":code,
            "argv":["$NATIVE_INIT","$RUNTIME_DIR","2136809472","$GGUF_FILE"],**identities,
            "native_status":"timed_out" if timed_out else ("completed" if code==0 else "failed"),
            "driver_csv":None,"driver_readback":{"status":"pending","timeout_seconds":DRIVER_QUERY_TIMEOUT_SECONDS},
            "stdout":sanitized(stdout),"stderr":sanitized(stderr),"generation_forwards":0,"warmup":False,
            "status":"post_run_telemetry_pending" if code==0 else "qualification_failure"}
    # Retain the child outcome before optional post-run telemetry. Pending or
    # failed telemetry never has the capture validator's successful status.
    write(output,record)
    def telemetry_text(value):
        if isinstance(value,bytes): value=value.decode("utf-8",errors="replace")
        return sanitized(value or "")
    try:
        raw_driver=subprocess.check_output(
            ["nvidia-smi","--query-gpu=name,driver_version,memory.total,memory.free","--format=csv"],
            text=True,encoding="utf-8",errors="replace",stderr=subprocess.PIPE,timeout=DRIVER_QUERY_TIMEOUT_SECONDS)
        record["driver_csv"]=sanitized(raw_driver.strip())
        driver_readback(record["driver_csv"])
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError,ValueError) as error:
        record["driver_readback"]={"status":"failed","timeout_seconds":DRIVER_QUERY_TIMEOUT_SECONDS,
            "error_type":type(error).__name__,"error":sanitized(str(error)),
            "stdout":telemetry_text(getattr(error,"stdout",None)),
            "stderr":telemetry_text(getattr(error,"stderr",None))}
        if isinstance(error,subprocess.CalledProcessError): record["driver_readback"]["exit_code"]=error.returncode
        record["status"]="qualification_failure"
    else:
        record["driver_readback"]={"status":"completed","timeout_seconds":DRIVER_QUERY_TIMEOUT_SECONDS}
        record["status"]="native_initialization_completed" if code==0 else "qualification_failure"
    write(output,record)
    print(json.dumps({"file":str(output),"exit_code":code,"status":record["status"]}))
    return 0 if record["status"]=="native_initialization_completed" else 1

if __name__ == "__main__": raise SystemExit(main())
