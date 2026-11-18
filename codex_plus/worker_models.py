"""Pure resolution of concrete native model IDs for named worker families.

The catalogue passed to this module is supplied by the caller. This module does
not contact a native service, perform inference, or install the selected models.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
import tomllib


MAX_CATALOG_BYTES = 2 * 1024 * 1024
MAX_CATALOG_ROWS = 1024
MAX_JSON_NODES = 100_000
MAX_JSON_DEPTH = 64
MAX_JSON_STRING_BYTES = 64 * 1024
MAX_PREFERENCES_BYTES = 64 * 1024

FAMILY_MINIMUMS = {
    "sol": (6, 1),
    "astra": (6, 0),
    "luna": (6, 0),
    "terra": (6, 1),
}

ROLE_SPECS = {
    "sol-xhigh": ("sol", "xhigh"),
    "astra-xhigh": ("astra", "xhigh"),
    "luna-max": ("luna", "max"),
    "terra-6-1-xhigh": ("terra", "xhigh"),
}

_MODEL_ID = re.compile(r"gpt-(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?-(sol|astra|luna|terra)\Z")


class WorkerModelError(ValueError):
    """Raised when supplied catalogue or preference metadata is unsafe to use."""


def _model_parts(model: object) -> tuple[str, tuple[int, int]] | None:
    if not isinstance(model, str) or len(model) > 256:
        return None
    match = _MODEL_ID.fullmatch(model)
    if match is None:
        return None
    try:
        major = int(match.group(1))
        minor = int(match.group(2) or "0")
    except ValueError:
        return None
    return match.group(3), (major, minor)


def family_for_model(model: str) -> str | None:
    """Return a supported family only for an exact concrete ID at its floor."""
    parts = _model_parts(model)
    if parts is None:
        return None
    family, version = parts
    if version < FAMILY_MINIMUMS[family]:
        return None
    return family


def _validate_json_tree(value: object) -> int:
    """Validate a parsed JSON tree and return its encoded size estimate."""
    stack = [(value, 0)]
    nodes = 0
    string_bytes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise WorkerModelError("catalogue is too large")
        if depth > MAX_JSON_DEPTH:
            raise WorkerModelError("catalogue nesting is too deep")
        if current is None or isinstance(current, (bool, str)):
            if isinstance(current, str):
                try:
                    string_bytes += len(current.encode("utf-8"))
                except UnicodeEncodeError as error:
                    raise WorkerModelError("catalogue contains invalid text") from error
                if len(current) > MAX_JSON_STRING_BYTES:
                    raise WorkerModelError("catalogue contains an oversized string")
        elif isinstance(current, int) and not isinstance(current, bool):
            if current.bit_length() > 4096:
                raise WorkerModelError("catalogue contains an oversized number")
        elif isinstance(current, float):
            if not math.isfinite(current):
                raise WorkerModelError("catalogue must contain finite JSON numbers")
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
        elif isinstance(current, dict):
            for key, item in current.items():
                if not isinstance(key, str):
                    raise WorkerModelError("catalogue object keys must be strings")
                try:
                    string_bytes += len(key.encode("utf-8"))
                except UnicodeEncodeError as error:
                    raise WorkerModelError("catalogue contains invalid text") from error
                if len(key) > MAX_JSON_STRING_BYTES:
                    raise WorkerModelError("catalogue contains an oversized key")
                stack.append((item, depth + 1))
        else:
            raise WorkerModelError("catalogue must contain JSON values")
        if string_bytes > MAX_CATALOG_BYTES:
            raise WorkerModelError("catalogue is too large")
    return string_bytes


def _catalogue_rows(catalog: object) -> list[dict[str, object]]:
    _validate_json_tree(catalog)
    try:
        encoded_size = len(json.dumps(catalog, ensure_ascii=False, allow_nan=False,
                                      separators=(",", ":")).encode("utf-8"))
    except (TypeError, ValueError, RecursionError, UnicodeEncodeError) as error:
        raise WorkerModelError("catalogue must be valid JSON") from error
    if encoded_size > MAX_CATALOG_BYTES:
        raise WorkerModelError("catalogue is too large")

    if isinstance(catalog, list):
        rows = catalog
    elif isinstance(catalog, dict):
        rows = catalog.get("data")
        if not isinstance(rows, list):
            raise WorkerModelError("catalogue must contain a data array")
        if "nextCursor" in catalog and catalog["nextCursor"] is not None:
            raise WorkerModelError("catalogue is incomplete because nextCursor is set")
    else:
        raise WorkerModelError("catalogue must be a native data array or list response")

    if len(rows) > MAX_CATALOG_ROWS:
        raise WorkerModelError("catalogue has too many rows")
    normalized: list[dict[str, object]] = []
    execution_ids: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise WorkerModelError("catalogue rows must be objects")
        model = row.get("model")
        if not isinstance(model, str) or not model or len(model) > 256:
            raise WorkerModelError("catalogue row is missing a bounded model execution ID")
        previous = execution_ids.get(model)
        if previous is not None:
            if previous != row:
                raise WorkerModelError("catalogue has conflicting metadata for a model execution ID")
            continue
        execution_ids[model] = row

        parts = _model_parts(model)
        if parts is not None:
            hidden = row.get("hidden")
            effort_metadata = row.get("supportedReasoningEfforts")
            if type(hidden) is not bool:
                raise WorkerModelError("known model rows require boolean hidden metadata")
            if not isinstance(effort_metadata, list):
                raise WorkerModelError("known model rows require an unambiguous supportedReasoningEfforts list")
            efforts: list[str] = []
            for effort_item in effort_metadata:
                if not isinstance(effort_item, dict):
                    raise WorkerModelError("supportedReasoningEfforts entries must be objects")
                effort = effort_item.get("reasoningEffort")
                if not isinstance(effort, str) or not effort or len(effort) > 64:
                    raise WorkerModelError("supportedReasoningEfforts entries require a bounded reasoningEffort")
                efforts.append(effort)
            if len(set(efforts)) != len(efforts):
                raise WorkerModelError("supportedReasoningEfforts contains duplicate reasoningEffort values")
            normalized.append({
                "model": model,
                "family": parts[0],
                "version": parts[1],
                "hidden": hidden,
                "efforts": tuple(efforts),
            })
    return normalized


def _preferences(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict) or set(value) - {"models"}:
        raise WorkerModelError("preferences may contain only a models table")
    models = value.get("models", {})
    if not isinstance(models, dict):
        raise WorkerModelError("preferences.models must be a table")
    unknown_families = set(models) - set(FAMILY_MINIMUMS)
    if unknown_families:
        raise WorkerModelError("preferences contain an unknown model family")

    result: dict[str, str] = {}
    for family, table in models.items():
        if not isinstance(table, dict) or set(table) - {"version"}:
            raise WorkerModelError("each model preference may contain only version")
        if "version" not in table:
            raise WorkerModelError("each model preference requires a version")
        version = table["version"]
        if not isinstance(version, str) or not version:
            raise WorkerModelError("model preference version must be a string")
        if version == "latest-available":
            result[family] = version
            continue
        parts = _model_parts(version)
        if parts is None:
            raise WorkerModelError("model preference version must be latest-available or a concrete model ID")
        result[family] = version
    return result


def _evidence_models(rows: list[dict[str, object]], family: str) -> list[dict[str, object]]:
    family_rows = [row for row in rows if row["family"] == family]
    family_rows.sort(key=lambda row: (row["version"], row["model"]))
    return [{
        "model": row["model"],
        "version": list(row["version"]),
        "hidden": row["hidden"],
        "supported_reasoning_efforts": sorted(row["efforts"]),
        "meets_family_floor": row["version"] >= FAMILY_MINIMUMS[family],
    } for row in family_rows]


def _role_result(
    family: str,
    effort: str,
    preference: str,
    rows: list[dict[str, object]],
    total_rows: int,
) -> dict[str, object]:
    family_rows = [row for row in rows if row["family"] == family]
    evidence: dict[str, object] = {
        "source": "supplied-catalogue-only",
        "execution_id_field": "model",
        "catalogue_complete": True,
        "catalogue_row_count": total_rows,
        "family_models": _evidence_models(rows, family),
    }

    resolved: dict[str, object] | None = None
    reason: str | None = None
    if preference == "latest-available":
        eligible = [row for row in family_rows
                    if row["version"] >= FAMILY_MINIMUMS[family]
                    and row["hidden"] is False and effort in row["efforts"]]
        eligible.sort(key=lambda row: (row["version"], row["model"]))
        evidence["eligible_picker_models"] = [row["model"] for row in eligible]
        if not eligible:
            reason = "no-picker-visible-model-supports-effort"
        else:
            newest_version = eligible[-1]["version"]
            newest = [row for row in eligible if row["version"] == newest_version]
            if len(newest) != 1:
                reason = "ambiguous-latest-numeric-version"
            else:
                resolved = newest[0]
    else:
        pinned_parts = _model_parts(preference)
        assert pinned_parts is not None
        pinned_family, pinned_version = pinned_parts
        if pinned_family != family:
            reason = "pinned-model-family-mismatch"
        elif pinned_version < FAMILY_MINIMUMS[family]:
            reason = "pinned-model-below-family-floor"
        else:
            pinned = next((row for row in family_rows if row["model"] == preference), None)
            if pinned is None:
                reason = "pinned-model-not-in-catalogue"
            elif effort not in pinned["efforts"]:
                reason = "pinned-model-does-not-support-effort"
            else:
                resolved = pinned
        evidence["exact_pin"] = preference
        evidence["exact_pin_may_be_hidden"] = True

    if resolved is None:
        evidence["reason"] = reason
        return {
            "family": family,
            "preference": preference,
            "model": None,
            "reasoning_effort": effort,
            "status": "unavailable",
            "evidence": evidence,
        }

    evidence["selected_picker_visible"] = resolved["hidden"] is False
    evidence["selected_supported_reasoning_efforts"] = sorted(resolved["efforts"])
    return {
        "family": family,
        "preference": preference,
        "model": resolved["model"],
        "reasoning_effort": effort,
        "status": "resolved",
        "evidence": evidence,
    }


def resolve_catalog(catalog: object, preferences: object = None) -> dict[str, object]:
    """Resolve the four stable worker roles from a complete supplied catalogue.

    ``catalog`` accepts either the native model/list response object with a
    ``data`` array and a null or absent ``nextCursor``, or that array directly.
    Preferences are parsed TOML values, with the shape ``{"models": {...}}``.
    """
    rows = _catalogue_rows(catalog)
    selected_preferences = _preferences(preferences)
    if isinstance(catalog, dict):
        total_rows = len(catalog["data"])
    else:
        total_rows = len(catalog)
    roles = {
        role: _role_result(family, effort,
                           selected_preferences.get(family, "latest-available"),
                           rows, total_rows)
        for role, (family, effort) in ROLE_SPECS.items()
    }
    return {
        "schema": 1,
        "catalogue_source": "supplied-native-model-list",
        "catalogue_complete": True,
        "roles": roles,
    }


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WorkerModelError("JSON input contains duplicate object keys")
        result[key] = value
    return result


def _reject_constant(_: str) -> object:
    raise WorkerModelError("JSON input contains a non-finite number")


def _read_limited(path: Path, limit: int, label: str) -> bytes:
    try:
        with path.open("rb") as stream:
            payload = stream.read(limit + 1)
    except OSError as error:
        raise WorkerModelError(f"could not read {label}") from error
    if len(payload) > limit:
        raise WorkerModelError(f"{label} is too large")
    return payload


def _read_catalog(path: Path) -> object:
    payload = _read_limited(path, MAX_CATALOG_BYTES, "catalogue")
    try:
        return json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WorkerModelError("catalogue is not valid UTF-8 JSON") from error
    except RecursionError as error:
        raise WorkerModelError("catalogue nesting is too deep") from error


def _read_preferences(path: Path | None) -> object:
    if path is None:
        return None
    payload = _read_limited(path, MAX_PREFERENCES_BYTES, "preferences")
    try:
        return tomllib.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise WorkerModelError("preferences are not valid UTF-8 TOML") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve concrete model IDs for Codex Plus worker roles.")
    operations = parser.add_subparsers(dest="operation", required=True)
    resolve = operations.add_parser("resolve", help="resolve roles from a supplied native model/list catalogue")
    resolve.add_argument("--catalog", type=Path, required=True)
    resolve.add_argument("--preferences", type=Path)
    classify = operations.add_parser("classify", help="classify one exact concrete model ID")
    classify.add_argument("--model", required=True)
    args = parser.parse_args(argv)

    try:
        if args.operation == "classify":
            print(json.dumps({"model": args.model, "family": family_for_model(args.model)},
                             sort_keys=True, ensure_ascii=False, separators=(",", ":")))
            return 0
        result = resolve_catalog(_read_catalog(args.catalog), _read_preferences(args.preferences))
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
        return 0
    except WorkerModelError as error:
        print(json.dumps({"error": str(error)}, sort_keys=True), file=sys.stderr)
        return 1


__all__ = ["FAMILY_MINIMUMS", "ROLE_SPECS", "WorkerModelError", "family_for_model",
           "resolve_catalog", "main"]
