"""Read-only Windows spare-capacity screen for the dated supplemental MoE protocol."""

import argparse
import ctypes
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temporary-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", choices=("granite30", "granite31"), default="granite30")
    args = parser.parse_args()
    disk_threshold = 12 * 2**30 if args.profile == "granite30" else 2 * 2_669_283_096 + 2**30
    result = {"classification": "read-only capacity screen; not inference or a fit guarantee",
              "profile": args.profile,
              "observed_utc": datetime.now(timezone.utc).isoformat(),
              "thresholds": {"nvidia_smi_free_mib": 4096, "available_host_ram_bytes": 12 * 2**30,
                             "temporary_volume_free_bytes": disk_threshold},
              "methods": ["nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits",
                          "Windows kernel32 GlobalMemoryStatusEx.ullAvailPhys",
                          "Python shutil.disk_usage(temporary_dir).free"]}
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    try:
        smi = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             check=True, text=True, capture_output=True, timeout=30)
        if len(smi.stdout.strip().splitlines()) != 1:
            raise ValueError("one visible GPU required")
        memory = MemoryStatus()
        memory.dwLength = ctypes.sizeof(memory)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
            raise OSError("GlobalMemoryStatusEx failed")
        result["observed"] = {"nvidia_smi_free_mib": int(smi.stdout.strip()),
                              "available_host_ram_bytes": memory.ullAvailPhys,
                              "temporary_volume_free_bytes": shutil.disk_usage(args.temporary_dir).free}
        result["guards"] = {key: value >= result["thresholds"][key] for key, value in result["observed"].items()}
        result["status"] = "admitted_to_download_screen_only" if all(result["guards"].values()) else "unexecuted"
        result["reason"] = "all screens satisfied; recheck before inference" if all(result["guards"].values()) else "one or more spare-capacity guards failed; no weights downloaded or other process changed"
    except Exception as error:
        result["status"] = "unexecuted"
        result["reason"] = type(error).__name__ + ": " + str(error)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
