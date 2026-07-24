#!/usr/bin/env python3
"""Build the per-eval release-gate fixture and run the release gate.

This wraps the fixture-construction logic that lives inside
``run_benchmarks.py``'s ``evaluate_evals`` so that skill-forge's blind audit can
exercise ``release_gate`` runner evals via a declared CLI command. Given an
``--eval-id``, it loads the eval from ``evals/evals.json``, builds the benchmark
fixture / beta-gate result / completion evidence that the eval declares, runs
``run_release_gate.run_release_gate(...)``, and writes the full result JSON to
``--output``.

This is deliberately skill-local: the fixture shapes are specific to
virtual-intelligent-dev-team's release-gate contract.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EVALS_PATH = SKILL_DIR / "evals" / "evals.json"
RELEASE_GATE_SCRIPT = SKILL_DIR / "scripts" / "run_release_gate.py"
RESPONSE_CONTRACT_SCRIPT = SKILL_DIR / "scripts" / "response_contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_response_contract_fixture", RESPONSE_CONTRACT_SCRIPT)
release_gate_module = load_module("virtual_team_release_gate_fixture", RELEASE_GATE_SCRIPT)


def find_eval(eval_id: int, evals_path: Path) -> dict:
    payload = json.loads(evals_path.read_text(encoding="utf-8"))
    for item in payload.get("evals", []):
        if item.get("id") == eval_id:
            return item
    raise RuntimeError(f"eval id {eval_id} not found in {evals_path}")


def build_fixture(eval_item: dict, prompt: str, temp_root: Path) -> tuple[Path, Path | None, Path | None]:
    """Return (benchmark_fixture_path, beta_gate_result_path, completion_evidence_path)."""
    summary = eval_item.get("release_gate_summary", {})
    if not isinstance(summary, dict):
        raise RuntimeError(f"release_gate eval {eval_item.get('id')} must provide release_gate_summary")

    benchmark_json = temp_root / "benchmark-results.json"
    benchmark_markdown = temp_root / "benchmark-report.md"
    benchmark_json.write_text(
        json.dumps(
            {
                "summary": summary,
                "eval_run": {"passed": 0, "total": 0, "cases": [], "category_breakdown": []},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    benchmark_markdown.write_text("# Benchmark Report\n", encoding="utf-8")

    fixture_payload: dict = {
        "summary": summary,
        "json_report": str(benchmark_json),
        "markdown_report": str(benchmark_markdown),
    }
    if bool(summary.get("offline_drill_enabled")):
        offline_report = temp_root / "offline-loop-drill-report.md"
        offline_report.write_text("# Offline Loop Drill Report\n", encoding="utf-8")
        fixture_payload["offline_drill_run"] = {"markdown_report": str(offline_report)}
    fixture_path = temp_root / "benchmark-fixture.json"
    fixture_path.write_text(json.dumps(fixture_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    beta_gate_result: Path | None = None
    beta_gate_config = eval_item.get("release_gate_beta")
    if isinstance(beta_gate_config, dict):
        beta_decision = str(beta_gate_config.get("decision", "")).strip() or "hold"
        beta_round_id = str(beta_gate_config.get("round_id", "")).strip() or "round-02"
        beta_result_dir = temp_root / "beta-round-decisions" / beta_round_id
        beta_result_dir.mkdir(parents=True, exist_ok=True)
        beta_result_path = beta_result_dir / "beta-round-gate-result.json"
        beta_report_path = temp_root / "beta-reports" / f"{beta_round_id}.json"
        beta_report_path.parent.mkdir(parents=True, exist_ok=True)
        beta_report_path.write_text("{}", encoding="utf-8")
        beta_markdown_path = beta_result_dir / "beta-round-gate-report.md"
        beta_markdown_path.write_text("# Beta Gate Report\n", encoding="utf-8")
        beta_payload = {
            "generated_at": "2026-04-08T12:00:00Z",
            "skill_name": "virtual-intelligent-dev-team",
            "ok": beta_decision == "advance",
            "decision": beta_decision,
            "reason": str(beta_gate_config.get("reason", "beta gate fixture")),
            "round_id": beta_round_id,
            "report_path": str(beta_report_path),
            "observed": {
                "planned_sample_size": 12,
                "completed_sessions": 12,
                "success_rate": float(beta_gate_config.get("success_rate", 0.75 if beta_decision != "advance" else 0.92)),
                "blocker_issue_count": int(beta_gate_config.get("blocker_issue_count", 1 if beta_decision == "hold" else 0)),
                "critical_issue_count": int(beta_gate_config.get("critical_issue_count", 1 if beta_decision == "escalate" else 0)),
                "high_severity_issue_count": int(beta_gate_config.get("high_severity_issue_count", 1 if beta_decision != "advance" else 0)),
                "top_feedback_themes": beta_gate_config.get("top_feedback_themes", ["beta regression"]),
            },
            "thresholds": {
                "min_completed_sessions": 10,
                "min_success_rate": 0.8,
                "max_blocker_issue_count": 0,
                "max_critical_issue_count": 0,
            },
            "follow_up": {
                "next_action": str(beta_gate_config.get("next_action", "hold expansion and resolve beta blockers")),
                "continue_beta": beta_decision == "advance",
                "release_governance_recommended": bool(beta_gate_config.get("release_governance_recommended", beta_decision == "escalate")),
                "next_round_recommended": beta_gate_config.get("next_round_recommended", None if beta_decision == "escalate" else beta_round_id),
            },
            "json_report": str(beta_result_path),
            "markdown_report": str(beta_markdown_path),
        }
        blocker_breakdown = beta_gate_config.get("blocker_breakdown")
        if isinstance(blocker_breakdown, dict):
            beta_payload["blocker_breakdown"] = blocker_breakdown
        elif beta_decision != "advance":
            beta_payload["blocker_breakdown"] = {
                "by_persona": [
                    {
                        "label": "First-Time Novice",
                        "session_count": 4,
                        "blocker_issue_count": 1 if beta_decision == "hold" else 0,
                        "critical_issue_count": 1 if beta_decision == "escalate" else 0,
                        "high_severity_issue_count": 1,
                        "session_ids": ["session-01", "session-02"],
                        "top_feedback_themes": ["onboarding confusion"],
                    }
                ],
                "by_scenario": [
                    {
                        "label": "first meaningful task",
                        "session_count": 4,
                        "blocker_issue_count": 1 if beta_decision == "hold" else 0,
                        "critical_issue_count": 1 if beta_decision == "escalate" else 0,
                        "high_severity_issue_count": 1,
                        "session_ids": ["session-01", "session-02"],
                        "top_feedback_themes": ["onboarding confusion"],
                    }
                ],
            }
        response_contract.validate_beta_round_gate_result(beta_payload)
        beta_result_path.write_text(json.dumps(beta_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        beta_gate_result = beta_result_path

    completion_evidence_path: Path | None = None
    completion_evidence_config = eval_item.get("release_gate_completion_evidence")
    if isinstance(completion_evidence_config, dict):
        completion_evidence_dir = temp_root / ".vidt/evidence"
        completion_evidence_dir.mkdir(parents=True, exist_ok=True)
        completion_status = str(completion_evidence_config.get("status", "passed")).strip() or "passed"
        completion_payload = {
            "schema_version": "completion-evidence/v1",
            "generated_at": "2026-04-08T12:00:00Z",
            "source_request": prompt,
            "evidence_action": "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
            "result": {
                "status": completion_status,
                "summary": "release gate eval fixture completion evidence",
                "exit_code": 0 if completion_status == "passed" else 1,
            },
            "covered_scope": completion_evidence_config.get("covered_scope", ["release gate eval fixture"]),
            "uncovered_scope": completion_evidence_config.get("uncovered_scope", ["none"]),
            "residual_risk": completion_evidence_config.get("residual_risk", ["none"]),
            "confidence_grade": str(completion_evidence_config.get("confidence_grade", "B")).strip() or "B",
            "evidence_refs": completion_evidence_config.get(
                "evidence_refs",
                ["python scripts/run_release_gate.py --output-dir evals/release-gate --pretty"],
            ),
        }
        response_contract.validate_completion_evidence(completion_payload)
        completion_evidence_path = completion_evidence_dir / "completion-evidence.json"
        completion_evidence_path.write_text(json.dumps(completion_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return fixture_path, beta_gate_result, completion_evidence_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a release-gate eval fixture and run the release gate.")
    parser.add_argument("--eval-id", type=int, required=True, help="Eval id to load from evals.json.")
    parser.add_argument("--evals", default=str(EVALS_PATH), help="Path to evals.json.")
    parser.add_argument("--output", required=True, help="Output JSON path for the release-gate result.")
    args = parser.parse_args()

    evals_path = Path(args.evals).resolve()
    eval_item = find_eval(args.eval_id, evals_path)
    prompt = str(eval_item.get("prompt", ""))

    with tempfile.TemporaryDirectory(prefix="release-gate-fixture-") as tmp:
        temp_root = Path(tmp)
        fixture_path, beta_gate_result, completion_evidence = build_fixture(eval_item, prompt, temp_root)
        result = release_gate_module.run_release_gate(
            output_dir=temp_root / "release-gate-output",
            benchmark_fixture=fixture_path,
            beta_gate_result=beta_gate_result,
            completion_evidence=completion_evidence,
        )

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
