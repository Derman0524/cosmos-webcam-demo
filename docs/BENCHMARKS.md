# Benchmark method and limitations

The published summary is from the original 30 September 2026 interactive
webcam run. It is preserved separately from any later test of the repository.

## Timing boundaries

- **TTFT:** from immediately before the OpenAI-compatible HTTP request to
  receipt of the first nonempty content token.
- **Request to final:** same start to completion of the response stream.
- **Frame preprocessing to final:** from before JPEG encoding through stream
  completion, including encoding and API work.

None includes camera exposure, sampling wait, WebRTC transport into the
frontend, or browser rendering. True camera-to-screen latency was not measured.

The object prompt group contains 20 frames. The mixed-prompt group contains
all 183 frames, **including** those 20. They are not independent datasets.
All samples, including startup/warmup behavior, are retained. p95 uses the
nearest-rank method. Inputs adapted between 640x360, 480x270, and 320x180.
Output length and prompts varied in the mixed session. Temperature was 0,
thinking was disabled, and output was capped at 32 tokens.

The original frame interval was 30. During much of the session, requests
arrived roughly two seconds apart. Low model response latency does not imply
that the demo analyzed every camera frame.

## GPU memory

The NVIDIA-SMI recorder sampled the entire GPU once per second. The 383 samples
between the first and last recorded webcam requests have a median of 8,112 MiB
and p95 of 8,211 MiB. The recorded build/startup peak was 19,198 MiB.
Windows and other applications are included. The pre-run baseline changed,
so subtracting it is invalid. Model-only memory is not established.

## Accuracy

The model returned plausible labels such as cup, glass, headphones, and
no object. It sometimes identified worn headphones despite the instruction
to name the held object. No labeled accuracy study was performed. These
results establish a functioning local pipeline, not reliable inspection,
counting, metrology, or safety-critical decision-making.

## Public data

`frame-timings.csv` retains numeric timing, frame dimensions, sample index,
elapsed time from the first frame, and group membership. It excludes raw
timestamps, prompts, scene descriptions, and images. Group membership was
reconstructed in the original analysis from the contemporaneous prompt log.

`gpu-memory-timings.csv` retains elapsed time from the first GPU sample,
memory, utilization, and whether each reading falls within the webcam window.
Invalid rows were excluded and original null padding was removed before this
export; the preserved summary uses the same cleaned data.

Run `python3 scripts/linux/summarize_public_results.py` from this repository to
verify that both numeric exports reproduce `results/2026-09-30/summary.json`.
The historical prompts, responses, raw logs, and webcam images stay local.
