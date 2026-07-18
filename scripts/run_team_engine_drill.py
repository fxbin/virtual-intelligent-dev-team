#!/usr/bin/env python3
"""Offline Team Engine Lite drill for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SAMPLE_REPORT = SKILL_DIR / "assets" / "sample-delivery-cycle-report.json"


LEGAL_TRANSITIONS = {
    "planned": {"spawned"},
    "spawned": {"running"},
    "running": {"produced"},
    "produced": {"verifying"},
    "verifying": {"passed", "retrying", "hold", "failed", "spec_violation"},
    "spec_violation": {"retrying", "escalated"},
    "retrying": {"running"},
    "passed": {"accepted"},
    "hold": {"escalated"},
    "failed": {"escalated"},
}


def load_sample() -> dict[str, Any]:
    return json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))


def require(condition: bool, message: str, checks: list[str], errors: list[str]) -> None:
    if condition:
        checks.append(message)
    else:
        errors.append(message)


def validate_transition(previous: str, current: str, checks: list[str], errors: list[str]) -> None:
    allowed = LEGAL_TRANSITIONS.get(previous, set())
    require(current in allowed, f"legal transition {previous} -> {current}", checks, errors)


def run_drill(sample: dict[str, Any] | None = None) -> dict[str, Any]:
    sample = sample if sample is not None else load_sample()
    work_order = sample["work_order"]
    cycles = sample["cycles"]
    report = sample["delivery_cycle_report"]
    checks: list[str] = []
    errors: list[str] = []

    require(work_order["permissions"]["worker_can_self_pass"] is False, "worker cannot self-pass", checks, errors)
    require(
        work_order["permissions"]["lead_accept_requires_cycle_report"] is True,
        "lead accept requires DeliveryCycleReport",
        checks,
        errors,
    )
    require(work_order["worker_role"] != work_order["verifier_role"], "worker and verifier roles are separated", checks, errors)
    require(
        work_order["backend_binding"]["runtime_claim"] == "soft_orchestration_only",
        "backend binding declares soft orchestration only",
        checks,
        errors,
    )
    require(
        work_order["backend_binding"]["worker_backend_id"] != work_order["backend_binding"]["verifier_backend_id"],
        "worker and verifier backend bindings are separated",
        checks,
        errors,
    )
    require(len(cycles) <= int(work_order["max_cycles"]), "cycle count stays within max_cycles", checks, errors)
    required_gates = {
        str(gate) for gate in work_order.get("acceptance_gates", []) if str(gate).strip()
    }
    require(bool(required_gates), "WorkOrder declares required acceptance gates", checks, errors)

    state = "planned"
    for next_state in ["spawned", "running", "produced", "verifying"]:
        validate_transition(state, next_state, checks, errors)
        state = next_state

    for index, cycle in enumerate(cycles, start=1):
        implementation_output = cycle["implementation_output"]
        verification_report = cycle["verification_report"]
        verdict = verification_report["verdict"]

        require(
            implementation_output.get("task_id") == work_order.get("task_id"),
            f"cycle {index} implementation task_id matches work order",
            checks,
            errors,
        )
        require(
            implementation_output.get("cycle_id") == cycle.get("cycle_id"),
            f"cycle {index} implementation cycle_id matches cycle",
            checks,
            errors,
        )
        require(
            implementation_output.get("worker_role") == work_order.get("worker_role"),
            f"cycle {index} worker role matches work order",
            checks,
            errors,
        )
        require(
            implementation_output["self_reported_done"] is True,
            f"cycle {index} worker reports done only before verification",
            checks,
            errors,
        )
        require(
            verification_report.get("task_id") == work_order.get("task_id"),
            f"cycle {index} verification task_id matches work order",
            checks,
            errors,
        )
        require(
            verification_report.get("cycle_id") == cycle.get("cycle_id"),
            f"cycle {index} verification cycle_id matches cycle",
            checks,
            errors,
        )
        require(
            verification_report["verifier_role"] == work_order["verifier_role"],
            f"cycle {index} verifier role matches work order",
            checks,
            errors,
        )

        checked = verification_report.get("checked_gates", [])
        if not isinstance(checked, list):
            checked = []
        checked_gate_ids = [
            str(item.get("gate_id", ""))
            for item in checked
            if isinstance(item, dict) and str(item.get("gate_id", "")).strip()
        ]
        require(
            len(checked_gate_ids) == len(set(checked_gate_ids)),
            f"cycle {index} checked gates are unique",
            checks,
            errors,
        )

        if verdict in {"fail", "spec_violation"}:
            remediation_patch = verification_report.get("remediation_patch")
            require(
                bool(remediation_patch and remediation_patch.get("instructions")),
                f"cycle {index} {verdict} includes remediation_patch instructions",
                checks,
                errors,
            )
            if verdict == "spec_violation":
                require(
                    bool(verification_report.get("confirmed_issues"))
                    and bool(verification_report.get("evidence_refs")),
                    f"cycle {index} spec_violation includes objective issue and evidence",
                    checks,
                    errors,
                )
                validate_transition("verifying", "spec_violation", checks, errors)
                validate_transition("spec_violation", "retrying", checks, errors)
            else:
                validate_transition("verifying", "retrying", checks, errors)
            validate_transition("retrying", "running", checks, errors)
            state = "verifying"
        elif verdict == "pass":
            require(verification_report.get("remediation_patch") is None, f"cycle {index} pass has no remediation_patch", checks, errors)
            require(
                required_gates.issubset(set(checked_gate_ids)),
                f"cycle {index} pass checks every WorkOrder acceptance gate",
                checks,
                errors,
            )
            require(
                bool(checked)
                and all(
                    isinstance(item, dict)
                    and item.get("passed") is True
                    and bool(str(item.get("evidence", "")).strip())
                    for item in checked
                ),
                f"cycle {index} pass gives positive evidence for all checked gates",
                checks,
                errors,
            )
            validate_transition("verifying", "passed", checks, errors)
            state = "passed"
        elif verdict == "hold":
            validate_transition("verifying", "hold", checks, errors)
            state = "hold"
        else:
            errors.append(f"unsupported verifier verdict: {verdict}")

    require(report["cycle_count"] == len(cycles), "DeliveryCycleReport cycle_count matches cycle list", checks, errors)
    for identity_field in ("task_id", "workflow_bundle", "lead_role", "worker_role", "verifier_role", "max_cycles"):
        require(
            report.get(identity_field) == work_order.get(identity_field),
            f"DeliveryCycleReport {identity_field} matches WorkOrder",
            checks,
            errors,
        )
    require(report["producer_can_self_pass"] is False, "DeliveryCycleReport preserves self-pass prohibition", checks, errors)
    require(report["verifier_verdict"] == cycles[-1]["verification_report"]["verdict"], "DeliveryCycleReport matches final verifier verdict", checks, errors)
    final_checked = cycles[-1]["verification_report"].get("checked_gates", [])
    final_gate_ids = {
        str(item.get("gate_id", ""))
        for item in final_checked
        if isinstance(item, dict) and str(item.get("gate_id", "")).strip()
    }
    report_checked = report.get("checked_gates", [])
    report_gate_ids = {
        str(item.get("gate_id", "")) if isinstance(item, dict) else str(item)
        for item in report_checked
        if str(item.get("gate_id", "") if isinstance(item, dict) else item).strip()
    }
    require(
        report_gate_ids == final_gate_ids,
        "DeliveryCycleReport checked_gates matches final VerificationReport",
        checks,
        errors,
    )
    require(
        report["backend_orchestration_verdict"] in {"pass", "pass_with_watch", "simulated", "hold", "escalated"},
        "backend orchestration verdict is recognized",
        checks,
        errors,
    )
    require(
        report["team_engine_closure_verdict"] in {"pass", "pass_with_watch", "hold", "escalated"},
        "closure verdict is recognized",
        checks,
        errors,
    )

    if state == "passed":
        validate_transition("passed", "accepted", checks, errors)
        state = "accepted"
        require(report["next_state"] == "accepted", "passed task advances to accepted", checks, errors)
        require(bool(report.get("evidence_refs")), "accepted task preserves evidence refs", checks, errors)
    elif state in {"hold", "failed"}:
        validate_transition(state, "escalated", checks, errors)
        state = "escalated"
        require(bool(report.get("human_escalation")), "hold or failed task has human escalation", checks, errors)

    return {
        "ok": not errors,
        "checks": checks,
        "errors": errors,
        "final_state": state,
        "cycle_count": len(cycles),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Team Engine Lite offline drill.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    result = run_drill()
    payload = {
        "ok": result["ok"],
        "final_state": result["final_state"],
        "cycle_count": result["cycle_count"],
        "checks": result["checks"],
        "errors": result["errors"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
