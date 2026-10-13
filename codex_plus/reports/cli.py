"""Publish static reports without starting an agent, daemon or web server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .config import load
from .hosting import check_delivery, inspect_hosting
from .store import Store


def readable(value):
    if "publication" in value:
        status = value["publication"]
        output = [f'{value["title"]} ({status})', value.get("url") or "Hosting is unconfigured; the report is stored locally."]
        if value["delivery"]["state"] == "unavailable":
            output.append(value["delivery"]["detail"])
        if value["catalog"]["state"] == "stale":
            output.append("Report stored; catalog update failed: " + value["catalog"]["detail"])
        output.append("Report ID: " + value["report_id"])
        return "\n".join(output)
    if "reports" in value:
        return "\n".join(f'{row["title"]}\n{row.get("url") or row["report_id"]}' for row in value["reports"]) or "No published reports."
    return json.dumps(value, indent=2, ensure_ascii=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--data-root", type=Path, help="Explicit isolated store override")
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    publish = commands.add_parser("publish"); publish.add_argument("--source", type=Path, required=True)
    publish.add_argument("--title", required=True); publish.add_argument("--entrypoint"); publish.add_argument("--project")
    publish.add_argument("--check-delivery", action="store_true")
    get = commands.add_parser("get"); get.add_argument("report_id"); get.add_argument("--check-delivery", action="store_true")
    listing = commands.add_parser("list"); listing.add_argument("--limit", type=int, default=50)
    listing.add_argument("--cursor"); listing.add_argument("--project")
    delete = commands.add_parser("delete"); delete.add_argument("report_id")
    doctor = commands.add_parser("doctor"); doctor.add_argument("--check-hosting", action="store_true")
    repair = commands.add_parser("repair"); repair.add_argument("--apply", action="store_true")
    commands.add_parser("catalog-rebuild")
    args = parser.parse_args(argv)
    try:
        store = Store(load(args.config, data_root=args.data_root))
        if args.command == "publish":
            value = store.publish(args.source, args.title, entrypoint=args.entrypoint, project=args.project)
        elif args.command == "get": value = store.get(args.report_id)
        elif args.command == "list": value = store.list(limit=args.limit, cursor=args.cursor, project=args.project)
        elif args.command == "delete": value = store.delete(args.report_id)
        elif args.command == "doctor":
            value = store.doctor()
            if args.check_hosting: value["hosting"] = inspect_hosting(store.config)
        elif args.command == "repair": value = store.repair(apply=args.apply)
        else:
            if not store.initialized(): raise ValueError("report store is absent")
            with store.locked(): value = {"catalog": store.rebuild()}
        if getattr(args, "check_delivery", False):
            value["delivery"] = check_delivery(store, value)
        print(json.dumps(value, ensure_ascii=False) if args.json else readable(value))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
        print(json.dumps({"error": str(error)[:1024]}) if args.json else "Report error: " + str(error), file=sys.stderr)
        return 1
