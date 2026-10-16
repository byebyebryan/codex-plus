#!/usr/bin/env python3
"""Send top-level Codex completions through the originating Kitty terminal."""

import base64
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import uuid

from .context import resolve


def is_subagent(thread_id):
    if not isinstance(thread_id, str) or not thread_id:
        return False
    # notify carries the thread ID but not its source. Consult Codex's local
    # index read-only; never suppress ordinary completions if it is unavailable.
    try:
        home = resolve().home
        databases = []
        for path in home.glob("state_*.sqlite"):
            match = re.fullmatch(r"state_(\d+)\.sqlite", path.name)
            if match:
                databases.append((int(match[1]), path))
        for _, path in sorted(databases, reverse=True):
            try:
                with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro",
                                             uri=True, timeout=0.1)) as database:
                    row = database.execute("SELECT source FROM threads WHERE id = ?",
                                           (thread_id,)).fetchone()
            except sqlite3.Error:
                continue
            if row is None:
                continue
            if row[0] == "subagent":
                return True
            try:
                source = json.loads(row[0])
            except (TypeError, ValueError):
                return False
            return isinstance(source, dict) and "subagent" in source
    except (OSError, ValueError):
        pass
    return False


def completion_body(payload):
    if not isinstance(payload, dict) or payload.get("type") != "agent-turn-complete":
        return None
    # codex exec has no interactive terminal notification to replace.
    if payload.get("client") == "codex_exec":
        return None
    body = payload.get("last-assistant-message")
    if not isinstance(body, str):
        return None
    # Assistant text must not terminate the OSC sequence or inject controls.
    # Kitty's base64 body supports LF, so retain paragraph boundaries.
    cleaned = []
    for char in body:
        codepoint = ord(char)
        if char in "\r\n":
            cleaned.append(char)
        elif codepoint < 32 or 127 <= codepoint < 160:
            cleaned.append(" ")
        else:
            cleaned.append(char)
    body = "".join(cleaned)
    lines = body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    body = "\n".join(" ".join(line.split()) for line in lines).strip("\n")
    body = body.encode("utf-8", errors="replace")[:2048]
    body = body.decode("utf-8", errors="ignore") or "Turn complete."
    return body


def notification(payload):
    body = completion_body(payload)
    if body is None:
        return None
    identifier = uuid.uuid4().hex
    encoded = base64.b64encode(body.encode("utf-8")).decode("ascii")
    # Leave the application name unset: Kitty remains the sender.
    # Kitty applies focus filtering and supplies its native default action.
    return (f"\x1b]99;i={identifier}:o=unfocused:d=0;Codex\x07"
            f"\x1b]99;i={identifier}:p=body:e=1:d=1;{encoded}\x07").encode()


def terminal():
    pane = os.environ.get("TMUX_PANE", "")
    if os.environ.get("TMUX"):
        if not re.fullmatch(r"%\d+", pane):
            return None
        info = subprocess.check_output(
            ["tmux", "display-message", "-p", "-t", pane, "#{pane_tty}\t#{client_termname}"],
            text=True, stderr=subprocess.DEVNULL, timeout=2,
        ).strip().split("\t")
        if len(info) != 2 or not re.fullmatch(r"/dev/pts/\d+", info[0]):
            return None
        if "kitty" not in info[1]:
            return None
        return info[0], True
    kitty = bool(os.environ.get("KITTY_WINDOW_ID")) or "kitty" in os.environ.get("TERM", "")
    return ("/dev/tty", False) if kitty else None


def main():
    try:
        payload = json.loads(sys.argv[1])
        # Ignore unsupported events, background exec and subagents before tmux.
        data = notification(payload)
        if data is None or is_subagent(payload.get("thread-id")):
            return
        target = terminal()
        if target is None:
            return
        tty, tmux = target
        if tmux:
            data = b"\x1bPtmux;" + data.replace(b"\x1b", b"\x1b\x1b") + b"\x1b\\"
        fd = os.open(tty, os.O_WRONLY | os.O_NOCTTY | os.O_NONBLOCK)
        try:
            if os.isatty(fd) and (not tmux or os.fstat(fd).st_uid == os.getuid()):
                while data:
                    written = os.write(fd, data)
                    if not written:
                        break
                    data = data[written:]
        finally:
            os.close(fd)
    except (ValueError, IndexError, OSError, subprocess.SubprocessError):
        # A notification helper must not interfere with the Codex session.
        pass


if __name__ == "__main__":
    main()
