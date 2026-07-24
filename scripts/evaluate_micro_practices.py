#!/usr/bin/env python3
"""Evaluate a micro-practice ledger and emit a completion gate decision."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
DEFAULT_LEDGER_PATH = Path(".vidt/practices") / "micro-practice-ledger.json"
DEFAULT_OUTPUT_DIR = Path(".vidt/practices")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_evaluate_micro_practices_response_contract", RESPONSE_CONTRACT_SCRIPT)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_ledger(ledger_path: Path) -> dict[str, object]:
    with ledger_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("micro-practice ledger must be a JSON object")
    response_contract.validate_micro_practice_ledger(payload)
    return payload


def repo_root_from_ledger(ledger_path: Path) -> Path:
    for parent in ledger_path.parents:
        if parent.name == ".vidt":
            return parent.parent
    return ledger_path.parent


def compact_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def quote_cli_arg(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def summarize_practices(ledger: dict[str, object]) -> list[dict[str, object]]:
    raw_practices = ledger.get("active_practices", [])
    if not isinstance(raw_practices, list):
        return []
    practices: list[dict[str, object]] = []
    for item in raw_practices:
        if not isinstance(item, dict):
            continue
        practices.append(
            {
                "name": str(item.get("name", "")).strip(),
                "reference": str(item.get("reference", "")).strip(),
                "status": str(item.get("status", "active")).strip(),
                "evidence": compact_string_list(item.get("evidence")),
                "next_check": str(item.get("next_check", "")).strip(),
            }
        )
    return practices


def build_status_counts(practices: list[dict[str, object]]) -> dict[str, int]:
    counts = Counter(str(item.get("status", "")).strip() for item in practices)
    return {
        "total": len(practices),
        "active": counts["active"],
        "satisfied": counts["satisfied"],
        "blocked": counts["blocked"],
    }


def decide(status_counts: dict[str, int]) -> tuple[str, str, bool, str]:
    if status_counts["blocked"] > 0:
        return (
            "blocked",
            "one or more micro-practices are blocked",
            False,
            "resolve blocked micro-practices before claiming completion",
        )
    if status_counts["active"] > 0:
        return (
            "continue",
            "one or more micro-practices still need concrete evidence",
            False,
            "capture evidence and update active practices to satisfied or blocked",
        )
    return (
        "complete",
        "all micro-practices are satisfied",
        True,
        "use the ledger evaluation as completion evidence",
    )


def build_recommended_commands(
    *,
    practices: list[dict[str, object]],
    decision: str,
    ledger_rel: str,
) -> list[str]:
    commands: list[str] = []
    if decision in {"continue", "blocked"}:
        target_status = "active" if decision == "continue" else "blocked"
        evidence_hint = "<evidence>" if decision == "continue" else "<blocker resolution evidence>"
        for item in practices:
            if str(item.get("status", "")).strip() != target_status:
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            commands.append(
                "python scripts/update_micro_practices.py"
                f" --ledger {ledger_rel}"
                f" --name {quote_cli_arg(name)}"
                " --status satisfied"
                f" --evidence {quote_cli_arg(evidence_hint)}"
                " --pretty"
            )
        if not commands:
            commands.append(
                "python scripts/update_micro_practices.py"
                f" --ledger {ledger_rel}"
                " --name <practice-name>"
                " --status satisfied"
                f" --evidence {quote_cli_arg(evidence_hint)}"
                " --pretty"
            )
    commands.append(f"python scripts/evaluate_micro_practices.py --ledger {ledger_rel} --pretty")
    return commands


def render_markdown(result: dict[str, object]) -> str:
    status_counts = result.get("status_counts", {})
    if not isinstance(status_counts, dict):
        status_counts = {}
    practices = result.get("practices", [])
    if not isinstance(practices, list):
        practices = []
    follow_up = result.get("follow_up", {})
    if not isinstance(follow_up, dict):
        follow_up = {}

    lines = [
        "# Micro-Practice Evaluation",
        "",
        f"- Generated: `{result.get('generated_at', '')}`",
        f"- Decision: `{result.get('decision', '')}`",
        f"- OK: `{result.get('ok', False)}`",
        f"- Reason: {result.get('reason', '')}",
        f"- Workflow bundle: `{result.get('workflow_bundle', '')}`",
        f"- Ledger: `{result.get('ledger_path', '')}`",
        "",
        "## Status Counts",
        "",
        f"- Total: `{status_counts.get('total', 0)}`",
        f"- Active: `{status_counts.get('active', 0)}`",
        f"- Satisfied: `{status_counts.get('satisfied', 0)}`",
        f"- Blocked: `{status_counts.get('blocked', 0)}`",
        "",
        "## Practices",
        "",
    ]
    if practices:
        for item in practices:
            if not isinstance(item, dict):
                continue
            lines.extend(
                [
                    f"- `{item.get('name', '')}`: `{item.get('status', '')}`",
                    f"  - Reference: `{item.get('reference', '')}`",
                    f"  - Evidence: {', '.join(compact_string_list(item.get('evidence'))) or 'none'}",
                    f"  - Next check: {item.get('next_check', '')}",
                ]
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Follow-up",
            "",
            f"- Completion allowed: `{follow_up.get('completion_allowed', False)}`",
            f"- Next action: `{follow_up.get('next_action', '')}`",
            f"- Resume anchor: `{follow_up.get('resume_anchor', '')}`",
            "- Recommended commands:",
        ]
    )
    for command in compact_string_list(follow_up.get("recommended_commands")):
        lines.append(f"- `{command}`")
    lines.append("")
    return "\n".join(lines)


def evaluate_micro_practices(
    ledger_path: Path,
    *,
    output_dir: Path | None = None,
    write_reports: bool = True,
) -> dict[str, object]:
    resolved_ledger = ledger_path.resolve()
    ledger = load_ledger(resolved_ledger)
    repo_root = repo_root_from_ledger(resolved_ledger)
    resolved_output_dir = output_dir.resolve() if output_dir is not None else repo_root / DEFAULT_OUTPUT_DIR
    if write_reports:
        resolved_output_dir.mkdir(parents=True, exist_ok=True)

    practices = summarize_practices(ledger)
    status_counts = build_status_counts(practices)
    decision, reason, completion_allowed, next_action = decide(status_counts)

    json_report = resolved_output_dir / "micro-practice-evaluation.json"
    markdown_report = resolved_output_dir / "micro-practice-evaluation.md"
    ledger_rel = str(resolved_ledger.relative_to(repo_root)) if resolved_ledger.is_relative_to(repo_root) else str(resolved_ledger)
    json_rel = str(json_report.relative_to(repo_root)) if json_report.is_relative_to(repo_root) else str(json_report)
    markdown_rel = str(markdown_report.relative_to(repo_root)) if markdown_report.is_relative_to(repo_root) else str(markdown_report)

    result: dict[str, object] = {
        "schema_version": "micro-practice-evaluation/v1",
        "generated_at": now_iso(),
        "source_gate": "micro-practice-ledger",
        "ok": completion_allowed,
        "decision": decision,
        "reason": reason,
        "workflow_bundle": str(ledger.get("workflow_bundle", "")),
        "ledger_path": ledger_rel,
        "source_request": str(ledger.get("source_request", "")),
        "status_counts": status_counts,
        "practices": practices,
        "follow_up": {
            "completion_allowed": completion_allowed,
            "next_action": next_action,
            "resume_anchor": ledger_rel,
            "resume_artifacts": [ledger_rel, json_rel, markdown_rel],
            "recommended_commands": build_recommended_commands(
                practices=practices,
                decision=decision,
                ledger_rel=ledger_rel,
            ),
        },
        "json_report": json_rel,
        "markdown_report": markdown_rel,
    }
    response_contract.validate_micro_practice_evaluation(result)
    if write_reports:
        json_report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        markdown_report.write_text(render_markdown(result), encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a micro-practice ledger completion gate.")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER_PATH), help="Path to micro-practice ledger JSON.")
    parser.add_argument("--output-dir", help="Optional output directory for evaluation artifacts.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate_micro_practices(
        Path(args.ledger).resolve(),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
