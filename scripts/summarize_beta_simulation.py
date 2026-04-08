#!/usr/bin/env python3
"""Summarize a beta simulation run and optionally write a beta round report."""

from __future__ import annotations

import argparse
from collections import Counter
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


response_contract = load_module("virtual_team_summarize_beta_simulation_response_contract", RESPONSE_CONTRACT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_themes(themes: object) -> list[str]:
    if not isinstance(themes, list):
        return []
    return [str(item) for item in themes if str(item).strip() != ""]


def severity_label_for_session(session: dict[str, object]) -> str:
    if bool(session.get("critical_issue_detected")):
        return "P0"
    if bool(session.get("blocker_detected")):
        return "P1"
    if bool(session.get("high_severity_issue_detected")):
        return "P1"
    if not bool(session.get("task_completed")):
        return "P2"
    return "P3"


def proposed_action_for_session(session: dict[str, object]) -> str:
    themes = compact_themes(session.get("top_feedback_themes", []))
    if bool(session.get("critical_issue_detected")):
        return "freeze expansion, fix the critical path, and add a regression check"
    if bool(session.get("blocker_detected")):
        theme_text = themes[0] if themes else "the blocker path"
        return f"fix {theme_text} before rerunning this round"
    if bool(session.get("high_severity_issue_detected")):
        theme_text = themes[0] if themes else "the high-friction path"
        return f"simplify {theme_text} and rerun the affected scenario"
    return "monitor in the next round after minor UX tightening"


def build_breakdown(
    sessions: list[dict[str, object]],
    *,
    label_key: str,
) -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = {}
    for session in sessions:
        if not isinstance(session, dict):
            continue
        label = str(session.get(label_key, "")).strip()
        if label == "":
            continue
        bucket = buckets.setdefault(
            label,
            {
                "label": label,
                "session_count": 0,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 0,
                "session_ids": [],
                "top_feedback_themes": Counter(),
            },
        )
        bucket["session_count"] = int(bucket["session_count"]) + 1
        bucket["blocker_issue_count"] = int(bucket["blocker_issue_count"]) + (1 if bool(session.get("blocker_detected")) else 0)
        bucket["critical_issue_count"] = int(bucket["critical_issue_count"]) + (1 if bool(session.get("critical_issue_detected")) else 0)
        bucket["high_severity_issue_count"] = int(bucket["high_severity_issue_count"]) + (1 if bool(session.get("high_severity_issue_detected")) else 0)
        bucket["session_ids"].append(str(session.get("session_id", "")))
        for theme in compact_themes(session.get("top_feedback_themes", [])):
            bucket["top_feedback_themes"][theme] += 1

    results: list[dict[str, object]] = []
    for bucket in buckets.values():
        theme_counter = bucket["top_feedback_themes"]
        results.append(
            {
                "label": str(bucket["label"]),
                "session_count": int(bucket["session_count"]),
                "blocker_issue_count": int(bucket["blocker_issue_count"]),
                "critical_issue_count": int(bucket["critical_issue_count"]),
                "high_severity_issue_count": int(bucket["high_severity_issue_count"]),
                "session_ids": [str(item) for item in bucket["session_ids"]],
                "top_feedback_themes": [theme for theme, _count in theme_counter.most_common(5)],
            }
        )
    return sorted(
        results,
        key=lambda item: (
            -int(item["critical_issue_count"]),
            -int(item["blocker_issue_count"]),
            -int(item["high_severity_issue_count"]),
            item["label"],
        ),
    )


def update_feedback_ledger(
    *,
    feedback_ledger_out: Path,
    round_id: str,
    sessions: list[dict[str, object]],
) -> None:
    generated_header = "## Generated Entries"
    rows = [
        "| Round | User archetype | Scenario | Signal | Severity | Proposed action | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for session in sessions:
        if not isinstance(session, dict):
            continue
        severity = severity_label_for_session(session)
        signal = str(session.get("feedback_summary", "")).strip() or "simulation feedback captured"
        proposed_action = proposed_action_for_session(session)
        status = "monitor" if severity == "P3" else "open"
        rows.append(
            f"| {round_id} | {session.get('persona_name', '')} | {session.get('scenario_title', '')} | {signal} | {severity} | {proposed_action} | {status} |"
        )

    generated_section = "\n".join(
        [
            generated_header,
            "",
            "Rows below are regenerated from the latest simulation summary for this round.",
            "",
            *rows,
            "",
        ]
    )

    if feedback_ledger_out.exists():
        original = feedback_ledger_out.read_text(encoding="utf-8")
        marker = f"\n{generated_header}\n"
        if marker in original:
            base = original.split(marker, 1)[0].rstrip() + "\n\n"
        else:
            base = original.rstrip() + "\n\n"
    else:
        base = (
            "# Beta Feedback Ledger\n\n"
            "| Round | User archetype | Scenario | Signal | Severity | Proposed action | Status |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "\n"
            "## Severity Rules\n\n"
            "- `P0`: blocks completion or creates a trust-breaking failure\n"
            "- `P1`: major friction that materially harms the target task\n"
            "- `P2`: real issue but tolerable for the current beta round\n"
            "- `P3`: polish or follow-up signal\n\n"
        )
    feedback_ledger_out.parent.mkdir(parents=True, exist_ok=True)
    feedback_ledger_out.write_text(base + generated_section, encoding="utf-8")


def summarize_beta_simulation(
    *,
    run_path: Path,
    summary_out: Path | None = None,
    feedback_ledger_out: Path | None = None,
    round_report_out: Path | None = None,
) -> dict[str, object]:
    run_payload = load_json(run_path)
    response_contract.validate_beta_simulation_run(run_payload)
    sessions = run_payload.get("sessions", [])
    if not isinstance(sessions, list):
        sessions = []

    theme_counter = Counter(
        theme
        for session in sessions
        if isinstance(session, dict)
        for theme in session.get("top_feedback_themes", [])
        if isinstance(theme, str) and theme.strip() != ""
    )
    blocker_sessions = [
        session for session in sessions if isinstance(session, dict) and bool(session.get("blocker_detected"))
    ]
    blocker_breakdown = {
        "by_persona": build_breakdown(sessions, label_key="persona_name"),
        "by_scenario": build_breakdown(sessions, label_key="scenario_title"),
    }
    summary_payload = {
        "generated_at": now_iso(),
        "skill_name": "virtual-intelligent-dev-team",
        "source_run": str(run_path),
        "round_id": str(run_payload["round_id"]),
        "phase": str(run_payload["phase"]),
        "planned_sessions": int(run_payload["summary"]["planned_sessions"]),
        "completed_sessions": int(run_payload["summary"]["completed_sessions"]),
        "task_success_count": int(run_payload["summary"]["task_success_count"]),
        "blocker_issue_count": int(run_payload["summary"]["blocker_issue_count"]),
        "critical_issue_count": int(run_payload["summary"]["critical_issue_count"]),
        "high_severity_issue_count": int(run_payload["summary"]["high_severity_issue_count"]),
        "top_feedback_themes": [theme for theme, _count in theme_counter.most_common(5)],
        "recommendation": (
            "hold"
            if int(run_payload["summary"]["blocker_issue_count"]) > 0
            or int(run_payload["summary"]["critical_issue_count"]) > 0
            else "advance"
        ),
        "blocker_breakdown": blocker_breakdown,
        "blocker_sessions": [
            {
                "session_id": str(item["session_id"]),
                "persona_name": str(item["persona_name"]),
                "scenario_title": str(item["scenario_title"]),
                "feedback_summary": str(item["feedback_summary"]),
            }
            for item in blocker_sessions
        ],
    }

    if summary_out is None:
        summary_out = run_path.parent / "beta-simulation-summary.json"
    write_json(summary_out, summary_payload)

    if feedback_ledger_out is not None:
        update_feedback_ledger(
            feedback_ledger_out=feedback_ledger_out,
            round_id=str(run_payload["round_id"]),
            sessions=sessions,
        )

    if round_report_out is not None:
        round_report = {
            "schema_version": "beta-round-report/v1",
            "round_id": str(run_payload["round_id"]),
            "phase": str(run_payload["phase"]),
            "goal": str(run_payload["objective"]),
            "participant_mode": "simulated users",
            "planned_sample_size": int(run_payload["summary"]["planned_sessions"]),
            "completed_sessions": int(run_payload["summary"]["completed_sessions"]),
            "task_success_count": int(run_payload["summary"]["task_success_count"]),
            "blocker_issue_count": int(run_payload["summary"]["blocker_issue_count"]),
            "critical_issue_count": int(run_payload["summary"]["critical_issue_count"]),
            "high_severity_issue_count": int(run_payload["summary"]["high_severity_issue_count"]),
            "top_feedback_themes": [theme for theme, _count in theme_counter.most_common(5)],
            "exit_criteria": "Advance only when simulation traces show the main workflow is understandable and blocker themes are closed.",
            "gate_thresholds": {
                "min_completed_sessions": max(int(run_payload["summary"]["planned_sessions"]) - 1, 1),
                "min_success_rate": 0.8,
                "max_blocker_issue_count": 0,
                "max_critical_issue_count": 0,
            },
            "source_simulation_run": str(run_path),
            "evidence_artifacts": {
                "simulation_run_json": str(run_path),
                "simulation_run_markdown": str(run_payload["markdown_report"]),
                "simulation_summary_json": str(summary_out),
                "feedback_ledger_markdown": str(feedback_ledger_out) if feedback_ledger_out is not None else "",
            },
            "blocker_breakdown": blocker_breakdown,
            "notes": (
                "Derived from beta simulation evidence. "
                f"Recommendation: {summary_payload['recommendation']}. "
                f"Primary blocker sessions: {len(blocker_sessions)}."
            ),
        }
        response_contract.validate_beta_round_report(round_report)
        write_json(round_report_out, round_report)

    return {
        "ok": True,
        "summary_json": str(summary_out),
        "feedback_ledger_out": str(feedback_ledger_out) if feedback_ledger_out is not None else None,
        "round_report_out": str(round_report_out) if round_report_out is not None else None,
        "recommendation": summary_payload["recommendation"],
        "top_feedback_themes": summary_payload["top_feedback_themes"],
        "blocker_breakdown": blocker_breakdown,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a beta simulation run.")
    parser.add_argument("--run", required=True, help="Path to beta simulation run JSON.")
    parser.add_argument("--summary-out", help="Optional output path for summary JSON.")
    parser.add_argument("--feedback-ledger-out", help="Optional output path for the generated feedback ledger markdown.")
    parser.add_argument("--round-report-out", help="Optional output path for beta round report JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = summarize_beta_simulation(
        run_path=Path(args.run).resolve(),
        summary_out=Path(args.summary_out).resolve() if args.summary_out else None,
        feedback_ledger_out=Path(args.feedback_ledger_out).resolve() if args.feedback_ledger_out else None,
        round_report_out=Path(args.round_report_out).resolve() if args.round_report_out else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
