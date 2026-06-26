#!/usr/bin/env python3
"""Migrate legacy governance_events.jsonl entries into decision-log.jsonl (v5.0).

This is a one-shot migration utility. It does NOT delete the source file
after migration — operators should confirm the destination is intact and
then remove the source manually.

Usage:
    python scripts/migrate_governance_events.py [--repo <path>] [--dry-run]

Exit codes:
    0 — migration succeeded (no fatal errors; some lines may have been skipped)
    2 — migration failed (source unreadable, destination unwritable, etc.)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPO = SKILL_DIR

SOURCE_FILENAME = ".skill-metrics/governance_events.jsonl"
DEST_FILENAME = ".skill-metrics/decision-log.jsonl"

# Schema version enforced by references/decision-log.schema.json
DECISION_LOG_VERSION = "decision-log/v1"

# Defaults applied to legacy entries that predate the v5.0 schema.
LEGACY_DEFAULTS: dict[str, object] = {
    "decision": "route_selected",
    "verifier": "n_a",
    "reason": "",
}

REQUIRED_FIELDS = (
    "timestamp",
    "decision",
    "lead_agent",
    "verifier",
    "risk_level",
    "selected_track",
    "reason",
    "mode_hint",
)

# `reason` is `minLength: 0` in decision-log.schema.json — the schema
# requires the field to exist but explicitly allows empty strings for
# legacy entries. The other required fields still need a non-empty value.
FIELDS_ALLOWING_EMPTY = frozenset({"reason"})


def _coerce_str(value: object, default: str) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return default
    return str(value)


def _normalize_entry(raw: dict[str, object]) -> dict[str, object]:
    """Apply legacy defaults and ensure all v5.0 required fields are present."""
    entry: dict[str, object] = dict(raw)
    for key, default in LEGACY_DEFAULTS.items():
        if key not in entry or entry[key] is None:
            entry[key] = default
    # Ensure types are strings where the schema demands them.
    for field in REQUIRED_FIELDS:
        if field not in entry or entry[field] is None:
            entry[field] = ""
        elif not isinstance(entry[field], str):
            entry[field] = str(entry[field])
    # evidence is the only optional field; if missing, omit it (None in entry
    # would violate additionalProperties=false schema); only set if present.
    if "evidence" in entry and entry["evidence"] is not None and not isinstance(entry["evidence"], str):
        entry["evidence"] = str(entry["evidence"])
    return entry


def _looks_valid(entry: dict[str, object]) -> tuple[bool, str]:
    for field in REQUIRED_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str):
            return False, f"missing or non-string required field: {field}"
        if value == "" and field not in FIELDS_ALLOWING_EMPTY:
            return False, f"missing or empty required field: {field}"
    timestamp = entry.get("timestamp", "")
    if not isinstance(timestamp, str) or "T" not in timestamp:
        return False, "timestamp is not ISO 8601"
    return True, ""


def migrate(repo_path: Path, dry_run: bool = False) -> dict[str, object]:
    source = repo_path / SOURCE_FILENAME
    destination = repo_path / DEST_FILENAME

    result: dict[str, object] = {
        "schema_version": DECISION_LOG_VERSION,
        "source": str(source),
        "destination": str(destination),
        "dry_run": dry_run,
        "total_lines": 0,
        "migrated": 0,
        "skipped_invalid": 0,
        "skipped_blank": 0,
        "errors": [],
    }

    if not source.exists():
        result["errors"].append(f"source file not found: {source}")
        result["ok"] = False
        return result

    try:
        with source.open("r", encoding="utf-8") as fh:
            raw_lines = fh.readlines()
    except Exception as exc:
        result["errors"].append(f"failed to read source: {exc!r}")
        result["ok"] = False
        return result

    result["total_lines"] = len(raw_lines)
    migrated_lines: list[str] = []

    for line_no, raw in enumerate(raw_lines, start=1):
        stripped = raw.strip()
        if stripped == "":
            result["skipped_blank"] += 1
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            result["skipped_invalid"] += 1
            result["errors"].append(f"line {line_no}: JSON decode error: {exc.msg}")
            continue
        if not isinstance(parsed, dict):
            result["skipped_invalid"] += 1
            result["errors"].append(f"line {line_no}: top-level value is not an object")
            continue
        normalized = _normalize_entry(parsed)
        ok, why = _looks_valid(normalized)
        if not ok:
            result["skipped_invalid"] += 1
            result["errors"].append(f"line {line_no}: {why}")
            continue
        migrated_lines.append(json.dumps(normalized, ensure_ascii=False))

    result["migrated"] = len(migrated_lines)

    if dry_run:
        result["ok"] = True
        return result

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Atomic-ish: write to a temp file then rename. Avoids leaving a
        # half-written decision-log.jsonl if the process is interrupted.
        tmp_path = destination.with_suffix(destination.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            for line in migrated_lines:
                fh.write(line + "\n")
        tmp_path.replace(destination)
    except Exception as exc:
        result["errors"].append(f"failed to write destination: {exc!r}")
        result["ok"] = False
        return result

    result["ok"] = True
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=str(DEFAULT_REPO),
        help="Repository root (defaults to the skill directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing the destination file.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON result on stdout.",
    )
    args = parser.parse_args(argv)

    repo_path = Path(args.repo).resolve()
    try:
        result = migrate(repo_path, dry_run=args.dry_run)
    except Exception as exc:
        result = {"ok": False, "error": f"unexpected migration error: {exc!r}"}

    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))