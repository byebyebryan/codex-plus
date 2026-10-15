#!/usr/bin/env python3
"""Focused checks for the Codex notification helper, without desktop side effects."""

import base64
import fcntl
import json
import os
from pathlib import Path
import pty
import runpy
import select
import sqlite3
import subprocess
import sys
import tempfile
import termios
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / "scripts/codex-notify"
HELPER_GLOBALS = runpy.run_path(str(HELPER))
NOTIFY = HELPER_GLOBALS["notification"]
IS_SUBAGENT = HELPER_GLOBALS["is_subagent"]
TERMINAL = HELPER_GLOBALS["terminal"]

ROOT_THREAD = "11111111-1111-4111-8111-111111111111"
CHILD_THREAD = "22222222-2222-4222-8222-222222222222"


class Notifications(unittest.TestCase):
    def setUp(self):
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        self.codex_home = Path(home.name)
        environment = patch.dict(os.environ, {"CODEX_HOME": home.name})
        environment.start()
        self.addCleanup(environment.stop)

    def state_database(self, rows, version=5):
        path = self.codex_home / f"state_{version}.sqlite"
        database = sqlite3.connect(path)
        try:
            database.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, source TEXT)")
            database.executemany("INSERT INTO threads VALUES (?, ?)", rows)
            database.commit()
        finally:
            database.close()
        return path

    def payload(self, body="We've / we’ve checked 東京 → ✓."):
        return {"type": "agent-turn-complete", "client": "codex_tui",
                "last-assistant-message": body}

    def decode_kitty(self, packet):
        sequences = packet.decode().split("\x07")
        metadata, title = sequences[0].split(";", 2)[1:]
        body_metadata, encoded = sequences[1].split(";", 2)[1:]
        self.assertIn("o=unfocused", metadata)
        self.assertNotIn("f=", metadata)
        self.assertEqual(metadata.split(":", 1)[0], body_metadata.split(":", 1)[0])
        self.assertIn("p=body", body_metadata)
        return title, base64.b64decode(encoded).decode("utf-8")

    def test_kitty_title_and_body(self):
        payload = self.payload()
        title, body = self.decode_kitty(NOTIFY(payload))
        self.assertEqual(title, "Codex")
        self.assertEqual(body, payload["last-assistant-message"])

    def test_kitty_preserves_paragraphs_and_compacts_line_whitespace(self):
        title, body = self.decode_kitty(
            NOTIFY(self.payload("  First   paragraph.\n\tSecond   line.\n\nThird.  "))
        )
        self.assertEqual(title, "Codex")
        self.assertEqual(body, "First paragraph.\nSecond line.\n\nThird.")

    def test_untrusted_controls_and_utf8_limit(self):
        payload = self.payload("we've\n\x1b]9;injected\x07\x9c " + "東京" * 1000)
        _, body = self.decode_kitty(NOTIFY(payload))
        self.assertLessEqual(len(body.encode()), 2048)
        self.assertFalse(any(c != "\n" and (ord(c) < 32 or 127 <= ord(c) < 160) for c in body))
        self.assertIn("we've", body)

    def test_unsupported_and_background_events(self):
        for payload in (None, [], {"type": "approval-requested"},
                        {**self.payload(), "client": "codex_exec"},
                        {**self.payload(), "last-assistant-message": None}):
            self.assertIsNone(NOTIFY(payload))

    def test_subagent_identity_uses_read_only_state(self):
        source = json.dumps({"subagent": {"thread_spawn": {
            "parent_thread_id": ROOT_THREAD, "agent_path": "/root/worker"}}})
        path = self.state_database([(ROOT_THREAD, "cli"), (CHILD_THREAD, source)])
        before = path.read_bytes()
        self.assertFalse(IS_SUBAGENT(ROOT_THREAD))
        self.assertTrue(IS_SUBAGENT(CHILD_THREAD))
        self.assertFalse(IS_SUBAGENT("unknown-thread"))
        self.assertEqual(path.read_bytes(), before)

    def test_newest_state_schema_takes_precedence(self):
        self.state_database([(CHILD_THREAD, "cli")], version=4)
        self.state_database([(CHILD_THREAD, json.dumps({"subagent": "review"}))], version=5)
        self.assertTrue(IS_SUBAGENT(CHILD_THREAD))

    def test_missing_or_unusable_state_does_not_suppress_completion(self):
        for thread_id in (None, [], "", ROOT_THREAD):
            self.assertFalse(IS_SUBAGENT(thread_id))
        self.assertEqual(list(self.codex_home.iterdir()), [])
        path = self.codex_home / "state_5.sqlite"
        path.write_bytes(b"not a database")
        self.assertFalse(IS_SUBAGENT(ROOT_THREAD))
        path.unlink()
        self.state_database([(ROOT_THREAD, "malformed source")])
        self.assertFalse(IS_SUBAGENT(ROOT_THREAD))

    def run_on_controlling_tty(self, argument, term="xterm-kitty"):
        master, slave = pty.openpty()
        environment = os.environ.copy()
        for key in ("TMUX", "TMUX_PANE", "KITTY_WINDOW_ID"):
            environment.pop(key, None)
        environment["TERM"] = term

        def attach_tty():
            os.setsid()
            fcntl.ioctl(slave, termios.TIOCSCTTY, 0)

        try:
            process = subprocess.run([sys.executable, str(HELPER), argument],
                                     env=environment, pass_fds=(slave,), preexec_fn=attach_tty,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.PIPE, timeout=5)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(process.stderr, b"")
            return os.read(master, 4096) if select.select([master], [], [], .05)[0] else b""
        finally:
            os.close(slave)
            os.close(master)

    def test_null_standard_streams_use_controlling_terminal(self):
        packet = self.run_on_controlling_tty(json.dumps(self.payload()))
        title, body = self.decode_kitty(packet)
        self.assertEqual(title, "Codex")
        self.assertIn("東京", body)

    def test_invalid_json_and_background_exec_do_not_emit(self):
        self.assertEqual(self.run_on_controlling_tty("{"), b"")
        payload = {**self.payload(), "client": "codex_exec"}
        self.assertEqual(self.run_on_controlling_tty(json.dumps(payload)), b"")

    def test_unsupported_terminals_do_not_emit(self):
        for term in ("xterm-ghostty", "xterm-256color"):
            with self.subTest(term=term):
                self.assertEqual(self.run_on_controlling_tty(json.dumps(self.payload()), term), b"")

    def test_tmux_uses_originating_kitty_pane(self):
        with patch.dict(os.environ, {"TMUX": "fixture", "TMUX_PANE": "%3"}), \
                patch.object(subprocess, "check_output", return_value="/dev/pts/8\txterm-kitty\n") as lookup:
            self.assertEqual(TERMINAL(), ("/dev/pts/8", True))
            self.assertIn("%3", lookup.call_args.args[0])
            lookup.assert_called_once()

    def test_tmux_unsupported_client_does_not_use_fallback(self):
        with patch.dict(os.environ, {"TMUX": "fixture", "TMUX_PANE": "%3"}), \
                patch.object(subprocess, "check_output", return_value="/dev/pts/8\txterm-ghostty\n") as lookup:
            self.assertIsNone(TERMINAL())
            lookup.assert_called_once()

    def test_subagent_completion_does_not_emit_but_root_does(self):
        source = json.dumps({"subagent": {"thread_spawn": {"parent_thread_id": ROOT_THREAD}}})
        self.state_database([(ROOT_THREAD, "cli"), (CHILD_THREAD, source)])
        child = {**self.payload(), "thread-id": CHILD_THREAD}
        self.assertEqual(self.run_on_controlling_tty(json.dumps(child)), b"")
        root = {**self.payload(), "thread-id": ROOT_THREAD}
        title, body = self.decode_kitty(self.run_on_controlling_tty(json.dumps(root)))
        self.assertEqual(title, "Codex")
        self.assertEqual(body, root["last-assistant-message"])

    def test_subagent_filter_runs_before_terminal_lookup(self):
        self.state_database([(CHILD_THREAD, json.dumps({"subagent": "review"}))])
        child = {**self.payload(), "thread-id": CHILD_THREAD}
        with patch.object(sys, "argv", [str(HELPER), json.dumps(child)]), \
                patch.dict(HELPER_GLOBALS["main"].__globals__,
                           {"terminal": lambda: self.fail("subagent touched terminal") }):
            HELPER_GLOBALS["main"]()


unittest.main()
