#!/usr/bin/env bash
set -euo pipefail
export XDG_CONFIG_HOME=/opt/cosmos-demo/config
export XDG_CACHE_HOME=/opt/cosmos-demo/cache
export PATH=/usr/lib/wsl/lib:$PATH
cd /opt/cosmos-demo
exec /opt/cosmos-demo/webui-venv/bin/python /opt/cosmos-demo/run_webui.py \
  --host 127.0.0.1 --port 8090 --no-ssl \
  --api-base http://127.0.0.1:8000/v1 \
  --model nvidia/Cosmos3-Edge --process-every 30 \
  --prompt "Identify the object being held up to the camera. Reply with only its common name. If no object is held up, reply: no object."
