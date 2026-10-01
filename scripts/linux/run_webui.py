"""Run NVIDIA live-vlm-webui with streaming timing for the local Edge-LLM API."""
import base64
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import os

from live_vlm_webui.vlm_service import VLMService, logger

root = Path("/opt/cosmos-demo")
(root / "webui.pid").write_text(str(os.getpid()))
max_tokens = int(os.environ.get("COSMOS_MAX_TOKENS", "32"))
if max_tokens < 1:
    raise ValueError("COSMOS_MAX_TOKENS must be positive")
save_frame = os.environ.get("COSMOS_SAVE_FRAME", "0") == "1"
log_content = os.environ.get("COSMOS_LOG_CONTENT", "0") == "1"


async def measured_analyze_image(self, image, prompt=None):
    start = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    jpeg = buffer.getvalue()
    if save_frame:
        (root / "latest-webcam-frame.jpg").write_bytes(jpeg)
    data_url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt or self.prompt},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}]
    request_start = time.perf_counter()
    first = None
    chunks = []
    try:
        stream = await self.client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=max_tokens,
            temperature=0, stream=True, extra_body={"enable_thinking": False},
        )
        async for event in stream:
            for choice in event.choices:
                content = choice.delta.content or ""
                if content and first is None:
                    first = time.perf_counter()
                chunks.append(content)
        end = time.perf_counter()
        result = "".join(chunks).strip()
        if not result:
            raise RuntimeError("The endpoint returned no text")
        self.last_inference_time = end - start
        self.total_inferences += 1
        self.total_inference_time += self.last_inference_time
        row = {
            "timestamp_utc": timestamp, "sample": self.total_inferences,
            "width": image.width, "height": image.height,
            "ttft_ms": (first - request_start) * 1000,
            "request_to_final_ms": (end - request_start) * 1000,
            "frame_preprocess_to_final_ms": (end - start) * 1000,
            "max_tokens": max_tokens, "temperature": 0,
        }
        if log_content:
            row.update(response=result, prompt=prompt or self.prompt)
        with (root / "webcam-metrics.jsonl").open("a") as handle:
            handle.write(json.dumps(row) + "\n")
        logger.info("COSMOS_METRIC %s", json.dumps(row))
        return result
    except Exception as exc:
        logger.exception("Local Cosmos webcam inference failed")
        return f"Error: {exc}"


VLMService.analyze_image = measured_analyze_image
from live_vlm_webui.server import main

main()
