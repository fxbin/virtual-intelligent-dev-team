#!/usr/bin/env python3
"""Evaluate a beta round report and emit a gate decision."""

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


def load_cohort_plan(plan_path: Path) -> dict[str, object]:
    with plan_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("beta cohort plan must be a JSON object")
    response_contract.validate_beta_cohort_plan(payload)
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


def compact_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip() != ""]


def repo_root_from_report(report_path: Path) -> Path:
    if report_path.parent.name == "reports" and report_path.parent.parent.name == ".skill-beta":
        return report_path.parent.parent.parent
    return report_path.parent


def replace_or_append_section(document: str, heading: str, section_body: str) -> str:
    marker = f"\n{heading}\n"
    content = document.rstrip() + "\n"
    if marker not in content:
        return content + "\n" + heading + "\n\n" + section_body.rstrip() + "\n"
    before, after = content.split(marker, 1)
    next_heading_index = after.find("\n## ")
    if next_heading_index == -1:
        return before.rstrip() + "\n\n" + heading + "\n\n" + section_body.rstrip() + "\n"
    remainder = after[next_heading_index:]
    return before.rstrip() + "\n\n" + heading + "\n\n" + section_body.rstrip() + remainder


def writeback_section_body(
    *,
    round_id: str,
    decision: str,
    reason: str,
    blockers: list[dict[str, str]],
    blocker_breakdown: dict[str, object] | None,
    brief_json: str,
) -> str:
    lines = [
        f"- Round: `{round_id}`",
        f"- Decision: `{decision}`",
        f"- Reason: {reason}",
        f"- Remediation brief: `{brief_json}`",
        "",
        "### Gate Blockers",
        "",
    ]
    for blocker in blockers:
        lines.extend(
            [
                f"- `{blocker['id']}`: {blocker['label']}",
                f"  - Objective hint: {blocker['objective_hint']}",
                f"  - Evidence required: `{blocker['evidence_required']}`",
            ]
        )
    if blocker_breakdown is not None:
        by_persona = blocker_breakdown.get("by_persona", [])
        by_scenario = blocker_breakdown.get("by_scenario", [])
        if isinstance(by_persona, list) and by_persona:
            lines.extend(["", "### Persona Hotspots", ""])
            for item in by_persona[:5]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {item.get('label')}: blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, themes={', '.join(compact_string_list(item.get('top_feedback_themes')))}"
                )
        if isinstance(by_scenario, list) and by_scenario:
            lines.extend(["", "### Scenario Hotspots", ""])
            for item in by_scenario[:5]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {item.get('label')}: blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, themes={', '.join(compact_string_list(item.get('top_feedback_themes')))}"
                )
    return "\n".join(lines)


def sync_workspace_writebacks(
    *,
    repo_root: Path,
    output_dir: Path,
    round_id: str,
    decision: str,
    reason: str,
    blockers: list[dict[str, str]],
    blocker_breakdown: dict[str, object] | None,
    brief_json: str,
    release_governance_recommended: bool,
) -> list[str]:
    section_body = writeback_section_body(
        round_id=round_id,
        decision=decision,
        reason=reason,
        blockers=blockers,
        blocker_breakdown=blocker_breakdown,
        brief_json=brief_json,
    )
    resume_artifacts: list[str] = []

    product_writeback = output_dir / "product-writeback.md"
    product_writeback.write_text("# Product Writeback\n\n" + section_body + "\n", encoding="utf-8")
    resume_artifacts.append(str(product_writeback))

    product_targets = [
        repo_root / ".skill-product" / "current-slice.md",
        repo_root / ".skill-product" / "acceptance-criteria.md",
        repo_root / ".skill-product" / "contract-questions.md",
    ]
    for target in product_targets:
        if not target.exists():
            continue
        updated = replace_or_append_section(
            target.read_text(encoding="utf-8"),
            "## Beta Gate Writeback",
            section_body,
        )
        target.write_text(updated, encoding="utf-8")
        resume_artifacts.append(str(target))

    governance_writeback = output_dir / "governance-writeback.md"
    governance_lines = [
        "# Governance Writeback",
        "",
        section_body,
    ]
    if not release_governance_recommended:
        governance_lines.extend(["", "Governance escalation is not required for this round yet."])
    governance_writeback.write_text("\n".join(governance_lines) + "\n", encoding="utf-8")
    resume_artifacts.append(str(governance_writeback))

    if release_governance_recommended:
        governance_targets = [
            repo_root / ".skill-governance" / "change-plan.md",
            repo_root / ".skill-governance" / "release-checklist.md",
        ]
        for target in governance_targets:
            if not target.exists():
                continue
            updated = replace_or_append_section(
                target.read_text(encoding="utf-8"),
                "## Beta Gate Escalation Writeback",
                section_body,
            )
            target.write_text(updated, encoding="utf-8")
            resume_artifacts.append(str(target))

    return resume_artifacts


