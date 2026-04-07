#!/usr/bin/env python3
"""Compare baseline and candidate benchmark reports for bounded iteration decisions."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_compare_benchmark_response_contract", RESPONSE_CONTRACT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    response_contract.validate_benchmark_run_result(data)
    return data


def case_failures(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    eval_run = payload.get("eval_run", {})
    if not isinstance(eval_run, dict):
        return {}
    cases = eval_run.get("cases", [])
    if not isinstance(cases, list):
        return {}

    failures: dict[str, dict[str, object]] = {}
    for item in cases:
        if not isinstance(item, dict):
            continue
        if bool(item.get("passed", False)):
            continue
        case_id = str(item.get("id"))
        failures[case_id] = {
            "id": item.get("id"),
            "prompt": item.get("prompt"),
            "failures": item.get("failures", []),
        }
    return failures


def category_map(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    eval_run = payload.get("eval_run", {})
    if not isinstance(eval_run, dict):
        return {}
    items = eval_run.get("category_breakdown", [])
    if not isinstance(items, list):
        return {}
    return {
        str(item.get("category")): item
        for item in items
        if isinstance(item, dict) and item.get("category") is not None
    }


def summarize(payload: dict[str, object]) -> dict[str, object]:
    summary = payload.get("summary", {})
    eval_run = payload.get("eval_run", {})
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(eval_run, dict):
        eval_run = {}
    return {
        "overall_passed": bool(summary.get("overall_passed", False)),
        "evals_passed": int(eval_run.get("passed", 0)),
        "evals_total": int(eval_run.get("total", 0)),
    }


def compare_results(baseline: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
    baseline_summary = summarize(baseline)
    candidate_summary = summarize(candidate)

    baseline_failures = case_failures(baseline)
    candidate_failures = case_failures(candidate)
    baseline_categories = category_map(baseline)
    candidate_categories = category_map(candidate)

    new_failures = [
        candidate_failures[key]
        for key in sorted(candidate_failures)
        if key not in baseline_failures
    ]
    resolved_failures = [
        baseline_failures[key]
        for key in sorted(baseline_failures)
        if key not in candidate_failures
    ]

    category_regressions: list[dict[str, object]] = []
    category_improvements: list[dict[str, object]] = []
    for category in sorted(set(baseline_categories) | set(candidate_categories)):
        previous = baseline_categories.get(category, {"passed": 0, "total": 0})
        current = candidate_categories.get(category, {"passed": 0, "total": 0})
        previous_passed = int(previous.get("passed", 0))
        previous_total = int(previous.get("total", 0))
        current_passed = int(current.get("passed", 0))
        current_total = int(current.get("total", 0))
        if current_passed < previous_passed:
            category_regressions.append(
                {
                    "category": category,
                    "baseline": {"passed": previous_passed, "total": previous_total},
                    "candidate": {"passed": current_passed, "total": current_total},
                }
            )
        elif current_passed > previous_passed:
            category_improvements.append(
                {
                    "category": category,
                    "baseline": {"passed": previous_passed, "total": previous_total},
                    "candidate": {"passed": current_passed, "total": current_total},
                }
            )

    rollback_reasons: list[str] = []
    if baseline_summary["overall_passed"] and not candidate_summary["overall_passed"]:
        rollback_reasons.append("candidate benchmark no longer passes overall checks")
    if candidate_summary["evals_passed"] < baseline_summary["evals_passed"]:
        rollback_reasons.append("candidate passes fewer evals than baseline")
    if len(new_failures) > 0:
        rollback_reasons.append("candidate introduces new eval failures")
    if len(category_regressions) > 0:
        rollback_reasons.append("candidate regresses one or more benchmark categories")

    keep_reasons: list[str] = []
    if candidate_summary["overall_passed"] and not baseline_summary["overall_passed"]:
        keep_reasons.append("candidate restores overall benchmark pass state")
    if candidate_summary["evals_passed"] > baseline_summary["evals_passed"]:
        keep_reasons.append("candidate passes more evals than baseline")
    if len(resolved_failures) > 0 and len(new_failures) == 0:
        keep_reasons.append("candidate resolves failures without introducing new ones")
    if len(category_improvements) > 0 and len(category_regressions) == 0:
        keep_reasons.append("candidate improves benchmark categories without regressions")

    if rollback_reasons:
        decision = "rollback"
        decision_reason = rollback_reasons
    elif keep_reasons:
        decision = "keep"
        decision_reason = keep_reasons
    elif candidate_summary == baseline_summary and len(new_failures) == 0 and len(resolved_failures) == 0:
        decision = "stop"
        decision_reason = ["candidate is materially unchanged from baseline"]
    else:
        decision = "retry"
        decision_reason = ["candidate is inconclusive and needs another evidence-backed round"]

    return {
        "decision": decision,
        "decision_reason": decision_reason,
        "baseline": baseline_summary,
        "candidate": candidate_summary,
        "new_failures": new_failures,
        "resolved_failures": resolved_failures,
        "category_regressions": category_regressions,
        "category_improvements": category_improvements,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two benchmark JSON reports.")
    parser.add_argument("--baseline", required=True, help="Baseline benchmark-results.json")
    parser.add_argument("--candidate", required=True, help="Candidate benchmark-results.json")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = compare_results(
        baseline=load_json(Path(args.baseline).resolve()),
        candidate=load_json(Path(args.candidate).resolve()),
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
