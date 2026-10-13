"""Bounded report delivery checks and readonly hosting inspection."""

from __future__ import annotations

import hashlib
import json
import shutil
import socket
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler, Request

from .store import CHUNK, timestamp


class NoRedirect(HTTPRedirectHandler):
    max_redirections = 2
    max_repeats = 1

    def redirect_request(self, request, fp, code, message, headers, newurl):
        old, new = urlsplit(request.full_url), urlsplit(newurl)
        if (old.scheme == new.scheme and old.netloc == new.netloc
                and old.path.endswith("/index.html") and new.path == old.path[:-len("index.html")]
                and not new.query and not new.fragment):
            return super().redirect_request(request, fp, code, message, headers, newurl)
        raise ValueError("report delivery redirected instead of returning its entrypoint")


def clean_detail(error):
    return "".join(c if ord(c) >= 32 else " " for c in str(error))[:1024]


def check_delivery(store, receipt, *, timeout=5):
    result = {"checked_at": timestamp(), "checked_from": socket.gethostname()}
    if not receipt.get("url"):
        return {**result, "state": "unavailable", "detail": "hosting is unconfigured; the local snapshot is retained"}
    record = store.record(receipt["report_id"])
    if record["state"] != "published":
        return {**result, "state": "unavailable", "detail": "report is not published"}
    expected = record["snapshot"]["files"][record["snapshot"]["entrypoint"]]
    started = time.monotonic(); digest = hashlib.sha256(); total = 0
    try:
        request = Request(receipt["url"], headers={"User-Agent": "codex-plus-report/1", "Accept-Encoding": "identity"})
        with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=timeout) as response:
            if response.status != 200:
                raise ValueError("HTTP status was not 200")
            verified_url = response.geturl()
            while True:
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise TimeoutError("report delivery exceeded its time bound")
                sock = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
                if sock is not None:
                    sock.settimeout(remaining)
                chunk = response.read1(min(CHUNK, expected["bytes"] - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > expected["bytes"]:
                    raise ValueError("HTTP response exceeds the published entrypoint size")
                digest.update(chunk)
        if total != expected["bytes"] or digest.hexdigest() != expected["sha256"]:
            raise ValueError("HTTP entrypoint bytes do not match the stored report")
        return {**result, "state": "verified", "http_status": 200, "bytes": total, "verified_url": verified_url}
    except (OSError, ValueError, TimeoutError) as error:
        return {**result, "state": "unavailable", "detail": clean_detail(error)}


def inspect_hosting(config):
    if not config.base_url:
        return {"state": "unconfigured"}
    parsed = urlsplit(config.base_url)
    flags = ["--bg", f"--{'https' if parsed.scheme == 'https' else 'http'}={parsed.port or (443 if parsed.scheme == 'https' else 80)}",
             "--set-path=" + parsed.path.rstrip("/")]
    suggested = ["tailscale", "serve", *flags, str(config.data_root / "public")]
    result = {"state": "unchecked", "provisioning_command": suggested,
              "note": "operator provisioning only; no command was applied"}
    if not shutil.which("tailscale"):
        return {**result, "state": "unavailable", "detail": "tailscale is not installed"}
    try:
        command = subprocess.run(["tailscale", "serve", "status", "--json"], capture_output=True, timeout=5, check=True)
        if len(command.stdout) > 256 * 1024:
            raise ValueError("Serve status exceeds inspection bound")
        state = json.loads(command.stdout)
        handlers = []
        expected_port = parsed.port or (443 if parsed.scheme == "https" else 80)
        matching_scopes = []
        scopes = [("persistent", state), *(("foreground", scope) for scope in state.get("Foreground", {}).values())]
        for scope_name, scope in scopes:
            transport = scope.get("TCP", {}).get(str(expected_port), {})
            if not transport.get("HTTPS" if parsed.scheme == "https" else "HTTP"):
                continue
            for authority, server in scope.get("Web", {}).items():
                endpoint = urlsplit("http://" + authority)
                same_host = endpoint.hostname == parsed.hostname or (
                    "." not in parsed.hostname and endpoint.hostname and endpoint.hostname.split(".")[0] == parsed.hostname)
                if endpoint.port == expected_port and same_host:
                    selected = [handler for mount, handler in server.get("Handlers", {}).items()
                                if mount.rstrip("/") == parsed.path.rstrip("/")]
                    handlers += selected
                    if any(h.get("Path") == str(config.data_root / "public") for h in selected):
                        matching_scopes.append(scope_name)
        matched = any(handler.get("Path") == str(config.data_root / "public") for handler in handlers)
        return {**result, "state": "route_present" if matched else "route_missing", "route_scopes": matching_scopes}
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return {**result, "state": "unavailable", "detail": clean_detail(error)}
