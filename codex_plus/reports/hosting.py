"""Bounded report delivery checks and readonly hosting inspection."""

from __future__ import annotations

import hashlib
import json
import socket
import time
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler, Request

from .store import CHUNK, Store, read_file, timestamp


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


def verify_http(url, expected, *, timeout=5):
    result = {"checked_at": timestamp(), "checked_from": socket.gethostname()}
    started = time.monotonic(); digest = hashlib.sha256(); total = 0
    try:
        request = Request(url, headers={"User-Agent": "codex-plus-report/1", "Accept-Encoding": "identity"})
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



def check_delivery(store, receipt, *, timeout=5):
    if not receipt.get("url"):
        return {"state": "unavailable", "detail": "hosting is unconfigured; the local snapshot is retained"}
    record = store.record(receipt["report_id"])
    if record["state"] != "published":
        return {"state": "unavailable", "detail": "report is not published"}
    expected = record["snapshot"]["files"][record["snapshot"]["entrypoint"]]
    return verify_http(receipt["url"], expected, timeout=timeout)


def inspect_hosting(config):
    if not config.base_url:
        return {"state": "unconfigured"}
    store = Store(config)
    if not store.initialized():
        return {"state": "store_absent", "url": config.base_url}
    try:
        expected = read_file(config.data_root / "public/index.html", 2 * 1024 * 1024)
        return {"url": config.base_url, **verify_http(config.base_url, expected)}
    except (OSError, ValueError) as error:
        return {"url": config.base_url, "state": "unavailable", "detail": clean_detail(error)}
