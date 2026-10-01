"""Run with python3 -m unittest discover -s tests -v inside Linux/WSL."""
import asyncio
import importlib.util
import json
import os
import socket
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts/linux" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


manager = load_script("manage_demo")
summary = load_script("summarize_public_results")


class LifecycleTests(unittest.TestCase):
    def test_reused_pid_does_not_stop_an_unrelated_process(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(manager, "ROOT", Path(directory)):
            for name in manager.PORTS:
                (Path(directory) / f"{name}.pid").write_text(str(os.getpid()))
                self.assertIsNone(manager.owned_pid(name))
            with mock.patch.object(manager.os, "kill") as kill:
                manager.stop_services()
            kill.assert_not_called()

    def test_occupied_port_is_not_replaced(self):
        with socket.socket() as server, tempfile.TemporaryDirectory() as directory:
            server.bind(("127.0.0.1", 0))
            server.listen()
            with mock.patch.object(manager, "ROOT", Path(directory)), \
                    mock.patch.dict(manager.PORTS, backend=server.getsockname()[1]), \
                    mock.patch.object(manager.subprocess, "Popen") as launch:
                with self.assertRaisesRegex(RuntimeError, "already in use"):
                    manager.start_service("backend", 1)
                launch.assert_not_called()

    def test_frontend_failure_returns_failure_without_success_message(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(manager, "ROOT", Path(directory)), \
                mock.patch.object(sys, "argv", ["manage_demo.py", "start"]), \
                mock.patch.object(manager, "start_service", side_effect=[None, RuntimeError("frontend failed")]), \
                mock.patch("builtins.print") as output:
            self.assertEqual(manager.main(), 1)
            self.assertFalse(any("Open http" in str(call) for call in output.call_args_list))


class FakeImage:
    width, height = 640, 360

    def save(self, handle, format):
        handle.write(b"test-image-bytes")


async def response_stream(text):
    yield types.SimpleNamespace(choices=[types.SimpleNamespace(delta=types.SimpleNamespace(content=text))])


class PrivacyTests(unittest.TestCase):
    def run_request(self, directory, env, text="private scene description"):
        service_module = types.ModuleType("live_vlm_webui.vlm_service")
        service_module.VLMService = type("VLMService", (), {})
        service_module.logger = mock.Mock()
        server_module = types.ModuleType("live_vlm_webui.server")
        server_module.main = mock.Mock()
        modules = {"live_vlm_webui": types.ModuleType("live_vlm_webui"),
                   "live_vlm_webui.vlm_service": service_module,
                   "live_vlm_webui.server": server_module}
        with mock.patch.dict(sys.modules, modules), mock.patch.dict(os.environ, env, clear=True), \
                mock.patch("pathlib.Path", return_value=Path(directory)):
            wrapper = load_script("run_webui")
        create = mock.AsyncMock(return_value=response_stream(text))
        service = types.SimpleNamespace(prompt="private request", model="nvidia/Cosmos3-Edge",
                    total_inferences=0, total_inference_time=0,
                    client=types.SimpleNamespace(chat=types.SimpleNamespace(
                        completions=types.SimpleNamespace(create=create))))
        result = asyncio.run(wrapper.measured_analyze_image(service, FakeImage()))
        return result, create, service_module.logger

    def test_default_inference_keeps_content_out_of_metrics_and_saves_no_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            result, create, logger = self.run_request(directory, {})
            self.assertEqual(result, "private scene description")
            metrics = (Path(directory) / "webcam-metrics.jsonl").read_text()
            row = json.loads(metrics)
            self.assertEqual(row["sample"], 1)
            self.assertGreaterEqual(row["request_to_final_ms"], row["ttft_ms"])
            self.assertNotIn("private", metrics)
            self.assertNotIn("private", str(logger.info.call_args))
            self.assertFalse((Path(directory) / "latest-webcam-frame.jpg").exists())
            self.assertEqual(create.call_args.kwargs["max_tokens"], 32)
            self.assertEqual(create.call_args.kwargs["extra_body"], {"enable_thinking": False})

    def test_content_and_frame_capture_require_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            _, create, _ = self.run_request(directory, {
                "COSMOS_SAVE_FRAME": "1", "COSMOS_LOG_CONTENT": "1", "COSMOS_MAX_TOKENS": "16"})
            row = json.loads((Path(directory) / "webcam-metrics.jsonl").read_text())
            self.assertEqual(row["response"], "private scene description")
            self.assertEqual(row["prompt"], "private request")
            self.assertTrue((Path(directory) / "latest-webcam-frame.jpg").exists())
            self.assertEqual(create.call_args.kwargs["max_tokens"], 16)

    def test_empty_completion_is_not_recorded_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            result, _, _ = self.run_request(directory, {}, text="")
            self.assertTrue(result.startswith("Error:"))
            self.assertFalse((Path(directory) / "webcam-metrics.jsonl").exists())


class PublicDataTests(unittest.TestCase):
    def test_export_reproduces_original_summary(self):
        directory = REPO / "results/2026-09-30"
        expected = json.loads((directory / "summary.json").read_text())
        expected.pop("measurement_note")
        self.assertEqual(summary.summarize(directory), expected)


if __name__ == "__main__":
    unittest.main()