def build_blocker(
    *,
    blocker_id: str,
    label: str,
    objective_hint: str,
    evidence_required: str,
) -> dict[str, str]:
    return {
        "id": blocker_id,
        "label": label,
        "objective_hint": objective_hint,
        "evidence_required": evidence_required,
    }


def build_beta_gate_blockers(
    *,
    decision: str,
    reason: str,
    round_id: str,
    completed_sessions: int,
    min_completed_sessions: int,
    success_rate: float,
    min_success_rate: float,
    blocker_issue_count: int,
    max_blocker_issue_count: int,
    cohort_gate: dict[str, object],
    ramp_gate: dict[str, object],
    diff_gate: dict[str, object],
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    gate_command = f"python scripts/evaluate_beta_round.py --report .skill-beta/reports/{round_id}.json --pretty"
    simulation_command = f"python scripts/run_beta_simulation.py --config .skill-beta/simulation-configs/{round_id}.json --pretty"

    if decision == "escalate":
        blockers.append(
            build_blocker(
                blocker_id="critical-issues",
                label="critical issues exceeded the allowed threshold",
                objective_hint="freeze cohort expansion, enter technical governance, and resolve the critical path before reopening beta",
                evidence_required=gate_command,
            )
        )

    if str(cohort_gate.get("status")) in {"missing", "missing-round", "mismatch"}:
        blockers.append(
            build_blocker(
                blocker_id=f"cohort-plan-{str(cohort_gate.get('status'))}",
                label=str(cohort_gate.get("reason", "cohort plan drift detected")),
                objective_hint="reconcile the machine-readable cohort plan with the resolved fixture manifest before the next beta rerun",
                evidence_required=gate_command,
            )
        )

    if str(ramp_gate.get("status")) in {"missing", "missing-round", "mismatch"}:
        blockers.append(
            build_blocker(
                blocker_id=f"ramp-plan-{str(ramp_gate.get('status'))}",
                label=str(ramp_gate.get("reason", "ramp plan drift detected")),
                objective_hint="repair the ramp plan so phase, participant mode, and sample size match the current round before expansion",
                evidence_required=gate_command,
            )
        )

    if str(diff_gate.get("status")) in {"missing", "review-required"}:
        blockers.append(
            build_blocker(
                blocker_id=f"fixture-diff-{str(diff_gate.get('status'))}",
                label=str(diff_gate.get("reason", "fixture diff review is still open")),
                objective_hint="review the round-to-round fixture diff and close any unresolved expansion drift before the next rerun",
                evidence_required=gate_command,
            )
        )

    if completed_sessions < min_completed_sessions:
        blockers.append(
            build_blocker(
                blocker_id="minimum-sample-not-met",
                label=f"completed sessions {completed_sessions} are below the minimum threshold {min_completed_sessions}",
                objective_hint="increase completed sessions before promoting the next beta round",
                evidence_required=simulation_command,
            )
        )
    if success_rate < min_success_rate:
        blockers.append(
            build_blocker(
                blocker_id="success-rate-below-threshold",
                label=f"success rate {round(success_rate, 4)} is below the minimum threshold {min_success_rate}",
                objective_hint="repair the main workflow blockers and rerun the current round until the success threshold is met",
                evidence_required=simulation_command,
            )
        )
    if blocker_issue_count > max_blocker_issue_count:
        blockers.append(
            build_blocker(
                blocker_id="blocker-themes-open",
                label=f"blocker issue count {blocker_issue_count} exceeds the allowed threshold {max_blocker_issue_count}",
                objective_hint="close blocker themes in the current round before cohort expansion",
                evidence_required=simulation_command,
            )
        )

    if not blockers:
        blockers.append(
            build_blocker(
                blocker_id="beta-round-hold",
                label=reason,
                objective_hint="repair the current beta gate blockers and rerun the gate",
                evidence_required=gate_command,
            )
        )
    return blockers


def build_resume_artifacts(
    *,
    report_path: Path,
    evidence_artifacts: dict[str, object],
) -> list[str]:
    ordered = [
        str(report_path),
        str(evidence_artifacts.get("feedback_ledger_markdown", "")).strip(),
        str(evidence_artifacts.get("fixture_manifest_json", "")).strip(),
        str(evidence_artifacts.get("cohort_plan_json", "")).strip(),
        str(evidence_artifacts.get("ramp_plan_json", "")).strip(),
        str(evidence_artifacts.get("fixture_diff_json", "")).strip(),
        str(evidence_artifacts.get("simulation_summary_json", "")).strip(),
    ]
    seen: set[str] = set()
    result: list[str] = []
    for item in ordered:
        if item == "" or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def build_recommended_commands(
    *,
    round_id: str,
    previous_round_id: str | None,
    decision: str,
    product_workspace_exists: bool,
    governance_workspace_exists: bool,
) -> list[str]:
    commands: list[str] = []
    if not product_workspace_exists:
        commands.append("python scripts/init_product_delivery.py --root . --pretty")
    if decision == "escalate" and not governance_workspace_exists:
        commands.append("python scripts/init_technical_governance.py --root . --pretty")
    commands.append(
        f"python scripts/preview_beta_simulation_fixture.py --config .skill-beta/simulation-configs/{round_id}.json --pretty"
    )
    if previous_round_id is not None:
        commands.append(
            "python scripts/compare_beta_simulation_manifests.py "
            f"--previous .skill-beta/fixture-previews/{previous_round_id}/beta-simulation-manifest.json "
            f"--current .skill-beta/fixture-previews/{round_id}/beta-simulation-manifest.json --pretty"
        )
    commands.extend(
        [
            f"python scripts/run_beta_simulation.py --config .skill-beta/simulation-configs/{round_id}.json --pretty",
            "python scripts/summarize_beta_simulation.py "
            f"--run .skill-beta/simulation-runs/{round_id}/beta-simulation-run.json "
            "--feedback-ledger-out .skill-beta/feedback-ledger.md "
            f"--round-report-out .skill-beta/reports/{round_id}.json --pretty",
            f"python scripts/evaluate_beta_round.py --report .skill-beta/reports/{round_id}.json --pretty",
        ]
    )
    return commands


def build_beta_remediation_brief(
    *,
    output_dir: Path,
    decision: str,
    reason: str,
    round_id: str,
    report_path: Path,
    repo_root: Path,
    previous_round_id: str | None,
    follow_up: dict[str, object],
    blockers: list[dict[str, str]],
    blocker_breakdown: dict[str, object] | None,
    cohort_gate: dict[str, object],
    ramp_gate: dict[str, object],
    diff_gate: dict[str, object],
    evidence_artifacts: dict[str, object],
) -> tuple[str, str]:
    owner = "Sentinel Architect (NB)" if bool(follow_up.get("release_governance_recommended")) else "World-Class Product Architect"
    loop_state = "escalated" if decision == "escalate" else "reopened"
    objective_prefix = (
        "stabilize the critical beta blockers and enter governance for"
        if decision == "escalate"
        else "repair the beta round blockers for"
    )
    product_workspace_exists = (repo_root / ".skill-product").exists()
    governance_workspace_exists = (repo_root / ".skill-governance").exists()
    brief = {
        "schema_version": "beta-remediation-brief/v1",
        "generated_at": now_iso(),
        "source_gate": "beta-round-gate",
        "decision": decision,
        "loop_state": loop_state,
        "owner": owner,
        "round_id": round_id,
        "reason": reason,
        "objective": f"{objective_prefix} {round_id}",
        "objective_hints": [item["objective_hint"] for item in blockers],
        "blockers": blockers,
        "gate_context": {
            "cohort_gate_status": str(cohort_gate.get("status", "")),
            "ramp_gate_status": str(ramp_gate.get("status", "")),
            "diff_gate_status": str(diff_gate.get("status", "")),
            "continue_beta": bool(follow_up.get("continue_beta")),
            "release_governance_recommended": bool(follow_up.get("release_governance_recommended")),
            "next_round_recommended": follow_up.get("next_round_recommended"),
        },
        "report_context": {
            "report_path": str(report_path),
            "source_simulation_run": str(evidence_artifacts.get("simulation_run_json", "")).strip() or None,
            "feedback_ledger_markdown": str(evidence_artifacts.get("feedback_ledger_markdown", "")).strip() or None,
            "fixture_manifest_json": str(evidence_artifacts.get("fixture_manifest_json", "")).strip() or None,
            "cohort_plan_json": str(evidence_artifacts.get("cohort_plan_json", "")).strip() or None,
            "ramp_plan_json": str(evidence_artifacts.get("ramp_plan_json", "")).strip() or None,
            "fixture_diff_json": str(evidence_artifacts.get("fixture_diff_json", "")).strip() or None,
        },
        "recommended_commands": build_recommended_commands(
            round_id=round_id,
            previous_round_id=previous_round_id,
            decision=decision,
            product_workspace_exists=product_workspace_exists,
            governance_workspace_exists=governance_workspace_exists,
        ),
        "required_evidence": sorted({item["evidence_required"] for item in blockers}),
        "resume_artifacts": build_resume_artifacts(
            report_path=report_path,
            evidence_artifacts=evidence_artifacts,
        ),
    }
    if blocker_breakdown is not None:
        brief["blocker_breakdown"] = blocker_breakdown
    response_contract.validate_beta_remediation_brief(brief)

    json_path = output_dir / "next-round-remediation-brief.json"
    markdown_path = output_dir / "next-round-remediation-brief.md"
    json_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_lines = [
        "# Beta Remediation Brief",
        "",
        f"- Generated: `{brief['generated_at']}`",
        f"- Decision: `{decision}`",
        f"- Loop state: `{loop_state}`",
        f"- Owner: `{owner}`",
        f"- Round: `{round_id}`",
        f"- Reason: {reason}",
        f"- Objective: {brief['objective']}",
        "",
        "## Blockers",
        "",
    ]
    for blocker in blockers:
        markdown_lines.extend(
            [
                f"- `{blocker['id']}`: {blocker['label']}",
                f"  - Objective hint: {blocker['objective_hint']}",
                f"  - Evidence required: `{blocker['evidence_required']}`",
            ]
        )
    markdown_lines.extend(["", "## Recommended Commands", ""])
    markdown_lines.extend([f"- `{item}`" for item in brief["recommended_commands"]])
    markdown_lines.extend(["", "## Resume Artifacts", ""])
    markdown_lines.extend([f"- `{item}`" for item in brief["resume_artifacts"]])
    if blocker_breakdown is not None:
        by_persona = blocker_breakdown.get("by_persona", [])
        by_scenario = blocker_breakdown.get("by_scenario", [])
        if isinstance(by_persona, list) and by_persona:
            markdown_lines.extend(["", "## Blocker Breakdown By Persona", ""])
            for item in by_persona[:5]:
                if not isinstance(item, dict):
                    continue
                markdown_lines.append(
                    f"- {item.get('label')}: sessions={item.get('session_count')}, blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, high={item.get('high_severity_issue_count')}, themes={', '.join(compact_string_list(item.get('top_feedback_themes')))}"
                )
        if isinstance(by_scenario, list) and by_scenario:
            markdown_lines.extend(["", "## Blocker Breakdown By Scenario", ""])
            for item in by_scenario[:5]:
                if not isinstance(item, dict):
                    continue
                markdown_lines.append(
                    f"- {item.get('label')}: sessions={item.get('session_count')}, blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, high={item.get('high_severity_issue_count')}, themes={', '.join(compact_string_list(item.get('top_feedback_themes')))}"
                )
    markdown_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    return str(json_path), str(markdown_path)


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
    fixture_manifest_path = (
        resolve_report_relative_path(report_path, fixture_manifest_json_raw)
        if fixture_manifest_json_raw != ""
        else None
    )
    ramp_plan_json_raw = str(evidence_artifacts.get("ramp_plan_json", "")).strip()
    cohort_plan_json_raw = str(evidence_artifacts.get("cohort_plan_json", "")).strip()
    manifest_sessions: list[dict[str, object]] = []
    observed_persona_ids: list[str] = []
    if fixture_manifest_path is not None and fixture_manifest_path.exists():
        manifest_payload = load_manifest(fixture_manifest_path)
        sessions = manifest_payload.get("sessions", [])
        if isinstance(sessions, list):
            manifest_sessions = [dict(item) for item in sessions if isinstance(item, dict)]
            observed_persona_ids = sorted(
                {
                    str(item.get("persona_id", "")).strip()
                    for item in manifest_sessions
                    if str(item.get("persona_id", "")).strip() != ""
                }
            )

    cohort_required_for_round = fixture_manifest_json_raw != ""
    observed_persona_counter = Counter(
        str(item.get("persona_id", "")).strip()
        for item in manifest_sessions
        if str(item.get("persona_id", "")).strip() != ""
    )
    observed_scenario_ids = sorted(
        {
            str(item.get("scenario_id", "")).strip()
            for item in manifest_sessions
            if str(item.get("scenario_id", "")).strip() != ""
        }
    )
    observed_trace_ids = sorted(
        {
            str(item.get("trace_id", "")).strip()
            for item in manifest_sessions
            if str(item.get("trace_id", "")).strip() != ""
        }
    )
    cohort_gate = {
        "status": "not-required",
        "required_for_round": cohort_required_for_round,
        "reason": "Cohort-plan evidence is not required when no fixture manifest is attached to the round report.",
        "cohort_plan_json": cohort_plan_json_raw or None,
        "expected_fixture_id": None,
        "expected_planned_sessions": None,
        "observed_fixture_sessions": len(manifest_sessions),
        "expected_persona_counts": {},
        "observed_persona_counts": dict(sorted(observed_persona_counter.items())),
        "expected_scenario_ids": [],
        "observed_scenario_ids": observed_scenario_ids,
        "expected_trace_ids": [],
        "observed_trace_ids": observed_trace_ids,
    }
    if cohort_required_for_round:
        if fixture_manifest_path is None or not fixture_manifest_path.exists():
            cohort_gate.update(
                {
                    "status": "missing",
                    "reason": "Cohort gate requires a readable fixture manifest before the round can advance.",
                }
            )
        elif cohort_plan_json_raw == "":
            cohort_gate.update(
                {
                    "status": "missing",
                    "reason": "Fixture-backed beta evidence requires a machine-readable cohort plan before the gate can advance.",
                }
            )
        else:
            cohort_payload = load_cohort_plan(resolve_report_relative_path(report_path, cohort_plan_json_raw))
            rounds = cohort_payload.get("rounds", [])
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
                cohort_gate.update(
                    {
                        "status": "missing-round",
                        "reason": "Cohort plan does not define the current round.",
                    }
                )
            else:
                persona_targets = expected_round.get("persona_targets", [])
                expected_persona_counts = {
                    str(item.get("persona_id", "")).strip(): int(item.get("session_count", 0))
                    for item in persona_targets
                    if isinstance(item, dict) and str(item.get("persona_id", "")).strip() != ""
                } if isinstance(persona_targets, list) else {}
                expected_scenario_ids = sorted(
                    {
                        str(item).strip()
                        for item in expected_round.get("required_scenario_ids", [])
                        if str(item).strip() != ""
                    }
                ) if isinstance(expected_round.get("required_scenario_ids", []), list) else []
                expected_trace_ids = sorted(
                    {
                        str(item).strip()
                        for item in expected_round.get("required_trace_ids", [])
                        if str(item).strip() != ""
                    }
                ) if isinstance(expected_round.get("required_trace_ids", []), list) else []
                expected_fixture_id = str(expected_round.get("fixture_id", "")).strip() or None
                expected_planned_sessions = int(expected_round.get("planned_sessions", 0))
                cohort_gate.update(
                    {
                        "cohort_plan_json": cohort_plan_json_raw,
                        "expected_fixture_id": expected_fixture_id,
                        "expected_planned_sessions": expected_planned_sessions,
                        "expected_persona_counts": dict(sorted(expected_persona_counts.items())),
                        "expected_scenario_ids": expected_scenario_ids,
                        "expected_trace_ids": expected_trace_ids,
                    }
                )
                mismatches: list[str] = []
                if expected_planned_sessions != len(manifest_sessions):
                    mismatches.append("planned fixture sessions")
                if dict(sorted(expected_persona_counts.items())) != dict(sorted(observed_persona_counter.items())):
                    mismatches.append("persona counts")
                if expected_scenario_ids != observed_scenario_ids:
                    mismatches.append("scenario coverage")
                if expected_trace_ids != observed_trace_ids:
                    mismatches.append("trace coverage")
                if mismatches:
                    cohort_gate.update(
                        {
                            "status": "mismatch",
                            "reason": "Cohort plan does not match the resolved fixture for " + ", ".join(mismatches) + ".",
                        }
                    )
                else:
                    cohort_gate.update(
                        {
                            "status": "passed",
                            "reason": "Cohort plan matches the resolved fixture manifest.",
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
    elif cohort_required_for_round and cohort_gate["status"] in {"missing", "missing-round", "mismatch"}:
        decision = "hold"
        reason = str(cohort_gate["reason"])
        follow_up = {
            "next_action": "hold expansion, reconcile the cohort plan with the resolved fixture, and rerun the gate",
            "continue_beta": False,
            "release_governance_recommended": False,
            "next_round_recommended": round_id,
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

    blockers = build_beta_gate_blockers(
        decision=decision,
        reason=reason,
        round_id=round_id,
        completed_sessions=completed_sessions,
        min_completed_sessions=min_completed_sessions,
        success_rate=success_rate,
        min_success_rate=min_success_rate,
        blocker_issue_count=blocker_issue_count,
        max_blocker_issue_count=max_blocker_issue_count,
        cohort_gate=cohort_gate,
        ramp_gate=ramp_gate,
        diff_gate=diff_gate,
    )

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
        "cohort_gate": cohort_gate,
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
    if decision in {"hold", "escalate"}:
        repo_root = repo_root_from_report(report_path)
        base_resume_artifacts = build_resume_artifacts(
            report_path=report_path,
            evidence_artifacts=evidence_artifacts,
        )
        brief_json, brief_markdown = build_beta_remediation_brief(
            output_dir=output_dir,
            decision=decision,
            reason=reason,
            round_id=round_id,
            report_path=report_path,
            repo_root=repo_root,
            previous_round_id=previous_round_id,
            follow_up=follow_up,
            blockers=blockers,
            blocker_breakdown=blocker_breakdown,
            cohort_gate=cohort_gate,
            ramp_gate=ramp_gate,
            diff_gate=diff_gate,
            evidence_artifacts=evidence_artifacts,
        )
        writeback_artifacts = sync_workspace_writebacks(
            repo_root=repo_root,
            output_dir=output_dir,
            round_id=round_id,
            decision=decision,
            reason=reason,
            blockers=blockers,
            blocker_breakdown=blocker_breakdown,
            brief_json=brief_json,
            release_governance_recommended=bool(follow_up.get("release_governance_recommended")),
        )
        follow_up["loop_state"] = "escalated" if decision == "escalate" else "reopened"
        follow_up["blockers"] = [str(item["label"]) for item in blockers]
        follow_up["brief_json"] = brief_json
        follow_up["brief_markdown"] = brief_markdown
        follow_up["resume_artifacts"] = base_resume_artifacts + [
            item for item in writeback_artifacts if item not in base_resume_artifacts
        ]
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
        f"- Cohort gate: {cohort_gate['status']}",
        f"- Cohort reason: {cohort_gate['reason']}",
        f"- Ramp gate: {ramp_gate['status']}",
        f"- Ramp reason: {ramp_gate['reason']}",
        f"- Diff gate: {diff_gate['status']}",
        f"- Diff reason: {diff_gate['reason']}",
        f"- Next action: {follow_up['next_action']}",
        f"- Next round: {follow_up['next_round_recommended'] or 'n/a'}",
    ]
    if "brief_json" in follow_up:
        lines.extend(
            [
                f"- Follow-up loop state: {follow_up.get('loop_state')}",
                f"- Remediation brief JSON: {follow_up['brief_json']}",
                f"- Remediation brief Markdown: {follow_up['brief_markdown']}",
            ]
        )
    if cohort_gate["status"] != "not-required":
        lines.extend(
            [
                "",
                "## Cohort Plan Gate",
                "",
                f"- Expected fixture id: {cohort_gate['expected_fixture_id'] or 'n/a'}",
                f"- Expected planned sessions: {cohort_gate['expected_planned_sessions']}",
                f"- Observed fixture sessions: {cohort_gate['observed_fixture_sessions']}",
                f"- Expected persona counts: {cohort_gate['expected_persona_counts']}",
                f"- Observed persona counts: {cohort_gate['observed_persona_counts']}",
                f"- Expected scenario ids: {', '.join(cohort_gate['expected_scenario_ids']) if cohort_gate['expected_scenario_ids'] else 'n/a'}",
                f"- Observed scenario ids: {', '.join(cohort_gate['observed_scenario_ids']) if cohort_gate['observed_scenario_ids'] else 'n/a'}",
                f"- Expected trace ids: {', '.join(cohort_gate['expected_trace_ids']) if cohort_gate['expected_trace_ids'] else 'n/a'}",
                f"- Observed trace ids: {', '.join(cohort_gate['observed_trace_ids']) if cohort_gate['observed_trace_ids'] else 'n/a'}",
            ]
        )
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
