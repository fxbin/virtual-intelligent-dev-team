#!/usr/bin/env python3
"""Initialize iteration workspace artifacts for one bounded-optimization round."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_line(content: str, prefix: str, value: str) -> str:
    lines = content.splitlines()
    updated: list[str] = []
    for line in lines:
        if line.startswith(prefix):
            updated.append(f"{prefix} {value}".rstrip())
        else:
            updated.append(line)
    return "\n".join(updated) + "\n"


def prepare_ledger(round_id: str, objective: str, baseline: str, owner: str) -> str:
    content = read_text(ASSETS_DIR / "iteration-ledger-template.md")
    content = replace_line(content, "- Round ID:", round_id)
    content = replace_line(content, "- Owner:", owner)
    content = replace_line(content, "- Objective:", objective)
    content = replace_line(content, "- Baseline:", baseline)
    return content


def prepare_reflection(candidate: str) -> str:
    content = read_text(ASSETS_DIR / "round-reflection-template.md")
    return replace_line(content, "- Candidate:", candidate)


def prepare_round_memory(round_id: str, objective: str, baseline: str, owner: str, candidate: str) -> str:
    content = read_text(ASSETS_DIR / "round-memory-template.md")
    content = replace_line(content, "- Round ID:", round_id)
    content = replace_line(content, "- Owner:", owner)
    content = replace_line(content, "- Objective:", objective)
    content = replace_line(content, "- Baseline:", baseline)
    content = replace_line(content, "- Candidate:", candidate)
    return content


def prepare_self_feedback(candidate: str) -> str:
    content = read_text(ASSETS_DIR / "self-feedback-template.md")
    return replace_line(content, "- One variable to change next:", candidate)


def initialize_round(
    workspace: Path,
    round_id: str,
    objective: str,
    baseline: str,
    owner: str,
    candidate: str,
) -> dict[str, str]:
    round_dir = workspace / round_id
    round_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = round_dir / "iteration-ledger.md"
    reflection_path = round_dir / "round-reflection.md"
    round_memory_path = round_dir / "round-memory.md"
    self_feedback_path = round_dir / "self-feedback.md"
    distilled_path = workspace / "distilled-patterns.md"

    write_text(
        ledger_path,
        prepare_ledger(
            round_id=round_id,
            objective=objective,
            baseline=baseline,
            owner=owner,
        ),
    )
    write_text(reflection_path, prepare_reflection(candidate=candidate))
    write_text(
        round_memory_path,
        prepare_round_memory(
            round_id=round_id,
            objective=objective,
            baseline=baseline,
            owner=owner,
            candidate=candidate,
        ),
    )
    write_text(self_feedback_path, prepare_self_feedback(candidate=candidate))
    if not distilled_path.exists():
        write_text(distilled_path, read_text(ASSETS_DIR / "distilled-patterns-template.md"))

    return {
        "workspace": str(workspace),
        "round_dir": str(round_dir),
        "ledger": str(ledger_path),
        "reflection": str(reflection_path),
        "round_memory": str(round_memory_path),
        "self_feedback": str(self_feedback_path),
        "distilled_patterns": str(distilled_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize bounded-iteration round assets.")
    parser.add_argument("--workspace", default=".skill-iterations", help="Workspace directory")
    parser.add_argument("--round-id", required=True, help="Round identifier")
    parser.add_argument("--objective", default="<goal>", help="Round objective")
    parser.add_argument("--baseline", default="<baseline>", help="Baseline label")
    parser.add_argument("--owner", default="Technical Trinity", help="Lead owner")
    parser.add_argument("--candidate", default="<candidate-change>", help="Candidate change summary")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = initialize_round(
        workspace=Path(args.workspace).resolve(),
        round_id=args.round_id,
        objective=args.objective,
        baseline=args.baseline,
        owner=args.owner,
        candidate=args.candidate,
    )
    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
