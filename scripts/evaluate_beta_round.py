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


def infer_previous_round_id(round_id: str) -> str | None:
    prefix = "round-"
    if not round_id.startswith(prefix):
        return None
    suffix = round_id[len(prefix) :]
    if not suffix.isdigit():
        return None
    value = int(suffix)
    if value <= 0:
        return None
    return f"{prefix}{value - 1}"


def load_fixture_diff(diff_path: Path) -> dict[str, object]:
    with diff_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("beta simulation diff must be a JSON object")
    response_contract.validate_beta_simulation_diff(payload)
    return payload


def load_ramp_plan(plan_path: Path) -> dict[str, object]:
    with plan_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("beta ramp plan must be a JSON object")
    response_contract.validate_beta_ramp_plan(payload)
    return payload


def load_manifest(manifest_path: Path) -> dict[str, object]:
    with manifest_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("beta simulation manifest must be a JSON object")
    response_contract.validate_beta_simulation_manifest(payload)
    return payload


def resolve_report_relative_path(report_path: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    report_relative = (report_path.parent / path).resolve()
    if report_relative.exists():
        return report_relative
    return path.resolve()


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
    evidence_artifacts = report.get("evidence_artifacts")
    if not isinstance(evidence_artifacts, dict):
        evidence_artifacts = {}
    success_rate = (
        float(task_success_count) / float(completed_sessions) if completed_sessions > 0 else 0.0
    )

    min_completed_sessions = int(thresholds.get("min_completed_sessions", 1))
    min_success_rate = float(thresholds.get("min_success_rate", 0.8))
    max_blocker_issue_count = int(thresholds.get("max_blocker_issue_count", 0))
    max_critical_issue_count = int(thresholds.get("max_critical_issue_count", 0))
    previous_round_id = infer_previous_round_id(round_id)
    diff_required_for_round = previous_round_id is not None
    ramp_required_for_round = previous_round_id is not None
    fixture_manifest_json_raw = str(evidence_artifacts.get("fixture_manifest_json", "")).strip()
    ramp_plan_json_raw = str(evidence_artifacts.get("ramp_plan_json", "")).strip()
    observed_persona_ids: list[str] = []
    if fixture_manifest_json_raw != "":
        manifest_path = resolve_report_relative_path(report_path, fixture_manifest_json_raw)
        if manifest_path.exists():
            manifest_payload = load_manifest(manifest_path)
            sessions = manifest_payload.get("sessions", [])
            if isinstance(sessions, list):
                observed_persona_ids = sorted(
                    {
                        str(item.get("persona_id", "")).strip()
                        for item in sessions
                        if isinstance(item, dict) and str(item.get("persona_id", "")).strip() != ""
                    }
                )
    ramp_gate = {
        "status": "not-required",
        "required_for_round": ramp_required_for_round,
        "reason": "Ramp-plan evidence is not required for the first beta round.",
        "ramp_plan_json": ramp_plan_json_raw or None,
        "expected_sample_size": None,
        "observed_planned_sample_size": planned_sample_size,
        "expected_participant_mode": None,
        "observed_participant_mode": str(report.get("participant_mode", "")),
        "expected_phase": None,
        "observed_phase": str(report.get("phase", "")),
        "expected_archetypes": [],
        "observed_persona_ids": observed_persona_ids,
    }
    if ramp_plan_json_raw != "":
        ramp_payload = load_ramp_plan(resolve_report_relative_path(report_path, ramp_plan_json_raw))
        rounds = ramp_payload.get("rounds", [])
        expected_round = None
        if isinstance(rounds, list):
            expected_round = next(
                (
                    item
                    for item in rounds
                    if isinstance(item, dict) and str(item.get("round_id", "")).strip() == round_id
                ),
                None,
            )
        if expected_round is None:
            ramp_gate.update(
                {
                    "status": "missing-round",
                    "reason": "Ramp plan does not define the current round.",
                }
            )
        else:
            expected_sample_size = int(expected_round.get("sample_size", 0))
            expected_participant_mode = str(expected_round.get("participant_mode", "")).strip()
            expected_phase = str(expected_round.get("phase", "")).strip()
            expected_archetypes = [
                str(item)
                for item in expected_round.get("archetypes", [])
                if str(item).strip() != ""
            ] if isinstance(expected_round.get("archetypes", []), list) else []
            ramp_gate.update(
                {
                    "ramp_plan_json": ramp_plan_json_raw,
                    "expected_sample_size": expected_sample_size,
                    "expected_participant_mode": expected_participant_mode,
                    "expected_phase": expected_phase,
                    "expected_archetypes": expected_archetypes,
                }
            )
            mismatches: list[str] = []
            if expected_sample_size != planned_sample_size:
                mismatches.append("planned sample size")
            if expected_participant_mode.casefold() != str(report.get("participant_mode", "")).strip().casefold():
                mismatches.append("participant mode")
            if expected_phase.casefold() != str(report.get("phase", "")).strip().casefold():
                mismatches.append("phase")
            if mismatches:
                ramp_gate.update(
                    {
                        "status": "mismatch",
                        "reason": "Ramp plan does not match the current round report for " + ", ".join(mismatches) + ".",
                    }
                )
            else:
                ramp_gate.update(
                    {
                        "status": "passed",
                        "reason": "Ramp plan matches the current round report.",
                    }
                )
    elif ramp_required_for_round:
        ramp_gate.update(
            {
                "status": "missing",
                "reason": "Round expansion requires a machine-readable ramp plan before the gate can advance.",
            }
        )
    fixture_diff_json_raw = str(evidence_artifacts.get("fixture_diff_json", "")).strip()
    fixture_diff_markdown_raw = str(evidence_artifacts.get("fixture_diff_markdown", "")).strip()
    diff_gate = {
        "status": "not-required",
        "required_for_round": diff_required_for_round,
        "review_required": False,
        "expansion_ok": True,
        "reason": "Diff evidence is not required for the first beta round.",
        "fixture_diff_json": fixture_diff_json_raw or None,
        "fixture_diff_markdown": fixture_diff_markdown_raw or None,
        "coverage_shift_summary": None,
        "risk_notes": [],
    }
    if diff_required_for_round:
        if fixture_diff_json_raw == "":
            diff_gate.update(
                {
                    "status": "missing",
                    "expansion_ok": False,
                    "reason": "Round expansion requires a round-to-round fixture diff before the gate can advance.",
                }
            )
        else:
            diff_payload = load_fixture_diff(resolve_report_relative_path(report_path, fixture_diff_json_raw))
            diff_review_required = bool(diff_payload.get("review_required"))
            diff_expansion_ok = bool(diff_payload.get("expansion_ok"))
            diff_gate.update(
                {
                    "status": "review-required" if diff_review_required or not diff_expansion_ok else "passed",
                    "review_required": diff_review_required,
                    "expansion_ok": diff_expansion_ok,
                    "reason": (
                        "Fixture drift requires explicit review before expansion."
                        if diff_review_required or not diff_expansion_ok
                        else "Fixture diff cleared expansion review."
                    ),
                    "fixture_diff_markdown": str(diff_payload.get("markdown_report") or fixture_diff_markdown_raw or "") or None,
                    "coverage_shift_summary": diff_payload.get("coverage_shift_summary"),
                    "risk_notes": [str(item) for item in diff_payload.get("risk_notes", []) if str(item).strip()],
                }
            )

    if critical_issue_count > max_critical_issue_count:
        decision = "escalate"
        reason = "Critical issues exceed the allowed threshold for this round."
        follow_up = {
            "next_action": "freeze expansion, escalate into technical governance, and resolve critical issues before another beta round",
            "continue_beta": False,
            "release_governance_recommended": True,
            "next_round_recommended": None,
        }
    elif ramp_required_for_round and ramp_gate["status"] in {"missing", "missing-round", "mismatch"}:
        decision = "hold"
        reason = str(ramp_gate["reason"])
        follow_up = {
            "next_action": "hold expansion, reconcile the round report with the ramp plan, and rerun the gate",
            "continue_beta": False,
            "release_governance_recommended": False,
            "next_round_recommended": round_id,
        }
    elif diff_required_for_round and diff_gate["status"] in {"missing", "review-required"}:
        decision = "hold"
        reason = str(diff_gate["reason"])
        follow_up = {
            "next_action": "hold expansion, review the fixture diff, and resolve coverage drift before another beta round",
            "continue_beta": False,
            "release_governance_recommended": False,
            "next_round_recommended": round_id,
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
        "ramp_gate": ramp_gate,
        "diff_gate": diff_gate,
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
        f"- Ramp gate: {ramp_gate['status']}",
        f"- Ramp reason: {ramp_gate['reason']}",
        f"- Diff gate: {diff_gate['status']}",
        f"- Diff reason: {diff_gate['reason']}",
        f"- Next action: {follow_up['next_action']}",
        f"- Next round: {follow_up['next_round_recommended'] or 'n/a'}",
    ]
    if ramp_gate["status"] != "not-required":
        lines.extend(
            [
                "",
                "## Ramp Plan Gate",
                "",
                f"- Expected sample size: {ramp_gate['expected_sample_size']}",
                f"- Observed planned sample size: {ramp_gate['observed_planned_sample_size']}",
                f"- Expected participant mode: {ramp_gate['expected_participant_mode'] or 'n/a'}",
                f"- Observed participant mode: {ramp_gate['observed_participant_mode']}",
                f"- Expected phase: {ramp_gate['expected_phase'] or 'n/a'}",
                f"- Observed phase: {ramp_gate['observed_phase']}",
                f"- Expected archetypes: {', '.join(ramp_gate['expected_archetypes']) if ramp_gate['expected_archetypes'] else 'n/a'}",
                f"- Observed persona ids: {', '.join(ramp_gate['observed_persona_ids']) if ramp_gate['observed_persona_ids'] else 'n/a'}",
            ]
        )
    if isinstance(diff_gate.get("coverage_shift_summary"), dict):
        coverage_shift = diff_gate["coverage_shift_summary"]
        lines.extend(
            [
                "",
                "## Fixture Diff Gate",
                "",
                f"- Expansion mode: {coverage_shift.get('expansion_mode')}",
                f"- New session matrix count: {coverage_shift.get('new_session_matrix_count')}",
            ]
        )
        risk_notes = diff_gate.get("risk_notes", [])
        if isinstance(risk_notes, list) and risk_notes:
            lines.append("")
            lines.append("### Diff Risk Notes")
            lines.append("")
            for item in risk_notes:
                lines.append(f"- {item}")
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
