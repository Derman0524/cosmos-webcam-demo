#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
demo_dir=/opt/cosmos-demo
[[ $EUID -eq 0 ]] || { echo 'Run with sudo bash scripts/linux/install.sh'; exit 1; }
source /etc/os-release
[[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 24.04 && $(uname -m) == x86_64 ]] || {
  echo 'This recipe targets Ubuntu 24.04 x86_64 only; no backend fallback.'; exit 1;
}
[[ ! -e "$demo_dir" ]] || {
  echo "$demo_dir already exists. Use its launchers; this installer will not overwrite it."; exit 1;
}
export PATH="/usr/lib/wsl/lib:$PATH"
nvidia-smi -i 0 --query-gpu=name,driver_version,compute_cap,memory.total --format=csv
sm="$(nvidia-smi -i 0 --query-gpu=compute_cap --format=csv,noheader | tr -d '[:space:]')"
[[ "$sm" == 12.0 ]] || { echo 'This recipe is validated for SM120. Stop and check the support matrix.'; exit 1; }
apt-get update
apt-get install -y python3.12-venv libgl1 libglib2.0-0 ca-certificates
install -d "$demo_dir"
cp "$repo_dir"/scripts/linux/*.py "$repo_dir"/scripts/linux/*.sh "$demo_dir/"
install -d "$demo_dir/requirements"
cp "$repo_dir"/requirements/*.txt "$demo_dir/requirements/"
python3.12 -m venv "$demo_dir/venv"
python3.12 -m venv "$demo_dir/webui-venv"
"$demo_dir/venv/bin/python" -m pip install -r "$demo_dir/requirements/backend.lock.txt"
"$demo_dir/webui-venv/bin/python" -m pip install -r "$demo_dir/requirements/frontend.lock.txt"
source "$demo_dir/env.sh"
"$demo_dir/venv/bin/python" -m pip check
"$demo_dir/webui-venv/bin/python" -m pip check
"$demo_dir/venv/bin/python" "$demo_dir/verify_runtime.py"
"$demo_dir/venv/bin/python" "$demo_dir/download_cosmos.py"
"$demo_dir/venv/bin/python" "$demo_dir/prepare_reasoner.py"
echo 'Installed. First start builds cached engines: python3 /opt/cosmos-demo/manage_demo.py start'
