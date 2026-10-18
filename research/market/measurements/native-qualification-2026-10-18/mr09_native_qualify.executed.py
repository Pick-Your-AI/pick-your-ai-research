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

MODEL = "SmolLM2-135M-Instruct-f16.gguf"
MODEL_SHA = "f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57"
DIRECTORY = Path("research/market/measurements/native-qualification-2026-10-18")

def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024**2),b""): h.update(b)
    return h.hexdigest()

def write(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")

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
    if checksum(exe)!=build["executables"]["native-init.exe"]: parser.error("native executable hash mismatch")
    if model.stat().st_size!=270885952 or checksum(model)!=MODEL_SHA: parser.error("model size/hash mismatch")
    manifest=json.loads((DIRECTORY/"runtime-artifacts.json").read_text())
    for item in manifest["files"]:
        if checksum(runtime/item["file"])!=item["sha256"]: parser.error("runtime artifact drift: "+item["file"])
    subprocess.run([sys.executable,"scripts/mr09_preflight.py","--profile","granite31","--temporary-dir",str(args.temporary_dir),"--output",str(preflight)],check=True,capture_output=True,text=True)
    screen=json.loads(preflight.read_text())
    if not all(screen["guards"].values()): raise RuntimeError("fresh spare-capacity guard failed; no launch")
    started=datetime.now(timezone.utc).isoformat()
    argv=[str(exe),str(runtime),"2136809472",str(model)]
    try:
        result=subprocess.run(argv,cwd=runtime,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=90)
        code,stdout,stderr=result.returncode,result.stdout,result.stderr
    except subprocess.TimeoutExpired as error:
        code=-1
        stdout=error.stdout or ""
        stderr=error.stderr or ""
        if isinstance(stdout,bytes): stdout=stdout.decode("utf-8",errors="replace")
        if isinstance(stderr,bytes): stderr=stderr.decode("utf-8",errors="replace")
        stderr+="\nQualification timed out; child killed; stop without retry."
    def sanitized(value):
        for path,label in ((model,"$GGUF_FILE"),(runtime,"$RUNTIME_DIR"),(args.temporary_dir,"$TASK_TEMP"),(Path.home(),"$USER_HOME")):
            value=value.replace(str(path),label).replace(str(path).replace("\\","/"),label)
        return value
    record={"classification":"real native initialization qualification, not accepted estimator calibration or process-wide peak", "repetition":args.repetition,
            "started_utc":started,"finished_utc":datetime.now(timezone.utc).isoformat(),"exit_code":code,
            "argv":["$NATIVE_INIT","$RUNTIME_DIR","2136809472","$GGUF_FILE"],"harness_sha256":checksum(exe),
            "harness_git_ref":build["harness_git_ref"],"launcher_sha256":checksum(Path(__file__)),
            "model_sha256":MODEL_SHA,"runtime_artifact_ledger_sha256":checksum(DIRECTORY/"runtime-artifacts.json"),
            "preflight_file":preflight.name,"preflight_sha256":checksum(preflight),
            "driver_csv":subprocess.check_output(["nvidia-smi","--query-gpu=name,driver_version,memory.total,memory.free","--format=csv"],text=True).strip(),
            "stdout":sanitized(stdout),"stderr":sanitized(stderr),"generation_forwards":0,"warmup":False,
            "status":"native_initialization_completed" if code==0 else "qualification_failure"}
    write(output,record)
    print(json.dumps({"file":str(output),"exit_code":code,"status":record["status"]}))
    return 0 if code==0 else 1

if __name__ == "__main__": raise SystemExit(main())
