#!/usr/bin/env python3
"""Promote a kept iteration round into a new local baseline."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REGISTER_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline_registry = load_module("virtual_team_promote_baseline_registry", REGISTER_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    return baseline_registry.load_json(path)


def promote_round(workspace: Path, round_id: str, label: str, notes: str = "") -> dict[str, object]:
    round_dir = workspace / round_id
    state_path = round_dir / "state.json"
    if not state_path.exists():
        raise RuntimeError(f"round state not found: {state_path}")

    state = load_json(state_path)
    decision = str(state.get("decision", ""))
    if decision != "keep":
        raise RuntimeError(f"round {round_id} is not eligible for promotion: decision={decision}")

    candidate_report = state.get("candidate_report")
    if not isinstance(candidate_report, str) or candidate_report.strip() == "":
        raise RuntimeError(f"round {round_id} has no candidate report")

    result = baseline_registry.register_baseline(
        workspace=workspace,
        label=label,
        report_path=Path(candidate_report).resolve(),
        notes=notes or f"promoted from {round_id}",
    )
    result["round_id"] = round_id
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a kept iteration round to a baseline.")
    parser.add_argument("--workspace", default=".skill-iterations", help="Iteration workspace")
    parser.add_argument("--round-id", required=True, help="Round identifier")
    parser.add_argument("--label", required=True, help="Baseline label to promote into")
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = promote_round(
        workspace=Path(args.workspace).resolve(),
        round_id=args.round_id,
        label=args.label,
        notes=args.notes,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
