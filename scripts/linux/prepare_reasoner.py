from pathlib import Path

source = Path("/opt/cosmos-demo/model")
target = Path("/opt/cosmos-demo/reasoner-model")
target.mkdir(exist_ok=True)
for path in source.iterdir():
    if path.is_file():
        link = target / path.name
        if not link.exists():
            link.symlink_to(path)
for folder in ("transformer", "vision_encoder", "text_tokenizer"):
    (target / folder).mkdir(exist_ok=True)
    for path in (source / folder).iterdir():
        if folder == "transformer" and path.name == "config.json":
            continue
        link = target / folder / path.name
        if path.is_file() and not link.exists():
            link.symlink_to(path)
print("Reasoning-only checkpoint view:", target)
