import argparse
import base64
import json
import mimetypes
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

PROMPT = "Identify the object being held up to the camera. Reply with only its common name. If no object is held up, reply: no object."
parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("--runs", type=int, default=10)
parser.add_argument("--output", default="/opt/cosmos-demo/api-benchmark.json")
args = parser.parse_args()
if args.runs < 1:
    parser.error("--runs must be positive")
mime = mimetypes.guess_type(args.image)[0]
if mime not in ("image/jpeg", "image/png", "image/webp"):
    parser.error("Use a JPEG, PNG, or WebP image")
raw = Path(args.image).read_bytes()
data_url = f"data:{mime};base64," + base64.b64encode(raw).decode()
body = {
    "model": "nvidia/Cosmos3-Edge", "max_tokens": 32,
    "temperature": 0, "enable_thinking": False, "stream": True,
    "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": data_url}},
        {"type": "text", "text": PROMPT}]}],
}
rows = []
with httpx.Client(timeout=180) as client:
    for index in range(args.runs):
        start = time.perf_counter()
        first = None
        output = ""
        with client.stream("POST", "http://127.0.0.1:8000/v1/chat/completions", json=body) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                if line == "data: [DONE]":
                    break
                event = json.loads(line[6:])
                if "error" in event:
                    raise RuntimeError(event["error"])
                for choice in event.get("choices", []):
                    text = choice.get("delta", {}).get("content") or ""
                    if text and first is None:
                        first = time.perf_counter()
                    output += text
        end = time.perf_counter()
        row = {"run": index, "warmup": index == 0,
               "ttft_ms": (first - start) * 1000 if first else None,
               "request_to_final_ms": (end - start) * 1000,
               "response": output}
        if not output:
            raise RuntimeError("No generated content")
        rows.append(row)
        print(json.dumps(row), flush=True)
result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "prompt": PROMPT,
          "image": str(Path(args.image)), "runs": rows,
          "measurement": "HTTP request start to first content token / final completion. Excludes webcam capture and browser rendering."}
Path(args.output).write_text(json.dumps(result, indent=2))
