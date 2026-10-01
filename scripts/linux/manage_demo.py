import argparse
import fcntl
import json
import os
import signal
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path("/opt/cosmos-demo")
PORTS = {"backend": 8000, "webui": 8090}


def healthy(name):
    try:
        url = f"http://127.0.0.1:{PORTS[name]}/" + ("v1/models" if name == "backend" else "")
        with urllib.request.urlopen(url, timeout=2) as result:
            if result.status != 200:
                return False
            if name == "backend":
                return any(model.get("id") == "nvidia/Cosmos3-Edge" for model in json.load(result).get("data", []))
            return True
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def owned_pid(name):
    """Only recognize this demo's command, even if an old PID was reused."""
    path = ROOT / f"{name}.pid"
    try:
        pid = int(path.read_text())
        if pid <= 1:
            return None
        command = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        markers = [str(ROOT / "run_webui.py").encode()] if name == "webui" else [
            str(ROOT / "reasoner-model").encode(),
            str(ROOT / "venv/bin/tensorrt-edgellm-serve").encode(),
        ]
        return pid if all(marker in command for marker in markers) else None
    except (OSError, ValueError):
        return None


def port_in_use(port):
    with socket.socket() as connection:
        connection.settimeout(1)
        return connection.connect_ex(("127.0.0.1", port)) == 0


def status():
    return {"backend_ready": bool(owned_pid("backend") and healthy("backend")),
            "frontend_ready": bool(owned_pid("webui") and healthy("webui"))}


def start_service(name, timeout):
    child = None
    if not owned_pid(name):
        if port_in_use(PORTS[name]):
            raise RuntimeError(f"Port {PORTS[name]} is already in use by another service; it was left untouched.")
        command = ([str(ROOT / "venv/bin/python"), str(ROOT / "run_backend_monitored.py")]
                   if name == "backend" else ["bash", str(ROOT / "start_webui.sh")])
        log_path = ROOT / ("supervisor.log" if name == "backend" else "webui.log")
        with log_path.open("a") as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, start_new_session=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if owned_pid(name) and healthy(name):
            return
        if child is not None and child.poll() is not None:
            raise RuntimeError(f"{name} exited before becoming ready; inspect /opt/cosmos-demo/{name}.log.")
        time.sleep(1)
    raise RuntimeError(f"{name} did not become ready within {timeout}s. Inspect /opt/cosmos-demo/{name}.log. "
                       "Any in-progress build was left running; use stop to end it. No backend fallback was attempted.")


def stop_services():
    for name in ("webui", "backend"):
        pid = owned_pid(name)
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if not any(owned_pid(name) for name in PORTS):
            print("Demo processes stopped.")
            return
        time.sleep(0.5)
    raise RuntimeError("A demo process did not exit within 30s; inspect its log before retrying.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status"])
    args = parser.parse_args()
    if not ROOT.is_dir():
        parser.error("/opt/cosmos-demo does not exist; run the installer first.")
    if args.action == "status":
        print(json.dumps(status()))
        return 0
    with (ROOT / "manager.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            if args.action == "start":
                start_service("backend", 900)
                start_service("webui", 45)
                print("Open http://localhost:8090")
            else:
                stop_services()
        except (OSError, RuntimeError) as exc:
            print(json.dumps({"error": str(exc), **status()}))
            return 1
    print(json.dumps(status()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
