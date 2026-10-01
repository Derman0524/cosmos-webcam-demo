from huggingface_hub import snapshot_download

path = snapshot_download(
    "nvidia/Cosmos3-Edge",
    revision="344d602b128d1bbdacb43b08d0a3626f46343e29",
    local_dir="/opt/cosmos-demo/model",
    allow_patterns=["*.json", "*.jinja", "transformer/*.safetensors", "vision_encoder/*.safetensors"],
    ignore_patterns=["assets/*", "vae/*", "scheduler/*", "images/*"],
    max_workers=3,
)
print(path)
