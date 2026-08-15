from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_field_trial_regressions.py"
CASES = ROOT / "references" / "field-trial-regression-cases.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("field_trial_checker", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_field_trial_regression_suite_passes():
    checker = load_checker()
    report = checker.run(CASES)
    assert report["result"] == "passed"
    assert report["failed"] == 0
    assert report["cases"] >= 8


def test_field_trial_case_ids_are_unique_and_cover_real_failures():
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    ids = [case["id"] for case in cases]
    kinds = {case["kind"] for case in cases}
    assert len(ids) == len(set(ids))
    assert {
        "production_gate",
        "permission_diagnosis",
        "operator_handoff",
        "migration_drift",
        "release_train_issue",
        "semantic_boundary",
        "truth_reconciliation",
        "hotfix",
    } <= kinds


def test_green_code_with_pending_remote_migration_is_hold():
    checker = load_checker()
    case = {
        "kind": "production_gate",
        "input": {
            "code_pass": True,
            "remote_required": True,
            "resource_identity_verified": True,
            "control_required": True,
            "control_pass": False,
            "data_required": False,
            "data_pass": False,
            "migration_history_state": "aligned",
        },
    }
    assert checker.evaluate_case(case) == "hold"


def test_resource_identity_precedes_permission_diagnosis():
    checker = load_checker()
    assert checker.evaluate_case(
        {
            "kind": "permission_diagnosis",
            "input": {
                "resource_identity_verified": False,
                "capability_verified": False,
            },
        }
    ) == "verify_resource_identity"


def test_visible_localized_text_cannot_drive_semantics():
    checker = load_checker()
    assert checker.evaluate_case(
        {
            "kind": "semantic_boundary",
            "input": {"semantic_source": "visible_text", "localized": True},
        }
    ) == "spec_violation"
