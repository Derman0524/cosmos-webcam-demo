#!/usr/bin/env bash
set -euo pipefail
source /opt/cosmos-demo/env.sh
cd /opt/cosmos-demo
exec tensorrt-edgellm-serve /opt/cosmos-demo/reasoner-model \
  --served-model-name nvidia/Cosmos3-Edge \
  --host 127.0.0.1 --port 8000 \
  --cache-dir /opt/cosmos-demo/engines \
  --engine-cache-max-size-gb 12 \
  --max-input-len 2048 --max-kv-cache-capacity 4096 \
  --max-batch-size 1 \
  --max-image-tokens 1024 --max-image-tokens-per-image 1024
