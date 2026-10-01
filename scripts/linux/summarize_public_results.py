"""Recompute the historical summary from public numeric data; no GPU required."""
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def distribution(values):
    values = sorted(values)
    return {"count": len(values), "median": statistics.median(values),
            "p95": values[math.ceil(len(values) * 0.95) - 1],
            "minimum": min(values), "maximum": max(values)}


def summarize(directory):
    with (directory / "frame-timings.csv").open(newline="") as handle:
        frames = list(csv.DictReader(handle))
    with (directory / "gpu-memory-timings.csv").open(newline="") as handle:
        gpu = list(csv.DictReader(handle))
    object_frames = [row for row in frames if row["object_prompt"] == "1"]
    result = {}
    for name, rows in [("object_prompt", object_frames), ("all_mixed_prompts", frames)]:
        result[name] = {key: distribution([float(row[key]) for row in rows]) for key in
                        ("ttft_ms", "request_to_final_ms", "frame_preprocess_to_final_ms")}
    result["live_total_gpu_memory_mib"] = distribution(
        [int(row["gpu_used_mib"]) for row in gpu if row["during_webcam"] == "1"])
    result["all_recorded_gpu_peak_mib"] = max(int(row["gpu_used_mib"]) for row in gpu)
    result["samples"] = len(frames)
    result["object_prompt_samples"] = len(object_frames)
    return result


if __name__ == "__main__":
    directory = ROOT / "results/2026-09-30"
    actual = summarize(directory)
    expected = json.loads((directory / "summary.json").read_text())
    expected.pop("measurement_note")
    if actual != expected:
        raise SystemExit("Public numeric data does not match the preserved summary.")
    print(json.dumps(actual, indent=2))
    print("Public numeric data exactly reproduces the preserved summary.")
