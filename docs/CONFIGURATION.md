# Configuration and data handling

The deployed runtime lives in `/opt/cosmos-demo`. Edit the deployed scripts
only while both services are stopped. Changes in this Git checkout do not
automatically modify the existing WSL installation.

## Model and engine

`start_backend.sh` uses batch size 1, maximum input length 2,048, KV capacity
4,096, and 1,024 image tokens per image / total. The original engines used
FP16. These are demo limits, not the model's advertised maximum capabilities.
Changing engine profiles may trigger a rebuild and increase memory use.

`prepare_reasoner.py` creates a symlink view of the original checkpoint.
It preserves the original weights and index while omitting
`transformer/config.json` from the view so the experimental automatic builder
selects the text reasoner and visual encoder, not unused generation components.
It does not edit the downloaded checkpoint. This workaround is pinned to the
tested checkpoint and backend versions.

## Frontend

`start_webui.sh` uses the local OpenAI-compatible endpoint and a frame interval
of 30. The browser UI can change the prompt and sampling interval. Lower
intervals do more inference work; they do not guarantee a particular FPS.
WebRTC may adapt the captured resolution. A 4K webcam does not mean the model
receives every frame at 4K.

The custom timing wrapper replaces the frontend's image-analysis method to
measure streamed first-content-token timing. It retains the same backend.
It uses temperature 0 and disables thinking for the short-answer experiment.
This wrapper is written for live-vlm-webui 0.4.0; changing that dependency
requires rechecking its internal method and statistics contract.

The wrapper accepts the following environment variables. Set them in the
deployed `start_webui.sh` before its `exec` line, then restart:

| Variable | Default | Meaning |
|---|---|---|
| `COSMOS_MAX_TOKENS` | `32` | Actual output-token cap; overrides the frontend token control |
| `COSMOS_SAVE_FRAME` | `0` | Set to `1` to overwrite one `latest-webcam-frame.jpg` per request |
| `COSMOS_LOG_CONTENT` | `0` | Set to `1` to add prompts and answers to measurement records |

Numeric timing measurements are logged by default. Upstream frontend logs
may still contain prompt changes or diagnostics. Disabling these two opt-ins
does not guarantee every dependency's logs are free of sensitive content.
Review local logs before sharing. Never commit your runtime directory.

The historical installation used on 30 September saved the latest image and
logged text; this GitHub packaging changes the defaults for **fresh installs**.
It does not silently change the existing installation.

## Benchmark a still image

Inside WSL, with the backend running:

```bash
source /opt/cosmos-demo/env.sh
python /opt/cosmos-demo/benchmark_api.py /path/to/test-image.jpg --runs 10
```

This local tool records generated text and the input path in `api-benchmark.json`.
That file is ignored by Git. It measures repeated HTTP requests for one image;
it does not measure webcam capture or browser display. All runs are retained
and the first run is marked as warmup, not silently discarded.
