#!/usr/bin/env python3
"""Evaluate a post-release feedback report and emit the next post-release decision."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
AUTOMATION_STATE_SCRIPT = SCRIPT_DIR / "automation_state.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_evaluate_post_release_response_contract", RESPONSE_CONTRACT_SCRIPT)
automation_state = load_module(
    "virtual_team_evaluate_post_release_automation_state",
    AUTOMATION_STATE_SCRIPT,
)


def load_report(report_path: Path) -> dict[str, object]:
    with report_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("post-release feedback report must be a JSON object")
    response_contract.validate_post_release_feedback_report(payload)
    return payload


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def repo_root_from_report(report_path: Path) -> Path:
    if report_path.parent.name == ".skill-post-release":
        return report_path.parent.parent
    if report_path.parent.parent.name == ".skill-post-release":
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


def open_feedback_items(feedback_items: object) -> list[dict[str, object]]:
    if not isinstance(feedback_items, list):
        return []
    result: list[dict[str, object]] = []
    for item in feedback_items:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "")).strip()
        if status in {"fixed", "accepted"}:
            continue
        result.append(item)
    return result


def build_breakdown(items: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    grouped: dict[str, Counter[str]] = {}
    for item in items:
        label = str(item.get(key, "")).strip() or "unknown"
        bucket = grouped.setdefault(label, Counter())
        bucket["feedback_count"] += 1
        severity = str(item.get("severity", "")).strip()
        if severity == "critical":
            bucket["critical_count"] += 1
        if severity == "high":
            bucket["high_count"] += 1
    ranked = sorted(
        grouped.items(),
        key=lambda pair: (-pair[1]["critical_count"], -pair[1]["high_count"], -pair[1]["feedback_count"], pair[0]),
    )
    return [
        {
            "label": label,
            "feedback_count": counts["feedback_count"],
            "critical_count": counts["critical_count"],
            "high_count": counts["high_count"],
        }
        for label, counts in ranked
    ]


def build_blocker_breakdown(items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "by_source": build_breakdown(items, "source"),
        "by_area": build_breakdown(items, "affected_area"),
    }


def build_blockers(
    *,
    items: list[dict[str, object]],
    signal_summary: dict[str, object],
    report_rel: str,
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for item in items:
        severity = str(item.get("severity", "")).strip()
        if severity not in {"critical", "high"}:
            continue
        blocker_id = str(item.get("id", "")).strip() or "feedback-blocker"
        label = str(item.get("label", "")).strip() or "post-release blocker"
        recommended_action = str(item.get("recommended_action", "")).strip() or "triage and remediate the shipped issue"
        evidence_required = compact_string_list(item.get("evidence_artifacts"))
        blockers.append(
            {
                "id": blocker_id,
                "label": label,
                "objective_hint": recommended_action,
                "evidence_required": evidence_required[0] if evidence_required else report_rel,
            }
        )
    blocker_issue_count = int(signal_summary.get("blocker_issue_count", 0))
    escalation_issue_count = int(signal_summary.get("escalation_issue_count", 0))
    if not blockers and (blocker_issue_count > 0 or escalation_issue_count > 0):
        blockers.append(
            {
                "id": "post-release-signal-drift",
                "label": "post-release signal summary reports unresolved blocker pressure",
                "objective_hint": "reconcile shipped feedback, telemetry, and release expectations before the next rollout step",
                "evidence_required": report_rel,
            }
        )
    return blockers


def writeback_section_body(
    *,
    release_label: str,
    decision: str,
    reason: str,
    report_path: str,
    blockers: list[dict[str, str]],
    blocker_breakdown: dict[str, object],
    brief_json: str | None,
) -> str:
    lines = [
        f"- Release label: `{release_label}`",
        f"- Decision: `{decision}`",
        f"- Reason: {reason}",
        f"- Signal report: `{report_path}`",
    ]
    if brief_json:
        lines.append(f"- Iteration brief: `{brief_json}`")
    lines.extend(["", "### Open Post-Release Blockers", ""])
    for blocker in blockers:
        lines.extend(
            [
                f"- `{blocker['id']}`: {blocker['label']}",
                f"  - Objective hint: {blocker['objective_hint']}",
                f"  - Evidence required: `{blocker['evidence_required']}`",
            ]
        )
    by_source = blocker_breakdown.get("by_source", [])
    if isinstance(by_source, list) and by_source:
        lines.extend(["", "### Source Hotspots", ""])
        for item in by_source[:5]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- {item.get('label')}: feedback={item.get('feedback_count')}, critical={item.get('critical_count')}, high={item.get('high_count')}"
            )
    by_area = blocker_breakdown.get("by_area", [])
    if isinstance(by_area, list) and by_area:
        lines.extend(["", "### Area Hotspots", ""])
        for item in by_area[:5]:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- {item.get('label')}: feedback={item.get('feedback_count')}, critical={item.get('critical_count')}, high={item.get('high_count')}"
            )
    return "\n".join(lines)


def sync_workspace_writebacks(
    *,
    repo_root: Path,
    output_dir: Path,
    release_label: str,
    decision: str,
    reason: str,
    report_path: str,
    blockers: list[dict[str, str]],
    blocker_breakdown: dict[str, object],
    brief_json: str | None,
) -> list[str]:
    section_body = writeback_section_body(
        release_label=release_label,
        decision=decision,
        reason=reason,
        report_path=report_path,
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
            "## Post-Release Feedback Writeback",
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
    if decision != "escalate":
        governance_lines.extend(["", "Governance escalation is not required for this observation window."])
    governance_writeback.write_text("\n".join(governance_lines) + "\n", encoding="utf-8")
    resume_artifacts.append(str(governance_writeback))

    if decision == "escalate":
        governance_targets = [
            repo_root / ".skill-governance" / "change-plan.md",
            repo_root / ".skill-governance" / "release-checklist.md",
        ]
        for target in governance_targets:
            if not target.exists():
                continue
            updated = replace_or_append_section(
                target.read_text(encoding="utf-8"),
                "## Post-Release Feedback Escalation",
                section_body,
            )
            target.write_text(updated, encoding="utf-8")
            resume_artifacts.append(str(target))

    return resume_artifacts


def build_recommended_commands(report_path: Path, decision: str, repo_root: Path) -> list[str]:
    repo_report = ".skill-post-release/current-signals.json"
    if repo_root not in report_path.parents:
        repo_report = str(report_path)
    commands = [f"python scripts/evaluate_post_release_feedback.py --report {repo_report} --pretty"]
    if not (repo_root / ".skill-product").exists():
        commands.append("python scripts/init_product_delivery.py --root . --pretty")
    if decision == "escalate" and not (repo_root / ".skill-governance").exists():
        commands.append("python scripts/init_technical_governance.py --root . --pretty")
    if decision in {"iterate", "escalate"}:
        commands.append("python scripts/run_release_gate.py --output-dir evals/release-gate --pretty")
    return commands


def evaluate_post_release_feedback(report_path: Path) -> dict[str, object]:
    resolved_report = report_path.resolve()
    payload = load_report(resolved_report)
    repo_root = repo_root_from_report(resolved_report)
    output_dir = resolved_report.parent / "decisions" / resolved_report.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    signal_summary = dict(payload.get("signal_summary", {}))
    report_context = dict(payload.get("report_context", {}))
    feedback_items = open_feedback_items(payload.get("feedback_items", []))
    blocker_breakdown = build_blocker_breakdown(feedback_items)
    report_rel = str(resolved_report)
    blockers = build_blockers(items=feedback_items, signal_summary=signal_summary, report_rel=report_rel)

    telemetry_status = str(signal_summary.get("telemetry_status", "unknown")).strip()
    adoption_trend = str(signal_summary.get("adoption_trend", "unknown")).strip()
    satisfaction_trend = str(signal_summary.get("satisfaction_trend", "unknown")).strip()
    critical_count = sum(1 for item in feedback_items if str(item.get("severity", "")).strip() == "critical")
    high_count = sum(1 for item in feedback_items if str(item.get("severity", "")).strip() == "high")
    blocker_issue_count = int(signal_summary.get("blocker_issue_count", 0))
    escalation_issue_count = int(signal_summary.get("escalation_issue_count", 0))
    recommended_commands = build_recommended_commands(resolved_report, "monitor", repo_root)

    if escalation_issue_count > 0 or critical_count > 0 or telemetry_status == "critical":
        decision = "escalate"
        loop_state = "escalated"
        owner = "Sentinel Architect (NB)"
        ok = False
        reason = "post-release signals show production-impacting regression pressure or critical telemetry risk"
        objective = "stabilize the shipped release, contain the escalation path, and reopen remediation under governance"
        next_action = "technical-governance"
    elif blocker_issue_count > 0 or high_count > 0 or telemetry_status == "warning" or adoption_trend == "worsening" or satisfaction_trend == "worsening":
        decision = "iterate"
        loop_state = "reopened"
        owner = "World-Class Product Architect"
        ok = False
        reason = "post-release signals show meaningful regression or adoption pressure that should reopen bounded remediation"
        objective = "close shipped blockers, tighten the current slice, and prepare a corrective iteration"
        next_action = "bounded-iteration"
    else:
        decision = "monitor"
        loop_state = "watching"
        owner = "World-Class Product Architect"
        ok = True
        reason = "post-release signals remain within the watch thresholds and do not justify reopening remediation yet"
        objective = "continue observing shipped feedback and refresh the signal report on the next checkpoint"
        next_action = "continue-monitoring"

    recommended_commands = build_recommended_commands(resolved_report, decision, repo_root)
    follow_up: dict[str, object] = {
        "loop_state": loop_state,
        "next_action": next_action,
        "resume_artifacts": [
            str(repo_root / ".skill-post-release" / "triage-summary.md"),
            str(resolved_report),
            str(repo_root / ".skill-post-release" / "feedback-ledger.md"),
        ],
        "recommended_commands": recommended_commands,
    }

    if not ok:
        brief = {
            "generated_at": now_iso(),
            "source_gate": "post-release-feedback",
            "decision": decision,
            "loop_state": loop_state,
            "owner": owner,
            "release_label": str(payload.get("release_label", "")).strip(),
            "reason": reason,
            "objective": objective,
            "blockers": blockers,
            "signal_summary": signal_summary,
            "report_context": report_context,
            "required_evidence": [
                str(resolved_report),
                str(repo_root / ".skill-post-release" / "feedback-ledger.md"),
                "updated release candidate evidence before the next ship decision",
            ],
            "recommended_commands": recommended_commands,
        }
        brief_json = output_dir / "next-iteration-brief.json"
        brief_markdown = output_dir / "next-iteration-brief.md"
        brief_json.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        brief_markdown.write_text(
            "\n".join(
                [
                    "# Post-Release Next Iteration Brief",
                    "",
                    f"- Decision: `{decision}`",
                    f"- Loop state: `{loop_state}`",
                    f"- Owner: `{owner}`",
                    f"- Objective: {objective}",
                    "",
                    "## Blockers",
                    "",
                ]
                + [
                    f"- `{item['id']}`: {item['label']}\n  - Objective hint: {item['objective_hint']}\n  - Evidence required: `{item['evidence_required']}`"
                    for item in blockers
                ]
                + [
                    "",
                    "## Recommended Commands",
                    "",
                ]
                + [f"- `{command}`" for command in recommended_commands]
            ),
            encoding="utf-8",
        )
        writebacks = sync_workspace_writebacks(
            repo_root=repo_root,
            output_dir=output_dir,
            release_label=str(payload.get("release_label", "")).strip(),
            decision=decision,
            reason=reason,
            report_path=report_rel,
            blockers=blockers,
            blocker_breakdown=blocker_breakdown,
            brief_json=str(brief_json),
        )
        follow_up.update(
            {
                "blockers": [str(item["label"]) for item in blockers],
                "brief_json": str(brief_json),
                "brief_markdown": str(brief_markdown),
                "resume_artifacts": follow_up["resume_artifacts"] + [item for item in writebacks if item not in follow_up["resume_artifacts"]],
            }
        )

    result = {
        "generated_at": now_iso(),
        "source_gate": "post-release-feedback",
        "ok": ok,
        "decision": decision,
        "loop_state": loop_state,
        "owner": owner,
        "release_label": str(payload.get("release_label", "")).strip(),
        "reason": reason,
        "objective": objective,
        "signal_summary": signal_summary,
        "blocker_breakdown": blocker_breakdown,
        "report_path": str(resolved_report),
        "report_context": report_context,
        "follow_up": follow_up,
    }

    json_path = output_dir / "post-release-feedback-result.json"
    markdown_path = output_dir / "post-release-feedback-report.md"
    result["json_report"] = str(json_path)
    result["markdown_report"] = str(markdown_path)
    result["automation_state"] = automation_state.write_automation_state(
        repo_root=repo_root,
        source_workflow="post-release-close-loop",
        state_kind="post-release-feedback-result",
        mode="manual",
        phase="post-release",
        status="completed",
        decision=decision,
        execution_mode="post-release-feedback",
        resume_anchor=str(repo_root / ".skill-post-release" / "triage-summary.md"),
        resume_artifacts=[str(item) for item in follow_up.get("resume_artifacts", []) if str(item).strip()],
        recommended_next_step=str(follow_up.get("next_action", next_action)),
        handoff_target=str(follow_up.get("next_action", next_action)),
        primary_path=str(output_dir / "automation-state.json"),
        related_paths=[
            str(json_path),
            str(markdown_path),
            str(resolved_report),
        ],
        upstream_dependencies=[
            str(item)
            for item in [
                resolved_report,
                report_context.get("release_closure_json"),
                report_context.get("release_gate_json"),
                report_context.get("telemetry_snapshot_json"),
            ]
            if str(item).strip()
        ],
        metadata={
            "ok": ok,
            "loop_state": loop_state,
            "owner": owner,
        },
    )
    response_contract.validate_post_release_feedback_result(result)
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown_lines = [
        "# Post-Release Feedback Report",
        "",
        f"- Generated: `{result['generated_at']}`",
        f"- Decision: `{decision}`",
        f"- Loop state: `{loop_state}`",
        f"- Owner: `{owner}`",
        f"- Release label: `{result['release_label']}`",
        f"- Reason: {reason}",
        f"- Objective: {objective}",
        "",
        "## Signal Summary",
        "",
        f"- Total feedback items: `{signal_summary.get('total_feedback_items')}`",
        f"- Unique users affected: `{signal_summary.get('unique_users_affected')}`",
        f"- Blocker issue count: `{signal_summary.get('blocker_issue_count')}`",
        f"- Escalation issue count: `{signal_summary.get('escalation_issue_count')}`",
        f"- Telemetry status: `{signal_summary.get('telemetry_status')}`",
        f"- Adoption trend: `{signal_summary.get('adoption_trend')}`",
        f"- Satisfaction trend: `{signal_summary.get('satisfaction_trend')}`",
        "",
        "## Hotspots By Source",
        "",
    ]
    by_source = blocker_breakdown.get("by_source", [])
    if isinstance(by_source, list) and by_source:
        markdown_lines.extend(
            [
                f"- {item['label']}: feedback={item['feedback_count']}, critical={item['critical_count']}, high={item['high_count']}"
                for item in by_source
                if isinstance(item, dict)
            ]
        )
    else:
        markdown_lines.append("- none")
    markdown_lines.extend(["", "## Hotspots By Area", ""])
    by_area = blocker_breakdown.get("by_area", [])
    if isinstance(by_area, list) and by_area:
        markdown_lines.extend(
            [
                f"- {item['label']}: feedback={item['feedback_count']}, critical={item['critical_count']}, high={item['high_count']}"
                for item in by_area
                if isinstance(item, dict)
            ]
        )
    else:
        markdown_lines.append("- none")
    markdown_lines.extend(["", "## Follow-up", ""])
    markdown_lines.append(f"- Next action: `{next_action}`")
    markdown_lines.append("- Resume artifacts:")
    markdown_lines.extend([f"- `{item}`" for item in follow_up["resume_artifacts"]])
    markdown_lines.extend(["", "## Recommended Commands", ""])
    markdown_lines.extend([f"- `{item}`" for item in recommended_commands])
    markdown_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

    triage_summary = repo_root / ".skill-post-release" / "triage-summary.md"
    triage_summary.parent.mkdir(parents=True, exist_ok=True)
    triage_summary.write_text(
        "\n".join(
            [
                "# Post-Release Triage Summary",
                "",
                f"- Current decision: `{decision}`",
                f"- Current owner: `{owner}`",
                f"- Release label: `{result['release_label']}`",
                f"- Resume anchor: `{resolved_report}`",
                "",
                "## Current Signals",
                "",
                f"- Reason: {reason}",
                f"- Telemetry status: `{signal_summary.get('telemetry_status')}`",
                f"- Adoption trend: `{signal_summary.get('adoption_trend')}`",
                f"- Satisfaction trend: `{signal_summary.get('satisfaction_trend')}`",
                "",
                "## Next Action",
                "",
                f"- `{next_action}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate post-release feedback signals.")
    parser.add_argument("--report", required=True, help="Path to the post-release feedback report JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON result.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate_post_release_feedback(Path(args.report).resolve())
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
