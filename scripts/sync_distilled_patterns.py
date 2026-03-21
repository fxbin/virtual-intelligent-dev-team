#!/usr/bin/env python3
"""Rebuild distilled patterns from kept iteration rounds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def collect_kept_rounds(workspace: Path) -> list[dict[str, object]]:
    rounds: list[dict[str, object]] = []
    for state_path in sorted(workspace.glob("round-*/state.json")):
        state = load_json(state_path)
        if str(state.get("decision", "")) != "keep":
            continue
        rounds.append(state)
    return rounds


def summarize_side(summary: object) -> str:
    if not isinstance(summary, dict):
        return "not recorded"
    return (
        f"overall_passed={bool(summary.get('overall_passed', False))}, "
        f"evals={int(summary.get('evals_passed', 0))}/{int(summary.get('evals_total', 0))}"
    )


def render_patterns(rounds: list[dict[str, object]]) -> str:
    lines = [
        "# Distilled Patterns",
        "",
        "Use this only after a pattern survives evidence.",
        "",
    ]
    if not rounds:
        lines.extend(["- None yet.", ""])
        return "\n".join(lines)

    for state in rounds:
        round_id = str(state.get("round_id", "unknown"))
        objective = str(state.get("objective", ""))
        candidate = str(state.get("candidate", ""))
        owner = str(state.get("owner", ""))
        baseline_label = str(state.get("baseline_label", ""))
        reasons = state.get("decision_reason", [])
        if not isinstance(reasons, list):
            reasons = []
        comparison = state.get("comparison", {})
        baseline_summary = comparison.get("baseline", {}) if isinstance(comparison, dict) else {}
        candidate_summary = comparison.get("candidate", {}) if isinstance(comparison, dict) else {}
        lines.extend(
            [
                f"## {round_id}",
                "",
                f"- Objective: {objective}",
                f"- Owner: {owner or 'unknown'}",
                f"- Baseline label: {baseline_label or 'unknown'}",
                f"- Candidate: {candidate}",
                "- Evidence snapshot:",
                f"  - Baseline: {summarize_side(baseline_summary)}",
                f"  - Candidate: {summarize_side(candidate_summary)}",
                "- Evidence-backed rule:",
            ]
        )
        lines.extend([f"  - {reason}" for reason in reasons] or ["  - keep only with matching evidence"])
        lines.extend(
            [
                "- Reuse guardrail:",
                "  - Re-run benchmark comparison before treating this as a stable pattern.",
                "",
            ]
        )
    return "\n".join(lines)


def sync_patterns(workspace: Path) -> dict[str, object]:
    rounds = collect_kept_rounds(workspace=workspace)
    path = workspace / "distilled-patterns.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_patterns(rounds), encoding="utf-8")
    return {
        "workspace": str(workspace),
        "distilled_patterns": str(path),
        "kept_rounds": len(rounds),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild distilled patterns from kept rounds.")
    parser.add_argument("--workspace", default=".skill-iterations", help="Iteration workspace")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = sync_patterns(workspace=Path(args.workspace).resolve())
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
