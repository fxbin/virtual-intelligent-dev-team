#!/usr/bin/env python3
"""Evaluate a beta round report and emit a gate decision."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_evaluate_beta_round_response_contract", RESPONSE_CONTRACT_SCRIPT)


def load_report(report_path: Path) -> dict[str, object]:
    with report_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("beta round report must be a JSON object")
    response_contract.validate_beta_round_report(payload)
    return payload


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate_beta_round(*, report_path: Path, output_dir: Path | None = None) -> dict[str, object]:
    report = load_report(report_path)
    round_id = str(report["round_id"])
    thresholds = report.get("gate_thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}

    planned_sample_size = int(report.get("planned_sample_size", 0))
    completed_sessions = int(report.get("completed_sessions", 0))
    task_success_count = int(report.get("task_success_count", 0))
    blocker_issue_count = int(report.get("blocker_issue_count", 0))
    critical_issue_count = int(report.get("critical_issue_count", 0))
    high_severity_issue_count = int(report.get("high_severity_issue_count", 0))
    top_feedback_themes = report.get("top_feedback_themes", [])
    if not isinstance(top_feedback_themes, list):
        top_feedback_themes = []
    blocker_breakdown = report.get("blocker_breakdown")
    if not isinstance(blocker_breakdown, dict):
        blocker_breakdown = None
    success_rate = (
        float(task_success_count) / float(completed_sessions) if completed_sessions > 0 else 0.0
    )

    min_completed_sessions = int(thresholds.get("min_completed_sessions", 1))
    min_success_rate = float(thresholds.get("min_success_rate", 0.8))
    max_blocker_issue_count = int(thresholds.get("max_blocker_issue_count", 0))
    max_critical_issue_count = int(thresholds.get("max_critical_issue_count", 0))

    if critical_issue_count > max_critical_issue_count:
        decision = "escalate"
        reason = "Critical issues exceed the allowed threshold for this round."
        follow_up = {
            "next_action": "freeze expansion, escalate into technical governance, and resolve critical issues before another beta round",
            "continue_beta": False,
            "release_governance_recommended": True,
            "next_round_recommended": None,
        }
    elif (
        completed_sessions < min_completed_sessions
        or success_rate < min_success_rate
        or blocker_issue_count > max_blocker_issue_count
    ):
        decision = "hold"
        reason = "This round has not yet cleared the minimum sample, success-rate, or blocker thresholds."
        follow_up = {
            "next_action": "hold expansion, fix blocker themes, and rerun the current beta round",
            "continue_beta": False,
            "release_governance_recommended": False,
            "next_round_recommended": round_id,
        }
    else:
        decision = "advance"
        reason = "This round meets the sample, success-rate, and blocker thresholds required to expand."
        next_round_recommended = None
        if round_id.startswith("round-"):
            suffix = round_id.split("-", 1)[1]
            if suffix.isdigit():
                next_round_recommended = f"round-{int(suffix) + 1}"
        follow_up = {
            "next_action": "promote the learnings, initialize the next round report, and expand the cohort only within the planned beta ramp",
            "continue_beta": True,
            "release_governance_recommended": False,
            "next_round_recommended": next_round_recommended,
        }

    result = {
        "generated_at": now_iso(),
        "skill_name": "virtual-intelligent-dev-team",
        "ok": decision == "advance",
        "decision": decision,
        "reason": reason,
        "round_id": round_id,
        "report_path": str(report_path),
        "observed": {
            "planned_sample_size": planned_sample_size,
            "completed_sessions": completed_sessions,
            "success_rate": round(success_rate, 4),
            "blocker_issue_count": blocker_issue_count,
            "critical_issue_count": critical_issue_count,
            "high_severity_issue_count": high_severity_issue_count,
            "top_feedback_themes": [str(item) for item in top_feedback_themes],
        },
        "thresholds": {
            "min_completed_sessions": min_completed_sessions,
            "min_success_rate": min_success_rate,
            "max_blocker_issue_count": max_blocker_issue_count,
            "max_critical_issue_count": max_critical_issue_count,
        },
        "follow_up": follow_up,
        "json_report": "",
        "markdown_report": "",
    }
    if blocker_breakdown is not None:
        result["blocker_breakdown"] = blocker_breakdown

    if output_dir is None:
        output_dir = report_path.parent.parent / "round-decisions" / round_id
    output_dir.mkdir(parents=True, exist_ok=True)
    json_report = output_dir / "beta-round-gate-result.json"
    markdown_report = output_dir / "beta-round-gate-report.md"
    result["json_report"] = str(json_report)
    result["markdown_report"] = str(markdown_report)
    response_contract.validate_beta_round_gate_result(result)

    json_report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# Beta Round Gate: {round_id}",
        "",
        f"- Decision: {decision}",
        f"- Reason: {reason}",
        f"- Completed sessions: {completed_sessions}/{planned_sample_size}",
        f"- Success rate: {round(success_rate, 4)}",
        f"- Blocker issues: {blocker_issue_count}",
        f"- Critical issues: {critical_issue_count}",
        f"- High severity issues: {high_severity_issue_count}",
        f"- Next action: {follow_up['next_action']}",
        f"- Next round: {follow_up['next_round_recommended'] or 'n/a'}",
    ]
    if blocker_breakdown is not None:
        by_persona = blocker_breakdown.get("by_persona", [])
        by_scenario = blocker_breakdown.get("by_scenario", [])
        if isinstance(by_persona, list) and by_persona:
            lines.extend(["", "## Blocker Breakdown By Persona", ""])
            for item in by_persona[:5]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {item.get('label')}: sessions={item.get('session_count')}, blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, high={item.get('high_severity_issue_count')}, themes={', '.join(item.get('top_feedback_themes', []))}"
                )
        if isinstance(by_scenario, list) and by_scenario:
            lines.extend(["", "## Blocker Breakdown By Scenario", ""])
            for item in by_scenario[:5]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {item.get('label')}: sessions={item.get('session_count')}, blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, high={item.get('high_severity_issue_count')}, themes={', '.join(item.get('top_feedback_themes', []))}"
                )
    markdown = "\n".join(lines) + "\n"
    markdown_report.write_text(markdown, encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a beta round report and emit a gate decision.")
    parser.add_argument("--report", required=True, help="Path to beta round report JSON.")
    parser.add_argument("--output-dir", help="Optional output directory for gate artifacts.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate_beta_round(
        report_path=Path(args.report).resolve(),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
