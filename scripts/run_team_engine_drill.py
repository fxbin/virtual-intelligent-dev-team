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
    "verifying": {"passed", "retrying", "hold", "failed"},
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


def run_drill() -> dict[str, Any]:
    sample = load_sample()
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

    state = "planned"
    for next_state in ["spawned", "running", "produced", "verifying"]:
        validate_transition(state, next_state, checks, errors)
        state = next_state

    for index, cycle in enumerate(cycles, start=1):
        implementation_output = cycle["implementation_output"]
        verification_report = cycle["verification_report"]
        verdict = verification_report["verdict"]

        require(
            implementation_output["self_reported_done"] is True,
            f"cycle {index} worker reports done only before verification",
            checks,
            errors,
        )
        require(
            verification_report["verifier_role"] == work_order["verifier_role"],
            f"cycle {index} verifier role matches work order",
            checks,
            errors,
        )

        if verdict == "fail":
            remediation_patch = verification_report.get("remediation_patch")
            require(
                bool(remediation_patch and remediation_patch.get("instructions")),
                f"cycle {index} fail includes remediation_patch instructions",
                checks,
                errors,
            )
            validate_transition("verifying", "retrying", checks, errors)
            validate_transition("retrying", "running", checks, errors)
            state = "verifying"
        elif verdict == "pass":
            require(verification_report.get("remediation_patch") is None, f"cycle {index} pass has no remediation_patch", checks, errors)
            checked = verification_report.get("checked_gates", [])
            require(
                bool(checked) and all(item.get("passed") for item in checked),
                f"cycle {index} pass checks all listed gates",
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
    require(report["producer_can_self_pass"] is False, "DeliveryCycleReport preserves self-pass prohibition", checks, errors)
    require(report["verifier_verdict"] == cycles[-1]["verification_report"]["verdict"], "DeliveryCycleReport matches final verifier verdict", checks, errors)
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
