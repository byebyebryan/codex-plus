"""Validated user configuration; loading never creates state or serving routes."""

from __future__ import annotations

from dataclasses import dataclass, fields
import ipaddress
import os
from pathlib import Path
import tomllib
from urllib.parse import unquote, urlsplit, urlunsplit


def absolute_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("an absolute path without parent traversal is required")
    return path


def data_home() -> Path:
    return absolute_path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")


def config_path() -> Path:
    root = absolute_path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return root / "codex-plus/report.toml"


def base_url(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 4096 or any(ord(c) <= 32 for c in value):
        raise ValueError("invalid report base URL")
    parsed = urlsplit(value)
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment):
        raise ValueError("report base URL must be host-addressed HTTP/HTTPS without credentials, query or fragment")
    parsed.port  # Validate the port, including malformed/out-of-range ports.
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("localhost report links cannot roam between desktops")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if address.is_loopback or address.is_unspecified:
            raise ValueError("loopback/unspecified report links cannot roam between desktops")
    path = parsed.path or "/"
    if any(p in (".", "..") for p in unquote(path).split("/")) or "\\" in unquote(path):
        raise ValueError("report base URL contains path traversal")
    return urlunsplit((parsed.scheme, parsed.netloc, path.rstrip("/") + "/", "", ""))


@dataclass(frozen=True)
class Config:
    data_root: Path
    base_url: str | None = None
    catalog_enabled: bool = True
    max_bundle_bytes: int = 100 * 1024 * 1024
    max_bundle_files: int = 2000
    max_store_bytes: int = 5 * 1024 * 1024 * 1024
    max_store_reports: int = 1000
    server_bind: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "data_root", absolute_path(self.data_root))
        object.__setattr__(self, "base_url", base_url(self.base_url))
        if self.server_bind is not None and (not isinstance(self.server_bind, str)
                or not self.server_bind or len(self.server_bind) > 256
                or any(c.isspace() or ord(c) < 32 or c in '/\\' for c in self.server_bind)):
            raise ValueError("server_bind must be an IP address or hostname")
        if type(self.catalog_enabled) is not bool:
            raise ValueError("catalog_enabled must be boolean")
        for name in ("max_bundle_bytes", "max_bundle_files", "max_store_bytes", "max_store_reports"):
            if type(getattr(self, name)) is not int or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_bundle_bytes > self.max_store_bytes:
            raise ValueError("bundle byte limit cannot exceed store byte limit")
        if self.max_bundle_files > 10000 or self.max_store_reports > 10000:
            raise ValueError("file/report limits cannot exceed the metadata read bound of 10000")


def load(path: Path | None = None, *, data_root: Path | None = None) -> Config:
    selected = absolute_path(path) if path is not None else config_path()
    values = {}
    if selected.exists() or selected.is_symlink():
        if selected.is_symlink() or not selected.is_file():
            raise ValueError("report config must be a regular file")
        if selected.stat().st_size > 65536:
            raise ValueError("report config exceeds 64 KiB")
        values = tomllib.loads(selected.read_text())
        schema = values.pop("schema", None)
        if type(schema) is not int or schema != 1:
            raise ValueError("unsupported report configuration schema")
    allowed = {field.name for field in fields(Config)}
    if set(values) - allowed:
        raise ValueError("unknown report configuration fields: " + ", ".join(sorted(set(values) - allowed)))
    values["data_root"] = data_root or values.get("data_root") or data_home() / "codex-plus/reports"
    return Config(**values)
