import csv
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path("/opt/cosmos-demo")
with (root / "backend.log").open("w", buffering=1) as log, (root / "gpu-memory.csv").open("w", newline="", buffering=1) as stats:
    writer = csv.writer(stats)
    writer.writerow(["timestamp_utc", "gpu_used_mib", "gpu_total_mib", "gpu_utilization_pct"])
    proc = subprocess.Popen(["bash", str(root / "start_backend.sh")], stdout=log, stderr=subprocess.STDOUT)
    (root / "backend.pid").write_text(str(proc.pid))
    try:
        while proc.poll() is None:
            smi = subprocess.run(["/usr/lib/wsl/lib/nvidia-smi", "--id=0", "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
            if smi.returncode == 0:
                writer.writerow([datetime.now(timezone.utc).isoformat(), *smi.stdout.strip().split(", ")])
            time.sleep(1)
    except (KeyboardInterrupt, subprocess.TimeoutExpired):
        proc.terminate()
        proc.wait(timeout=20)
    print(f"Backend exited with status {proc.returncode}")
    raise SystemExit(proc.returncode)
