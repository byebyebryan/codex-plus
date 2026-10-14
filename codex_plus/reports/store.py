"""Bounded content-addressed publication with inspectable filesystem recovery."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import uuid

from . import catalog
from .config import Config, absolute_path


CHUNK = 128 * 1024
MAX_RECORD = 2 * 1024 * 1024
OWNER = {"schema": 1, "component": "codex-plus-report"}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def process_birth(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def identity(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("an exact report ID is required")
    return value


def text(value, maximum, *, optional=False):
    if optional and value is None:
        return None
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or any(ord(c) < 32 for c in value):
        raise ValueError("report title/project is empty, invalid or too long")
    return value.strip()


def safe_relative(value):
    if not isinstance(value, str) or not value or len(value) > 4096 or "\\" in value or any(ord(c) < 32 for c in value):
        raise ValueError("invalid bundle-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..") for p in value.split("/")):
        raise ValueError("bundle paths must stay inside the selected report")
    return value


def no_links(path):
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError("symlink paths are not accepted: " + str(candidate))


def owned_directory(path, *, create=False):
    no_links(path)
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o022:
        raise ValueError("report directories must be owned and not writable by others: " + str(path))


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_bytes(path, data):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("refusing to replace an unsafe file: " + str(path))
    temporary = path.parent / (".write-" + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        temporary.replace(path)
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path):
    no_links(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        st = os.fstat(stream.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_size > MAX_RECORD:
            raise ValueError("unsafe or oversized report metadata")
        raw = stream.read(MAX_RECORD + 1)
    if len(raw) > MAX_RECORD:
        raise ValueError("oversized report metadata")
    return json.loads(raw)


def files_under(root, maximum):
    no_links(root)
    if not root.is_dir():
        raise ValueError("report bundle must be a real directory")
    result = []
    for current, directories, files in os.walk(root, followlinks=False):
        current = Path(current)
        for name in directories:
            if (current / name).is_symlink():
                raise ValueError("bundle symlinks are not accepted")
        for name in files:
            path = current / name
            if path.is_symlink():
                raise ValueError("bundle symlinks are not accepted")
            if not stat.S_ISREG(path.lstat().st_mode):
                raise ValueError("bundle contains a non-regular file")
            result.append((safe_relative(path.relative_to(root).as_posix()), path))
            if len(result) > maximum:
                raise ValueError("report exceeds file-count limit")
    return sorted(result)


def read_file(path, maximum, destination=None):
    no_links(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    digest = hashlib.sha256(); count = 0
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ValueError("report file is invalid or exceeds byte limit")
        while chunk := source.read(CHUNK):
            count += len(chunk)
            if count > maximum:
                raise ValueError("report exceeds byte limit")
            digest.update(chunk)
            if destination is not None:
                destination.write(chunk)
        after = os.fstat(source.fileno())
    observed = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if observed(before) != observed(after) or count != before.st_size:
        raise ValueError("source changed during report copying")
    return {"sha256": digest.hexdigest(), "bytes": count}


def describe_source(source, entrypoint, config):
    source = absolute_path(source); no_links(source)
    if source.is_file():
        entrypoint = entrypoint or source.name
        if entrypoint != source.name:
            raise ValueError("single-file entrypoint must match its filename")
        items = [(safe_relative(source.name), source)]
    elif source.is_dir():
        entrypoint = entrypoint or "index.html"
        items = files_under(source, config.max_bundle_files)
    else:
        raise ValueError("source must be an existing regular HTML file or report directory")
    entrypoint = safe_relative(entrypoint)
    if PurePosixPath(entrypoint).suffix.lower() not in (".html", ".htm"):
        raise ValueError("report entrypoint must be HTML")
    description = {}; total = 0
    for name, path in items:
        description[name] = read_file(path, config.max_bundle_bytes - total)
        total += description[name]["bytes"]
    if entrypoint not in description:
        raise ValueError("HTML entrypoint is missing from the selected bundle")
    return source, entrypoint, items, description, total


class Store:
    def __init__(self, config: Config):
        self.config = config
        self.root = config.data_root

    def initialized(self):
        if not self.root.exists():
            no_links(self.root)
            return False
        owned_directory(self.root)
        marker = self.root / "store.json"
        if not marker.exists():
            if any(p.name != "publish.lock" for p in self.root.iterdir()):
                raise ValueError("refusing a nonempty report store without its ownership marker")
            return False
        if read_json(marker) != OWNER:
            raise ValueError("report store ownership/schema does not match")
        for name in ("public", "metadata", "staging", "trash"):
            if (self.root / name).exists():
                owned_directory(self.root / name)
        return True

    @contextmanager
    def locked(self):
        owned_directory(self.root, create=True)
        fd = os.open(self.root / "publish.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode) or os.fstat(fd).st_uid != os.getuid():
                raise ValueError("unsafe report lock file")
            fcntl.flock(fd, fcntl.LOCK_EX)
            marker = self.root / "store.json"
            if not marker.exists():
                if any(p.name != "publish.lock" for p in self.root.iterdir()):
                    raise ValueError("refusing a nonempty store without its ownership marker")
                atomic_bytes(marker, canonical(OWNER))
            if read_json(marker) != OWNER:
                raise ValueError("report store ownership/schema does not match")
            for name in ("public", "metadata", "staging", "trash"):
                owned_directory(self.root / name, create=True)
            if not (self.root / "public/index.html").exists():
                atomic_bytes(self.root / "public/index.html", catalog.render([], False))
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)

    def record(self, report_id):
        path = self.root / "metadata" / (identity(report_id) + ".json")
        record = read_json(path)
        if (not isinstance(record, dict) or record.get("schema") != 1
                or record.get("report_id") != report_id
                or record.get("state") not in ("prepared", "published", "deleting", "deleted")
                or not isinstance(record.get("snapshot"), dict)
                or hashlib.sha256(canonical(record["snapshot"])).hexdigest() != report_id):
            raise ValueError("report metadata identity/schema is invalid")
        snapshot = record["snapshot"]
        text(record.get("created_at"), 64); text(record.get("origin"), 256)
        if record["state"] in ("deleting", "deleted") and (not isinstance(record.get("trash_id"), str)
                or not re.fullmatch(r"[0-9a-f]{32}", record["trash_id"])):
            raise ValueError("invalid deletion operation identity")
        if (snapshot.get("schema") != 1 or not isinstance(snapshot.get("files"), dict)
                or len(snapshot["files"]) > 10000):
            raise ValueError("report snapshot schema/limits are invalid")
        text(snapshot.get("title"), 256); text(snapshot.get("project"), 128, optional=True)
        safe_relative(snapshot.get("entrypoint"))
        for name, info in snapshot["files"].items():
            safe_relative(name)
            if (not isinstance(info, dict) or set(info) != {"bytes", "sha256"}
                    or type(info["bytes"]) is not int or not 0 <= info["bytes"] <= 1024 * 1024 * 1024 * 1024
                    or not isinstance(info["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", info["sha256"])):
                raise ValueError("invalid report file description")
        if snapshot["entrypoint"] not in snapshot["files"]:
            raise ValueError("report metadata lacks its entrypoint")
        return record

    def records(self):
        if not self.initialized():
            return []
        metadata = self.root / "metadata"
        if not metadata.exists():
            return []
        result = []
        for path in metadata.iterdir():
            if path.name.startswith(".write-"):
                continue
            if path.suffix != ".json":
                raise ValueError("unknown report metadata member")
            result.append(self.record(path.stem))
            if len(result) > 10000:
                raise ValueError("report metadata inventory exceeds read bound")
        return result

    def save(self, record):
        data = canonical(record)
        if len(data) > MAX_RECORD:
            raise ValueError("report metadata exceeds the 2 MiB read bound")
        atomic_bytes(self.root / "metadata" / (identity(record["report_id"]) + ".json"), data)

    def verify(self, record):
        root = self.root / "public" / record["report_id"]
        expected = record["snapshot"]["files"]
        observed = {}
        for name, path in files_under(root, 10000):
            if name not in expected:
                raise ValueError("published snapshot contains unexpected files")
            observed[name] = read_file(path, expected[name]["bytes"])
        if observed != record["snapshot"]["files"]:
            raise ValueError("published snapshot integrity differs; it was not overwritten")

    def rebuild(self):
        records = [self.flatten(r) for r in self.records() if r["state"] == "published"]
        atomic_bytes(self.root / "public/index.html", catalog.render(records, self.config.catalog_enabled))
        atomic_bytes(self.root / "catalog.json", canonical({"schema": 1, "updated_at": timestamp(), "enabled": self.config.catalog_enabled}))
        return {"state": "updated" if self.config.catalog_enabled else "disabled"}

    def catalog_result(self):
        try:
            return self.rebuild()
        except (OSError, ValueError) as error:
            return {"state": "stale", "detail": str(error)[:1024]}

    @staticmethod
    def flatten(record):
        snap = record["snapshot"]
        return {"report_id": record["report_id"], "title": snap["title"], "project": snap["project"],
                "entrypoint": snap["entrypoint"], "created_at": record["created_at"], "state": record["state"]}

    def receipt(self, record, publication=None, catalog_state=None):
        result = self.flatten(record)
        result.update(schema=1, publication=publication or record["state"], origin=record["origin"],
                      snapshot_path=str(self.root / "public" / record["report_id"]),
                      file_count=len(record["snapshot"]["files"]),
                      byte_count=sum(f["bytes"] for f in record["snapshot"]["files"].values()),
                      url=record.get("url") or (self.config.base_url + catalog.relative_url(self.flatten(record))
                                               if self.config.base_url else None),
                      catalog=catalog_state or {"state": "unchecked"},
                      delivery={"state": "unchecked"})
        return result

    def capacity(self, total, report_id):
        inventory = self.records()
        if len(inventory) >= 10000 and report_id not in {r["report_id"] for r in inventory}:
            raise ValueError("report metadata history is full; no new identity was stored")
        records = []
        for record in inventory:
            if record['state'] == 'deleted':
                trash = self.root / 'trash' / record['trash_id']
                no_links(trash)
                if not trash.exists():
                    continue
            records.append(record)
        used = sum(sum(f["bytes"] for f in r["snapshot"]["files"].values()) for r in records)
        reserved = 0; operations = 0
        for path in (self.root / "staging").iterdir():
            operation = read_json(path / "operation.json")
            if operation.get("schema") != 1 or type(operation.get("reserved_bytes")) is not int:
                raise ValueError("unknown staging operation; inspect doctor/repair")
            reserved += operation["reserved_bytes"]; operations += 1
        if used + reserved + total > self.config.max_store_bytes or len(records) + operations + 1 > self.config.max_store_reports:
            raise ValueError("report store capacity exceeded; explicitly remove reports or change configured limits")

    def check_republication(self, record):
        if record['state'] == 'deleting':
            raise ValueError("this report has an interrupted deletion; inspect repair")
        if record['state'] == 'deleted':
            trash = self.root / 'trash' / record['trash_id']
            no_links(trash)
            if trash.exists():
                raise ValueError("this report has unfinished trash cleanup; retry deletion or apply repair before republishing")

    def remove_trash(self, record):
        trash = self.root / 'trash' / record['trash_id']
        no_links(trash)
        if trash.exists():
            files_under(trash, 10000)
            shutil.rmtree(trash)
            sync_directory(trash.parent)

    def publish(self, source, title, *, entrypoint=None, project=None):
        source = absolute_path(source)
        if source == self.root or source.is_relative_to(self.root) or self.root.is_relative_to(source):
            raise ValueError("the report store itself cannot be a publication source")
        source, entrypoint, items, description, total = describe_source(source, entrypoint, self.config)
        snapshot = {"schema": 1, "entrypoint": entrypoint, "title": text(title, 256),
                    "project": text(project, 128, optional=True), "files": description}
        # Leave room for provenance, URL and deletion state. Never write a
        # snapshot that subsequent bounded reads cannot inspect or recover.
        if len(canonical(snapshot)) > MAX_RECORD - 16384:
            raise ValueError("report metadata exceeds the 2 MiB read bound")
        report_id = hashlib.sha256(canonical(snapshot)).hexdigest()
        operation_id = uuid.uuid4().hex; stage = self.root / "staging" / operation_id
        with self.locked():
            path = self.root / "metadata" / (report_id + ".json")
            if path.exists():
                existing = self.record(report_id)
                self.check_republication(existing)
                if existing["state"] in ("published", "prepared") and (self.root / "public" / report_id).exists():
                    self.verify(existing)
                    existing["state"] = "published"; self.save(existing)
                    return self.receipt(existing, "reused", self.catalog_result())
            elif (self.root / "public" / report_id).exists():
                raise ValueError("unregistered snapshot exists; inspect doctor/repair")
            self.capacity(total, report_id)
            stage.mkdir(mode=0o700)
            atomic_bytes(stage / "operation.json", canonical({"schema": 1, "operation_id": operation_id,
                         "report_id": report_id, "reserved_bytes": total,
                         "pid": os.getpid(), "process_birth": process_birth(os.getpid())}))
            (stage / "bundle").mkdir(mode=0o700)
        try:
            for name, path in items:
                target = stage / "bundle" / name; target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, "wb") as destination:
                    observed = read_file(path, description[name]["bytes"], destination)
                    destination.flush(); os.fsync(destination.fileno())
                if observed != description[name]:
                    raise ValueError("source changed between hashing and copying")
            if source.is_dir() and [name for name, _ in files_under(source, self.config.max_bundle_files)] != list(description):
                raise ValueError("source file inventory changed during publication")
            with self.locked():
                target = self.root / "public" / report_id
                path = self.root / "metadata" / (report_id + ".json")
                if path.exists():
                    self.check_republication(self.record(report_id))
                if target.exists():
                    existing = self.record(report_id); self.verify(existing)
                    existing["state"] = "published"; self.save(existing)
                    return self.receipt(existing, "reused", self.catalog_result())
                record = {"schema": 1, "report_id": report_id, "snapshot": snapshot,
                          "state": "prepared", "created_at": timestamp(), "origin": socket.gethostname(),
                          "source": str(source), "url": None}
                if self.config.base_url:
                    record["url"] = self.config.base_url + catalog.relative_url(self.flatten(record))
                self.save(record)
                # Completed bytes become visible together. The prepared record
                # survives failure before the following commit for exact retry.
                (stage / "bundle").rename(target); sync_directory(target.parent)
                record["state"] = "published"; self.save(record)
                return self.receipt(record, "created", self.catalog_result())
        finally:
            with self.locked():
                if stage.exists():
                    shutil.rmtree(stage)

    def get(self, report_id):
        if not self.initialized():
            raise ValueError("report store has no published reports")
        return self.receipt(self.record(identity(report_id)))

    def list(self, *, limit=50, cursor=None, project=None):
        if type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError("list limit must be between 1 and 200")
        records = sorted((self.flatten(r) for r in self.records() if r["state"] == "published"
                          and (project is None or r["snapshot"]["project"] == project)),
                         key=lambda r: (r["created_at"], r["report_id"]), reverse=True)
        offset = 0
        if cursor:
            identity(cursor)
            matches = [i for i, r in enumerate(records) if r["report_id"] == cursor]
            if not matches:
                raise ValueError("inventory cursor is no longer present; restart listing")
            offset = matches[0] + 1
        rows = records[offset:offset + limit]
        for row in rows:
            row["url"] = self.receipt(self.record(row["report_id"]))["url"]
        return {"reports": rows, "next_cursor": rows[-1]["report_id"] if rows and offset + limit < len(records) else None,
                "total": len(records)}

    def delete(self, report_id):
        identity(report_id)
        if not self.initialized():
            raise ValueError("report store is absent")
        with self.locked():
            record = self.record(report_id)
            if record["state"] == "deleted":
                self.remove_trash(record)
                return {"report_id": report_id, "state": "deleted", "catalog": self.catalog_result()}
            if record["state"] not in ("published", "deleting"):
                raise ValueError("uncommitted report needs explicit repair before deletion")
            if record["state"] == "published":
                self.verify(record)
                record.update(state="deleting", trash_id=uuid.uuid4().hex); self.save(record)
            trash = self.root / "trash" / record["trash_id"]
            public = self.root / "public" / report_id
            if public.exists():
                if trash.exists():
                    raise ValueError("ambiguous public/trash deletion state")
                public.rename(trash); sync_directory(public.parent)
            record.update(state="deleted", deleted_at=timestamp()); self.save(record)
            self.remove_trash(record)
            return {"report_id": report_id, "state": "deleted", "catalog": self.catalog_result()}

    def doctor(self):
        if not self.initialized():
            return {"store": "absent", "data_root": str(self.root), "base_url": self.config.base_url,
                    "delivery": "unconfigured" if self.config.base_url is None else "unchecked", "gaps": []}
        records = self.records(); known = {r["report_id"] for r in records}
        gaps = [{"report_id": r["report_id"], "state": r["state"]} for r in records if r["state"] in ("prepared", "deleting")]
        gaps += [{"report_id": r["report_id"], "state": "missing_snapshot"} for r in records
                 if r["state"] == "published" and not (self.root / "public" / r["report_id"]).is_dir()]
        public = self.root / "public"
        for path in public.iterdir() if public.exists() else []:
            if path.name != "index.html" and not path.name.startswith(".write-") and path.name not in known:
                gaps.append({"unknown_public_member": path.name})
        stages = [p.name for p in (self.root / "staging").iterdir()] if (self.root / "staging").exists() else []
        expected_index = catalog.render([self.flatten(r) for r in records if r["state"] == "published"], self.config.catalog_enabled)
        index = self.root / "public/index.html"
        no_links(index)
        actual_index = index.read_bytes() if index.exists() and index.stat().st_size <= MAX_RECORD else None
        return {"store": "initialized", "data_root": str(self.root), "base_url": self.config.base_url,
                "published": sum(r["state"] == "published" for r in records), "gaps": gaps,
                "staging": stages, "trash": [p.name for p in (self.root / "trash").iterdir()] if (self.root / "trash").exists() else [],
                "catalog": "current" if actual_index == expected_index else "stale"}

    def repair(self, *, apply=False):
        preview = self.doctor()
        if not apply or preview["store"] == "absent":
            return {"applied": False, "preview": preview}
        repaired = []
        with self.locked():
            for record in self.records():
                if record["state"] == "prepared" and (self.root / "public" / record["report_id"]).exists():
                    self.verify(record); record["state"] = "published"; self.save(record)
                    repaired.append(record["report_id"])
            active_reports = set()
            for stage in (self.root / "staging").iterdir():
                if (re.fullmatch(r"[0-9a-f]{32}", stage.name) and stage.is_dir()
                        and not stage.is_symlink() and not any(stage.iterdir())):
                    stage.rmdir(); repaired.append("empty-staging:" + stage.name)
                    continue
                operation = read_json(stage / "operation.json")
                if (operation.get("schema") != 1 or operation.get("operation_id") != stage.name
                        or not re.fullmatch(r"[0-9a-f]{32}", stage.name)
                        or type(operation.get("pid")) is not int or operation["pid"] <= 0
                        or not isinstance(operation.get("process_birth"), str)):
                    raise ValueError("unrecognized staging operation; no cleanup attempted")
                identity(operation.get("report_id"))
                if process_birth(operation["pid"]) != operation["process_birth"]:
                    files_under(stage, 10002); shutil.rmtree(stage)
                    repaired.append("staging:" + stage.name)
                else:
                    active_reports.add(operation["report_id"])
            for record in self.records():
                if (record["state"] == "prepared" and record["report_id"] not in active_reports
                        and not (self.root / "public" / record["report_id"]).exists()):
                    # No report became public and no publisher can still commit
                    # this reservation. Explicit repair releases its capacity.
                    (self.root / "metadata" / (record["report_id"] + ".json")).unlink()
                    sync_directory(self.root / "metadata")
                    repaired.append("unpublished:" + record["report_id"])
            for record in self.records():
                if record["state"] == "deleted":
                    trash = self.root / "trash" / record["trash_id"]
                    if trash.exists() or trash.is_symlink():
                        self.remove_trash(record)
                        repaired.append("trash:" + record["trash_id"])
            catalog_state = self.catalog_result()
        # Deletion retries take their own lock and preserve exact selected identity.
        for record in self.records():
            if record["state"] == "deleting":
                self.delete(record["report_id"]); repaired.append(record["report_id"])
        return {"applied": True, "repaired": repaired, "catalog": catalog_state, "remaining": self.doctor()}
