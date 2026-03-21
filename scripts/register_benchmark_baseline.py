#!/usr/bin/env python3
"""Register a benchmark report as a reusable local baseline."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import shutil
from pathlib import Path


LABEL_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def summarize_report(payload: dict[str, object]) -> dict[str, object]:
    summary = payload.get("summary", {})
    eval_run = payload.get("eval_run", {})
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(eval_run, dict):
        eval_run = {}
    return {
        "overall_passed": bool(summary.get("overall_passed", False)),
        "evals_passed": int(eval_run.get("passed", 0)),
        "evals_total": int(eval_run.get("total", 0)),
    }


def load_registry(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"baselines": []}
    return load_json(path)


def register_baseline(
    workspace: Path,
    label: str,
    report_path: Path,
    notes: str = "",
) -> dict[str, object]:
    if not LABEL_PATTERN.fullmatch(label):
        raise RuntimeError("baseline label must match [A-Za-z0-9._-]+")

    payload = load_json(report_path)
    baselines_dir = workspace / "baselines"
    registry_path = baselines_dir / "registry.json"
    baseline_dir = baselines_dir / label
    baseline_dir.mkdir(parents=True, exist_ok=True)

    stored_report = baseline_dir / "benchmark-results.json"
    shutil.copyfile(report_path, stored_report)

    registry = load_registry(registry_path)
    items = registry.get("baselines", [])
    if not isinstance(items, list):
        items = []

    entry = {
        "label": label,
        "registered_at": datetime.now().isoformat(timespec="seconds"),
        "source_report": str(report_path),
        "stored_report": str(stored_report),
        "notes": notes,
        "summary": summarize_report(payload),
    }

    updated: list[dict[str, object]] = []
    replaced = False
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("label") == label:
            updated.append(entry)
            replaced = True
        else:
            updated.append(item)
    if not replaced:
        updated.append(entry)

    registry["baselines"] = updated
    write_json(registry_path, registry)

    return {
        "label": label,
        "registry": str(registry_path),
        "stored_report": str(stored_report),
        "summary": entry["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a local benchmark baseline.")
    parser.add_argument("--workspace", default=".skill-iterations", help="Iteration workspace")
    parser.add_argument("--label", required=True, help="Baseline label")
    parser.add_argument("--report", required=True, help="Path to benchmark-results.json")
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = register_baseline(
        workspace=Path(args.workspace).resolve(),
        label=args.label,
        report_path=Path(args.report).resolve(),
        notes=args.notes,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
