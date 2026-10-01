export COSMOS_DEMO_ROOT=/opt/cosmos-demo
export PATH=/opt/cosmos-demo/venv/bin:/usr/lib/wsl/lib:$PATH
export LD_LIBRARY_PATH=/opt/cosmos-demo/venv/lib/python3.12/site-packages/nvidia/cu13/lib:/opt/cosmos-demo/venv/lib/python3.12/site-packages/tensorrt_libs:/usr/lib/wsl/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export HF_HOME=/opt/cosmos-demo/huggingface
export XDG_CACHE_HOME=/opt/cosmos-demo/cache
export CUDA_VISIBLE_DEVICES=0
