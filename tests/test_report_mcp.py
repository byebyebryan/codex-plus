import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from codex_plus.reports.mcp import Server, definitions


class ReportMCPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.store = self.root / "store"
        self.server = Server(self.root / "missing.toml", self.store)

    def call(self, name, arguments=None):
        return self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                  "params": {"name": name, "arguments": arguments or {}}})["result"]

    def test_discovery_needs_neither_configuration_state_nor_native_context(self):
        with patch("subprocess.run", side_effect=AssertionError("unexpected native command")):
            for method in ("initialize", "tools/list"):
                response = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": method})
                self.assertIn("result", response)
            self.assertEqual(self.call("report_list")["structuredContent"]["reports"], [])
        self.assertFalse(self.store.exists())
        tools = {t["name"]: t for t in definitions()}
        self.assertTrue(tools["report_list"]["annotations"]["readOnlyHint"])
        self.assertTrue(tools["report_delete"]["annotations"]["destructiveHint"])
        self.assertFalse(tools["report_publish"]["annotations"]["idempotentHint"])

    def test_provider_neutral_publish_and_delete_have_structured_truthful_receipts(self):
        source = self.root / "report.html"; source.write_text("<h1>Result</h1>")
        with patch("subprocess.run", side_effect=AssertionError("unexpected native command")):
            response = self.call("report_publish", {"source": str(source), "title": "Result"})
            self.assertFalse(response["isError"])
            value = response["structuredContent"]
            self.assertEqual(value["publication"], "created")
            self.assertIsNone(value["url"])
            self.assertEqual(value["delivery"]["state"], "unavailable")
            removed = self.call("report_delete", {"report_id": value["report_id"]})
        self.assertEqual(removed["structuredContent"]["state"], "deleted")
        self.assertTrue(source.is_file())

    def test_invalid_arguments_do_not_create_state(self):
        for name, arguments in (("report_list", {"limit": True}), ("report_list", {"limit": 201}),
                                ("report_get", {"report_id": "../x"}), ("report_publish", {"source": "/x"}),
                                ("report_list", {"caller": "spoof"}), ("unknown", {})):
            self.assertTrue(self.call(name, arguments)["isError"])
        self.assertFalse(self.store.exists())

    def test_cli_stdio_is_protocol_clean_and_keeps_working_without_codex_on_path(self):
        script = Path(__file__).resolve().parents[1] / "scripts/codex-plus-report-mcp"
        requests = [json.dumps({"jsonrpc": "2.0", "id": i, "method": method}) for i, method in enumerate(("initialize", "tools/list"), 1)]
        response = subprocess.run([sys.executable, "-B", str(script), "--data-root", str(self.store)],
                                  input="\n".join(requests) + "\n", text=True, capture_output=True,
                                  env={"PATH": "/unavailable", "PYTHONDONTWRITEBYTECODE": "1"},
                                  cwd=self.root, timeout=5, check=True)
        decoded = [json.loads(line) for line in response.stdout.splitlines()]
        self.assertEqual(len(decoded), 2)
        self.assertEqual(decoded[0]["result"]["serverInfo"]["name"], "html-report")
        self.assertEqual(response.stderr, "")
        self.assertFalse(self.store.exists())

    def test_oversized_request_is_drained_and_next_request_survives(self):
        output = io.StringIO()
        self.server.serve(io.StringIO("x" * (256 * 1024 + 1) + "\n" + json.dumps(
            {"jsonrpc": "2.0", "id": 2, "method": "ping"}) + "\n"), output)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertIn("error", responses[0]); self.assertEqual(responses[1]["id"], 2)


if __name__ == "__main__": unittest.main()
