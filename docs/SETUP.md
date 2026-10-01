# Setup and compatibility

## Tested environment

| Component | Original verified version |
|---|---|
| GPU | GeForce RTX 5090, 32,607 MiB, compute capability 12.0 / SM120 |
| Windows GPU driver | 617.14 |
| Host | Windows 11, build 26200.9457 |
| WSL | 2.3.24.0, kernel 5.15.153.1-2 |
| Linux | Ubuntu 24.04 x86_64 |
| Python | 3.12.3 |
| CUDA runtime and NVRTC | 13.2.86 |
| TensorRT | 10.16.1.11, CUDA 13 packages |
| TensorRT Edge-LLM | 0.11.0 |
| live-vlm-webui | 0.4.0 |
| Model revision | `344d602b128d1bbdacb43b08d0a3626f46343e29` |

The driver reported CUDA capability 13.4; that is different from the installed
CUDA runtime. The native loader selected `x86-ubuntu2404-cu13-sm120`. Actual GPU
allocation/copy, engine building, endpoint inference, and webcam requests
worked on this machine. NVIDIA's x86 Linux support tier is development and
validation, not a guarantee for every WSL/driver combination.

Read the [upstream support matrix](https://nvidia.github.io/TensorRT-Edge-LLM/latest/user_guide/getting_started/support-matrix.html)
and [installation guidance](https://nvidia.github.io/TensorRT-Edge-LLM/latest/user_guide/getting_started/installation.html)
before changing versions. There is no fallback to a different backend.

## 1. Prepare Windows and WSL2

Install a Windows NVIDIA driver compatible with the required CUDA runtime.
Use Windows' NVIDIA driver for WSL GPU access; do not install JetPack or a
Linux display driver in this distro.

In an administrator PowerShell terminal, if Ubuntu 24.04 is not installed:

```powershell
wsl --install -d Ubuntu-24.04
```

Complete Ubuntu's first-run setup and any requested reboot. Verify:

```powershell
wsl --list --verbose
nvidia-smi
wsl -d Ubuntu-24.04 --exec /usr/lib/wsl/lib/nvidia-smi
```

The distro must run as WSL version 2. Choose an unused Ubuntu 24.04 distro for
this experiment. This project does not modify NVIDIA-Workbench or Docker's
WSL distributions. Allow at least 25 GiB free disk space for downloads,
environments, model files, and build caches; larger configurations need more.
The original installation occupied about 13 GiB inside Linux, excluding its
base Ubuntu filesystem. Free sufficient VRAM before the first engine build.

## 2. Clone and install inside Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/Derman0524/cosmos-webcam-demo.git
cd cosmos-webcam-demo
sudo bash scripts/linux/install.sh
```

The installer installs to `/opt/cosmos-demo`, uses separate backend and
frontend Python environments, verifies native GPU support, downloads the
pinned model, and prepares a reasoning-only checkpoint view. It does not
start the servers. The first server launch builds the engines.

The script refuses to overwrite an existing `/opt/cosmos-demo`. On the
original machine, use the existing installation and the launchers instead.
Do not delete a working installation just to rerun the setup instructions.

Hugging Face currently exposes this model without a token. If its access
requirements change, follow the provider's terms and authentication workflow;
do not embed credentials in these files. Package/model downloads remain
subject to availability and their upstream licenses.

## 3. Start the services

From PowerShell in your Windows checkout:

```powershell
& .\scripts\windows\Start-Cosmos-Webcam.ps1 -Distro Ubuntu-24.04
```

Alternatively, from Ubuntu:

```bash
sudo python3 /opt/cosmos-demo/manage_demo.py start
```

Both services bind to `127.0.0.1`. Open http://localhost:8090 in the Windows
browser and grant camera permission. Localhost is a browser secure context;
this HTTP configuration is for local use, not a public/LAN deployment.
The camera is accessed by the browser, so USB passthrough into WSL is not used.

The helper waits up to 15 minutes for the backend on a fresh build. If it times
out, inspect `/opt/cosmos-demo/backend.log` and check status before starting
another process. A timeout does not automatically terminate an in-progress
build or replace the backend. Repeat `start` after resolving the issue.

## 4. Stop and inspect

```powershell
& .\scripts\windows\Status-Cosmos-Webcam.ps1 -Distro Ubuntu-24.04
& .\scripts\windows\Stop-Cosmos-Webcam.ps1 -Distro Ubuntu-24.04
```

These scripts address only this demo's processes. They do not run a global
`wsl --shutdown` or unregister any distribution.

Useful files inside `/opt/cosmos-demo`:

- `backend.log`, `supervisor.log`, `webui.log`: diagnostics.
- `gpu-memory.csv`: whole-GPU readings for the latest backend run.
- `webcam-metrics.jsonl`: per-frame measurements, appended across sessions.
- `engines/`: device/version-specific cached engines.

If a port is occupied by another application, the helper stops with an error.
It will not terminate an unrelated process. Native loader errors usually
require checking the exact OS, GPU SM, CUDA and TensorRT combination.

## Validation scope

The source installation was exercised with a real webcam and successful
stop/restart cycles. Packaging checks cover syntax, launcher behavior,
privacy defaults, dependency consistency, and the preserved benchmark data.
A full clean install on a second computer has not been performed. Treat this
as a documented reproduction recipe, not a universal one-click installer.
