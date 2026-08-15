#!/usr/bin/env python3
"""Deterministic regression checks derived from real production delivery field trials."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "references" / "field-trial-regression-cases.json"


def evaluate_case(case: dict[str, Any]) -> str:
    kind = case.get("kind")
    data = case.get("input") or {}

    if kind == "production_gate":
        if not data.get("code_pass"):
            return "hold"
        if data.get("remote_required") and not data.get("resource_identity_verified"):
            return "hold"
        if data.get("migration_history_state") in {"drift", "unexpected"}:
            return "hold"
        if data.get("control_required") and not data.get("control_pass"):
            return "hold"
        if data.get("data_required") and not data.get("data_pass"):
            return "hold"
        return "ship"

    if kind == "permission_diagnosis":
        if not data.get("resource_identity_verified"):
            return "verify_resource_identity"
        if not data.get("capability_verified"):
            return "verify_provider_scope"
        return "permission_path_verified"

    if kind == "operator_handoff":
        required = (
            "dry_run_first",
            "expected_output",
            "stop_conditions",
            "secret_boundary",
            "resume_anchor",
        )
        return "valid_handoff" if all(data.get(key) for key in required) else "invalid_handoff"

    if kind == "migration_drift":
        if not data.get("local_remote_aligned") or data.get("unexpected_remote_only"):
            return "reconcile_before_push"
        return "safe_to_dry_run"

    if kind == "release_train_issue":
        if not data.get("target_branch_is_default") and data.get("expects_auto_close"):
            return "do_not_assume_auto_close"
        return "closure_semantics_ok"

    if kind == "semantic_boundary":
        if data.get("semantic_source") == "visible_text":
            return "spec_violation"
        return "semantic_boundary_ok"

    if kind == "truth_reconciliation":
        if data.get("contradictory_sources") and data.get("starting_new_epic"):
            return "reconcile_before_new_epic"
        return "planning_truth_ready"

    if kind == "hotfix":
        if (
            data.get("release_complete")
            and data.get("scope_bounded")
            and not data.get("release_contract_broadly_invalid")
        ):
            return "bounded_hotfix"
        return "escalate_release_remediation"

    raise ValueError(f"unknown field-trial case kind: {kind!r}")


def run(cases_path: Path) -> dict[str, Any]:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("field-trial regression cases must be a non-empty JSON array")

    results: list[dict[str, Any]] = []
    failures = 0
    seen_ids: set[str] = set()

    for case in cases:
        case_id = str(case.get("id") or "")
        if not case_id or case_id in seen_ids:
            raise ValueError(f"case id must be unique and non-empty: {case_id!r}")
        seen_ids.add(case_id)

        expected = case.get("expected")
        actual = evaluate_case(case)
        passed = actual == expected
        failures += 0 if passed else 1
        results.append(
            {
                "id": case_id,
                "kind": case.get("kind"),
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
        )

    return {
        "cases": len(results),
        "passed": len(results) - failures,
        "failed": failures,
        "result": "passed" if failures == 0 else "failed",
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(args.cases)
    print(json.dumps(report, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
