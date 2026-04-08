#!/usr/bin/env python3
"""Initialize a machine-readable beta round report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = SKILL_DIR / "assets" / "beta-round-report-template.json"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_init_beta_round_response_contract", RESPONSE_CONTRACT_SCRIPT)


def load_template() -> dict[str, object]:
    with TEMPLATE_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("beta round report template must be a JSON object")
    return payload


def init_beta_round_report(
    *,
    root: Path,
    round_id: str,
    phase: str,
    sample_size: int,
    participant_mode: str,
    goal: str,
    exit_criteria: str,
    overwrite: bool = False,
) -> dict[str, object]:
    payload = load_template()
    payload["round_id"] = round_id
    payload["phase"] = phase
    payload["planned_sample_size"] = sample_size
    payload["participant_mode"] = participant_mode
    payload["goal"] = goal
    payload["exit_criteria"] = exit_criteria
    response_contract.validate_beta_round_report(payload)

    target = root / ".skill-beta" / "reports" / f"{round_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        status = "skipped"
    else:
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        status = "updated" if target.exists() and overwrite else "created"
    return {
        "ok": True,
        "status": status,
        "report_path": str(target.relative_to(root)),
        "round_id": round_id,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a beta round report JSON.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--round-id", required=True, help="Round id, for example round-1.")
    parser.add_argument("--phase", required=True, help="Round phase label.")
    parser.add_argument("--sample-size", required=True, type=int, help="Planned sample size.")
    parser.add_argument("--participant-mode", required=True, help="Participant mode.")
    parser.add_argument("--goal", required=True, help="Round goal.")
    parser.add_argument("--exit-criteria", required=True, help="Round exit criteria.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing report.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_beta_round_report(
        root=Path(args.root).resolve(),
        round_id=args.round_id,
        phase=args.phase,
        sample_size=args.sample_size,
        participant_mode=args.participant_mode,
        goal=args.goal,
        exit_criteria=args.exit_criteria,
        overwrite=args.overwrite,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
