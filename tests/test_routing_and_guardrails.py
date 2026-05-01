from __future__ import annotations

import importlib.util
from contextlib import contextmanager
import json
import shutil
import subprocess
import sys
import unittest
from unittest import mock
from pathlib import Path
from uuid import uuid4


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parent
TMP_ROOT = REPO_ROOT / ".tmp-validation"
ROUTE_SCRIPT = SKILL_DIR / "scripts" / "route_request.py"
GUARDRAIL_SCRIPT = SKILL_DIR / "scripts" / "git_workflow_guardrail.py"
INIT_ITERATION_SCRIPT = SKILL_DIR / "scripts" / "init_iteration_round.py"
COMPARE_BENCHMARKS_SCRIPT = SKILL_DIR / "scripts" / "compare_benchmark_results.py"
REGISTER_BASELINE_SCRIPT = SKILL_DIR / "scripts" / "register_benchmark_baseline.py"
RUN_ITERATION_CYCLE_SCRIPT = SKILL_DIR / "scripts" / "run_iteration_cycle.py"
PROMOTE_BASELINE_SCRIPT = SKILL_DIR / "scripts" / "promote_iteration_baseline.py"
SYNC_PATTERNS_SCRIPT = SKILL_DIR / "scripts" / "sync_distilled_patterns.py"
RUN_ITERATION_LOOP_SCRIPT = SKILL_DIR / "scripts" / "run_iteration_loop.py"
RUN_BENCHMARKS_SCRIPT = SKILL_DIR / "scripts" / "run_benchmarks.py"
RUN_OFFLINE_DRILL_SCRIPT = SKILL_DIR / "scripts" / "run_offline_loop_drill.py"
RUN_RELEASE_GATE_SCRIPT = SKILL_DIR / "scripts" / "run_release_gate.py"
INIT_PRE_DEVELOPMENT_SCRIPT = SKILL_DIR / "scripts" / "init_pre_development_plan.py"
INIT_PROJECT_MEMORY_SCRIPT = SKILL_DIR / "scripts" / "init_project_memory.py"
INIT_PRODUCT_DELIVERY_SCRIPT = SKILL_DIR / "scripts" / "init_product_delivery.py"
INIT_BETA_VALIDATION_SCRIPT = SKILL_DIR / "scripts" / "init_beta_validation.py"
INIT_BETA_ROUND_REPORT_SCRIPT = SKILL_DIR / "scripts" / "init_beta_round_report.py"
INIT_BETA_SIMULATION_SCRIPT = SKILL_DIR / "scripts" / "init_beta_simulation.py"
PREVIEW_BETA_SIMULATION_FIXTURE_SCRIPT = SKILL_DIR / "scripts" / "preview_beta_simulation_fixture.py"
COMPARE_BETA_SIMULATION_MANIFESTS_SCRIPT = SKILL_DIR / "scripts" / "compare_beta_simulation_manifests.py"
RUN_BETA_SIMULATION_SCRIPT = SKILL_DIR / "scripts" / "run_beta_simulation.py"
SUMMARIZE_BETA_SIMULATION_SCRIPT = SKILL_DIR / "scripts" / "summarize_beta_simulation.py"
EVALUATE_BETA_ROUND_SCRIPT = SKILL_DIR / "scripts" / "evaluate_beta_round.py"
INIT_TECHNICAL_GOVERNANCE_SCRIPT = SKILL_DIR / "scripts" / "init_technical_governance.py"
INIT_POST_RELEASE_FEEDBACK_SCRIPT = SKILL_DIR / "scripts" / "init_post_release_feedback.py"
EVALUATE_POST_RELEASE_FEEDBACK_SCRIPT = SKILL_DIR / "scripts" / "evaluate_post_release_feedback.py"
RUN_AUTO_WORKFLOW_SCRIPT = SKILL_DIR / "scripts" / "run_auto_workflow.py"
INSPECT_AUTOMATION_STATE_SCRIPT = SKILL_DIR / "scripts" / "inspect_automation_state.py"
RESUME_FROM_AUTOMATION_STATE_SCRIPT = SKILL_DIR / "scripts" / "resume_from_automation_state.py"
GENERATE_RESPONSE_PACK_SCRIPT = SKILL_DIR / "scripts" / "generate_response_pack.py"
RESPONSE_CONTRACT_SCRIPT = SKILL_DIR / "scripts" / "response_contract.py"
VALIDATOR_SCRIPT = SKILL_DIR / "scripts" / "validate_virtual_team.py"
VERIFY_ACTION_SCRIPT = SKILL_DIR / "scripts" / "verify_action.py"
CONTRACT_LINT_SCRIPT = SKILL_DIR / "scripts" / "lint_virtual_team_contract.py"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_intelligent_dev_team_route_request", ROUTE_SCRIPT)
guardrail = load_module("virtual_intelligent_dev_team_guardrail", GUARDRAIL_SCRIPT)
iteration_init = load_module("virtual_intelligent_dev_team_iteration_init", INIT_ITERATION_SCRIPT)
benchmark_compare = load_module("virtual_intelligent_dev_team_benchmark_compare", COMPARE_BENCHMARKS_SCRIPT)
baseline_registry = load_module("virtual_intelligent_dev_team_baseline_registry", REGISTER_BASELINE_SCRIPT)
iteration_cycle = load_module("virtual_intelligent_dev_team_iteration_cycle", RUN_ITERATION_CYCLE_SCRIPT)
baseline_promotion = load_module("virtual_intelligent_dev_team_baseline_promotion", PROMOTE_BASELINE_SCRIPT)
pattern_sync = load_module("virtual_intelligent_dev_team_pattern_sync", SYNC_PATTERNS_SCRIPT)
iteration_loop = load_module("virtual_intelligent_dev_team_iteration_loop", RUN_ITERATION_LOOP_SCRIPT)
benchmark_runner = load_module("virtual_intelligent_dev_team_run_benchmarks", RUN_BENCHMARKS_SCRIPT)
offline_loop_drill = load_module("virtual_intelligent_dev_team_run_offline_loop_drill", RUN_OFFLINE_DRILL_SCRIPT)
release_gate = load_module("virtual_intelligent_dev_team_run_release_gate", RUN_RELEASE_GATE_SCRIPT)
planning_init = load_module("virtual_intelligent_dev_team_planning_init", INIT_PRE_DEVELOPMENT_SCRIPT)
project_memory_init = load_module("virtual_intelligent_dev_team_project_memory_init", INIT_PROJECT_MEMORY_SCRIPT)
product_delivery_init = load_module("virtual_intelligent_dev_team_product_delivery_init", INIT_PRODUCT_DELIVERY_SCRIPT)
beta_validation_init = load_module("virtual_intelligent_dev_team_beta_validation_init", INIT_BETA_VALIDATION_SCRIPT)
beta_round_report_init = load_module("virtual_intelligent_dev_team_beta_round_report_init", INIT_BETA_ROUND_REPORT_SCRIPT)
beta_simulation_init = load_module("virtual_intelligent_dev_team_beta_simulation_init", INIT_BETA_SIMULATION_SCRIPT)
beta_simulation_preview = load_module("virtual_intelligent_dev_team_beta_simulation_preview", PREVIEW_BETA_SIMULATION_FIXTURE_SCRIPT)
beta_simulation_compare = load_module("virtual_intelligent_dev_team_beta_simulation_compare", COMPARE_BETA_SIMULATION_MANIFESTS_SCRIPT)
beta_simulation_runner = load_module("virtual_intelligent_dev_team_beta_simulation_runner", RUN_BETA_SIMULATION_SCRIPT)
beta_simulation_summary = load_module("virtual_intelligent_dev_team_beta_simulation_summary", SUMMARIZE_BETA_SIMULATION_SCRIPT)
beta_round_evaluator = load_module("virtual_intelligent_dev_team_beta_round_evaluator", EVALUATE_BETA_ROUND_SCRIPT)
technical_governance_init = load_module("virtual_intelligent_dev_team_technical_governance_init", INIT_TECHNICAL_GOVERNANCE_SCRIPT)
post_release_feedback_init = load_module("virtual_intelligent_dev_team_post_release_feedback_init", INIT_POST_RELEASE_FEEDBACK_SCRIPT)
post_release_feedback_evaluator = load_module("virtual_intelligent_dev_team_post_release_feedback_evaluator", EVALUATE_POST_RELEASE_FEEDBACK_SCRIPT)
auto_workflow = load_module("virtual_intelligent_dev_team_auto_workflow", RUN_AUTO_WORKFLOW_SCRIPT)
automation_state_inspector = load_module(
    "virtual_intelligent_dev_team_inspect_automation_state",
    INSPECT_AUTOMATION_STATE_SCRIPT,
)
automation_state_resumer = load_module(
    "virtual_intelligent_dev_team_resume_from_automation_state",
    RESUME_FROM_AUTOMATION_STATE_SCRIPT,
)
response_pack = load_module("virtual_intelligent_dev_team_response_pack", GENERATE_RESPONSE_PACK_SCRIPT)
response_contract = load_module("virtual_intelligent_dev_team_response_contract", RESPONSE_CONTRACT_SCRIPT)
verify_action = load_module("virtual_intelligent_dev_team_verify_action", VERIFY_ACTION_SCRIPT)
contract_lint = load_module("virtual_intelligent_dev_team_contract_lint", CONTRACT_LINT_SCRIPT)


def load_config() -> dict[str, object]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)
    config["governance"]["fast_track_control"]["write_event_log"] = False
    return config


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )


def configure_repo(repo: Path) -> None:
    git("config", "user.name", "Codex Test", cwd=repo)
    git("config", "user.email", "codex@example.com", cwd=repo)


def assert_field_expectation(
    testcase: unittest.TestCase,
    expectation: str,
    data: object,
    *,
    label: str,
) -> None:
    ok, detail = benchmark_runner.parse_field_expectation(
        expectation,
        data,
        context_label=label,
    )
    testcase.assertTrue(ok, detail)


@contextmanager
def make_tempdir():
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"tmp-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    yield str(path)


def write_beta_gate_fixture(
    root: Path,
    *,
    round_id: str,
    decision: str,
    reason: str,
    follow_up_extra: dict[str, object] | None = None,
) -> Path:
    output_dir = root / "round-decisions" / round_id
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": "2026-04-08T12:00:00Z",
        "skill_name": "virtual-intelligent-dev-team",
        "ok": decision == "advance",
        "decision": decision,
        "reason": reason,
        "round_id": round_id,
        "report_path": str(root / "reports" / f"{round_id}.json"),
        "observed": {
            "planned_sample_size": 12,
            "completed_sessions": 12,
            "success_rate": 0.75 if decision != "advance" else 0.92,
            "blocker_issue_count": 1 if decision == "hold" else 0,
            "critical_issue_count": 1 if decision == "escalate" else 0,
            "high_severity_issue_count": 1 if decision != "advance" else 0,
            "top_feedback_themes": ["onboarding confusion"],
        },
        "thresholds": {
            "min_completed_sessions": 10,
            "min_success_rate": 0.8,
            "max_blocker_issue_count": 0,
            "max_critical_issue_count": 0,
        },
        "follow_up": {
            "next_action": "hold expansion and resolve beta blockers" if decision != "advance" else "expand to next cohort",
            "continue_beta": decision == "advance",
            "release_governance_recommended": decision == "escalate",
            "next_round_recommended": None if decision == "escalate" else ("round-03" if decision == "advance" else round_id),
        },
        "blocker_breakdown": {
            "by_persona": [
                {
                    "label": "First-Time Novice",
                    "session_count": 4,
                    "blocker_issue_count": 1 if decision == "hold" else 0,
                    "critical_issue_count": 1 if decision == "escalate" else 0,
                    "high_severity_issue_count": 1 if decision != "advance" else 0,
                    "session_ids": ["session-01", "session-02"],
                    "top_feedback_themes": ["onboarding confusion"],
                }
            ],
            "by_scenario": [
                {
                    "label": "first meaningful task",
                    "session_count": 4,
                    "blocker_issue_count": 1 if decision == "hold" else 0,
                    "critical_issue_count": 1 if decision == "escalate" else 0,
                    "high_severity_issue_count": 1 if decision != "advance" else 0,
                    "session_ids": ["session-01", "session-02"],
                    "top_feedback_themes": ["onboarding confusion"],
                }
            ],
        },
        "json_report": str(output_dir / "beta-round-gate-result.json"),
        "markdown_report": str(output_dir / "beta-round-gate-report.md"),
    }
    if isinstance(follow_up_extra, dict):
        payload["follow_up"].update(follow_up_extra)
    fixture_path = output_dir / "beta-round-gate-result.json"
    fixture_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "beta-round-gate-report.md").write_text("# Beta Gate\n", encoding="utf-8")
    response_contract.validate_beta_round_gate_result(payload)
    return fixture_path


def write_beta_manifest(
    root: Path,
    *,
    round_id: str,
    phase: str,
    objective: str,
    sessions: list[dict[str, str]],
) -> Path:
    output_dir = root / ".skill-beta" / "fixture-previews" / round_id
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "beta-simulation-manifest/v1",
        "generated_at": "2026-04-08T12:00:00Z",
        "skill_name": "virtual-intelligent-dev-team",
        "round_id": round_id,
        "phase": phase,
        "objective": objective,
        "config_path": str(root / ".skill-beta" / "simulation-configs" / f"{round_id}.json"),
        "cohort_fixture_source": "references/simulation-cohort-fixtures.json",
        "trace_catalog_source": "references/simulation-trace-catalog.json",
        "sessions": sessions,
        "json_report": str(output_dir / "beta-simulation-manifest.json"),
        "markdown_report": str(output_dir / "beta-simulation-manifest.md"),
    }
    response_contract.validate_beta_simulation_manifest(payload)
    manifest_path = output_dir / "beta-simulation-manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "beta-simulation-manifest.md").write_text("# Fixture Manifest\n", encoding="utf-8")
    return manifest_path


def write_beta_cohort_plan(root: Path, *, rounds: list[dict[str, object]]) -> Path:
    plan_path = root / ".skill-beta" / "cohort-plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "beta-cohort-plan/v1",
        "skill_name": "virtual-intelligent-dev-team",
        "rounds": rounds,
    }
    response_contract.validate_beta_cohort_plan(payload)
    plan_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan_path


def write_beta_ramp_plan(root: Path, *, rounds: list[dict[str, object]]) -> Path:
    plan_path = root / ".skill-beta" / "ramp-plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "beta-ramp-plan/v1",
        "skill_name": "virtual-intelligent-dev-team",
        "rounds": rounds,
    }
    response_contract.validate_beta_ramp_plan(payload)
    plan_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan_path


def write_beta_fixture_diff(
    root: Path,
    *,
    previous_round_id: str,
    current_round_id: str,
    previous_session_count: int,
    current_session_count: int,
    previous_persona_count: int,
    current_persona_count: int,
    previous_scenario_count: int,
    current_scenario_count: int,
    previous_trace_count: int,
    current_trace_count: int,
) -> Path:
    diff_dir = root / ".skill-beta" / "fixture-diffs" / f"{previous_round_id}-to-{current_round_id}"
    diff_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "beta-simulation-diff/v1",
        "generated_at": "2026-04-08T12:00:00Z",
        "skill_name": "virtual-intelligent-dev-team",
        "previous_round_id": previous_round_id,
        "current_round_id": current_round_id,
        "previous_manifest_path": str(root / ".skill-beta" / "fixture-previews" / previous_round_id / "beta-simulation-manifest.json"),
        "current_manifest_path": str(root / ".skill-beta" / "fixture-previews" / current_round_id / "beta-simulation-manifest.json"),
        "previous_session_count": previous_session_count,
        "current_session_count": current_session_count,
        "session_count_delta": current_session_count - previous_session_count,
        "added_personas": [],
        "removed_personas": [],
        "added_scenarios": [],
        "removed_scenarios": [],
        "added_traces": [],
        "removed_traces": [],
        "new_session_matrix": [],
        "coverage_shift_summary": {
            "previous_persona_count": previous_persona_count,
            "current_persona_count": current_persona_count,
            "previous_scenario_count": previous_scenario_count,
            "current_scenario_count": current_scenario_count,
            "previous_trace_count": previous_trace_count,
            "current_trace_count": current_trace_count,
            "new_session_matrix_count": 0,
            "expansion_mode": "expanded",
        },
        "risk_notes": ["Coverage expanded while preserving the previous baseline."],
        "expansion_ok": True,
        "review_required": False,
        "json_report": str(diff_dir / "beta-simulation-diff.json"),
        "markdown_report": str(diff_dir / "beta-simulation-diff.md"),
    }
    response_contract.validate_beta_simulation_diff(payload)
    diff_path = diff_dir / "beta-simulation-diff.json"
    diff_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (diff_dir / "beta-simulation-diff.md").write_text("# Diff\n", encoding="utf-8")
    return diff_path


class RoutingTests(unittest.TestCase):
    def test_review_java_routes_to_code_audit_with_java_assistant(self) -> None:
        result = route_request.route_request(
            "请 review 这个 Java GC 问题并给出建议",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Java Virtuoso", result["assistant_agents"])
        self.assertEqual("audit-fix-deliver", result["workflow_bundle"])
        self.assertGreaterEqual(result["bundle_confidence"], 0.8)
        self.assertIn(".skill-iterations/current-round-memory.md", result["resume_artifacts"])
        self.assertEqual(
            "Code Audit Council",
            (result["reason"]["priority_routing"] or {}).get("agent"),
        )

    def test_pr_audit_does_not_trigger_git_workflow(self) -> None:
        result = route_request.route_request(
            "这是 PR，帮我做安全审计和重构建议",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertFalse(result["needs_git_workflow"])
        self.assertEqual([], result["assistant_agents"])
        self.assertEqual([], result["process_skills"])
        self.assertEqual("audit-fix-deliver", result["workflow_bundle"])

    def test_ui_review_stays_with_product_architect(self) -> None:
        result = route_request.route_request(
            "给 React 页面做 UI review",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIsNone(result["reason"]["priority_routing"])

    def test_checkout_ux_audit_stays_with_product_architect(self) -> None:
        result = route_request.route_request(
            "Audit this checkout UX for accessibility and mobile responsiveness.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertFalse(result["needs_git_workflow"])
        self.assertEqual([], result["process_skills"])

    def test_worktree_plan_uses_repo_base_branch(self) -> None:
        plan = route_request.build_process_plan(
            needs_iteration=False,
            needs_worktree=True,
            needs_git_workflow=False,
            repo_strategy={"strategy": "trunk-master", "base_branch": "master"},
        )

        self.assertEqual(
            "git worktree add ../wt-<task> -b <branch> master",
            plan[0]["commands"][1],
        )

    def test_git_workflow_plan_checks_before_sync_and_push(self) -> None:
        plan = route_request.build_process_plan(
            needs_iteration=False,
            needs_worktree=False,
            needs_git_workflow=True,
            repo_strategy={"strategy": "trunk-master", "base_branch": "master"},
        )
        commands = plan[0]["commands"]

        self.assertLess(
            commands.index("python scripts/git_workflow_guardrail.py --repo . --stage G3 --pretty"),
            commands.index("git pull --rebase origin master"),
        )
        self.assertLess(
            commands.index("python scripts/git_workflow_guardrail.py --repo . --stage G4 --pretty"),
            commands.index("git push -u origin feat/<ticket>-<summary>"),
        )

    def test_bounded_iteration_process_only_routes_to_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Run another iteration, benchmark it against the baseline, and stop if the result regresses.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertTrue(result["needs_iteration"])
        self.assertIn("bounded-iteration", result["process_skills"])
        self.assertTrue(result["iteration_profile"]["enabled"])
        self.assertGreaterEqual(result["iteration_profile"]["round_cap_offline"], 120)
        self.assertEqual("root-cause-remediate", result["workflow_bundle"])
        self.assertEqual(
            ".skill-iterations/current-round-memory.md",
            result["progress_anchor_recommended"],
        )

    def test_large_scale_rewrite_enables_pre_development_planning(self) -> None:
        result = route_request.route_request(
            "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertTrue(result["needs_pre_development_planning"])
        self.assertIn("pre-development-planning", result["process_skills"])
        self.assertEqual("plan-first-build", result["workflow_bundle"])
        self.assertEqual(0.96, result["bundle_confidence"])
        self.assertEqual("docs/progress/MASTER.md", result["progress_anchor_recommended"])
        self.assertIn("docs/progress/MASTER.md", result["resume_artifacts"])
        self.assertEqual("pre-development-planning", result["process_plan"][0]["skill"])
        self.assertIn(
            "python scripts/init_pre_development_plan.py --root . --task-name \"<task-name>\" --task-description \"<task-description>\" --phase-name foundation --pretty",
            result["process_plan"][0]["commands"],
        )
        self.assertIn("docs/progress/phase-4-cutover.md", result["process_plan"][0]["artifacts"])

    def test_chinese_research_first_migration_keeps_planning_branch_with_sentinel(self) -> None:
        result = route_request.route_request(
            "这个核心模块要大规模迁移，先调研再执行，先规划再开发。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Sentinel Architect (NB)", result["lead_agent"])
        self.assertTrue(result["needs_pre_development_planning"])
        self.assertIn("pre-development-planning", result["process_skills"])
        self.assertEqual("plan-first-build", result["workflow_bundle"])

    def test_frontend_iteration_keeps_semantic_lead(self) -> None:
        result = route_request.route_request(
            "Iterate on the React dashboard UX, benchmark the variants, and keep improving until stable.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertTrue(result["needs_iteration"])
        self.assertEqual(["bounded-iteration"], result["process_skills"])
        self.assertEqual("root-cause-remediate", result["workflow_bundle"])

    def test_product_iteration_keeps_semantic_lead(self) -> None:
        result = route_request.route_request(
            "Iterate on the onboarding flow and acceptance criteria, benchmark the variants, and stop if the new round regresses.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertTrue(result["needs_iteration"])

    def test_unknown_request_low_confidence_keeps_no_assistants(self) -> None:
        result = route_request.route_request(
            "Help me figure out what to do with this requirement.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertEqual(0.0, result["confidence"])
        self.assertEqual("en", result["request_language"])
        self.assertIsNotNone(result["clarifying_question"])

    def test_process_only_release_gate_low_confidence_keeps_no_assistants(self) -> None:
        result = route_request.route_request(
            "Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertIn("release-gate", result["process_skills"])
        self.assertEqual([], result["assistant_agents"])
        self.assertEqual(0.0, result["confidence"])
        self.assertEqual("en", result["request_language"])
        self.assertIsNone(result["clarifying_question"])

    def test_release_readiness_routes_to_formal_release_gate_without_git_workflow(self) -> None:
        result = route_request.route_request(
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertTrue(result["needs_release_gate"])
        self.assertFalse(result["needs_git_workflow"])
        self.assertIn("release-gate", result["process_skills"])
        self.assertEqual("ship-hold-remediate", result["workflow_bundle"])
        self.assertEqual(
            "evals/release-gate/release-gate-report.md",
            result["progress_anchor_recommended"],
        )
        self.assertFalse(result["assistant_delta_contract"]["enabled"])

    def test_assistant_delta_contract_is_enabled_when_assistants_exist(self) -> None:
        result = route_request.route_request(
            "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertTrue(result["assistant_delta_contract"]["enabled"])
        self.assertEqual("World-Class Product Architect", result["assistant_delta_contract"]["lead_owner"])
        self.assertIn("Technical Trinity", result["assistant_delta_contract"]["assistants"])
        self.assertIn("claim", result["assistant_delta_contract"]["required_fields"])
        self.assertIn("evidence", result["assistant_delta_contract"]["required_fields"])
        self.assertIn("next_action", result["assistant_delta_contract"]["by_agent"]["Technical Trinity"])

    def test_chinese_release_readiness_suppresses_ambiguous_git_submit_signal(self) -> None:
        result = route_request.route_request(
            "这版现在能不能提交/发版？不要只看 benchmark，通过正式 release gate 做提交前验收。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertTrue(result["needs_release_gate"])
        self.assertFalse(result["needs_git_workflow"])
        self.assertIn("release-gate", result["process_skills"])

    def test_bounded_iteration_plan_includes_validation_and_benchmark_commands(self) -> None:
        plan = route_request.build_process_plan(
            needs_iteration=True,
            needs_worktree=False,
            needs_git_workflow=False,
            repo_strategy={"strategy": "trunk-main", "base_branch": "main"},
        )
        commands = plan[0]["commands"]

        self.assertIn(
            "python scripts/init_project_memory.py --root . --mode iteration --pretty",
            commands,
        )
        self.assertIn(
            "mkdir -p .skill-iterations",
            commands,
        )
        self.assertIn(
            "cp assets/iteration-plan-template.json .skill-iterations/iteration-plan.json",
            commands,
        )
        self.assertIn(
            "python scripts/register_benchmark_baseline.py --workspace .skill-iterations --label stable --report <baseline-report> --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/run_iteration_cycle.py --workspace .skill-iterations --round-id round-01 --objective \"<goal>\" --baseline-label stable --owner \"<lead-owner>\" --candidate \"<candidate-change>\" --candidate-worktree ../wt-round-01 --candidate-output-dir .tmp-iteration-round-01 --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/compare_benchmark_results.py --baseline .skill-iterations/baselines/stable/benchmark-results.json --candidate .tmp-iteration-round-01/benchmark-results.json --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/promote_iteration_baseline.py --workspace .skill-iterations --round-id round-01 --label accepted-round-01 --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/sync_distilled_patterns.py --workspace .skill-iterations --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/materialize_candidate_patch.py --brief .skill-iterations/candidate-briefs/round-01.json --candidate-root ../wt-round-01 --patch-output .skill-iterations/patches/round-01.patch --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.json --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.json --resume --pretty",
            commands,
        )
        self.assertEqual(".skill-iterations/current-round-memory.md", plan[0]["resume_anchor"])
        self.assertIn(".skill-iterations/distilled-patterns.md", plan[0]["resume_artifacts"])

    def test_release_gate_plan_includes_formal_ship_hold_gate(self) -> None:
        plan = route_request.build_process_plan(
            needs_iteration=False,
            needs_worktree=False,
            needs_release_gate=True,
            needs_git_workflow=False,
            repo_strategy={"strategy": "trunk-main", "base_branch": "main"},
        )
        commands = plan[0]["commands"]

        self.assertIn(
            "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/run_release_gate.py --output-dir evals/release-gate --previous-output evals/benchmark-results/benchmark-results.json --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --release-label release-ready --pretty",
            commands,
        )
        self.assertIn(
            "python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --auto-run-next-iteration-on-hold --hold-loop-max-rounds 3 --pretty",
            commands,
        )
        self.assertEqual("evals/release-gate/release-gate-report.md", plan[0]["resume_anchor"])
        self.assertIn("evals/release-gate/next-iteration-brief.json", plan[0]["resume_artifacts"])

    def test_pre_development_plan_initializes_project_memory_anchor(self) -> None:
        plan = route_request.build_process_plan(
            needs_pre_development_planning=True,
            needs_iteration=False,
            needs_worktree=False,
            needs_release_gate=False,
            needs_git_workflow=False,
            repo_strategy={"strategy": "trunk-main", "base_branch": "main"},
        )
        commands = plan[0]["commands"]

        self.assertIn(
            "python scripts/init_project_memory.py --root . --mode planning --pretty",
            commands,
        )

    def test_rebase_conflict_adds_sentinel_assistant(self) -> None:
        result = route_request.route_request(
            "解决 rebase 冲突并给出最稳妥处理路径",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertIn("Sentinel Architect (NB)", result["assistant_agents"])

    def test_product_scope_request_adds_technical_trinity_copilot(self) -> None:
        result = route_request.route_request(
            "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertNotEqual("模式 A：单点执行", result["mode"])
        self.assertEqual("product-spec-deliver", result["workflow_bundle"])
        self.assertTrue(result["workflow_bundle_bootstrap"]["required"])
        self.assertIn(
            "python scripts/init_product_delivery.py --root . --pretty",
            result["workflow_bundle_bootstrap"]["commands"],
        )

    def test_beta_validation_request_routes_to_product_beta_bundle(self) -> None:
        result = route_request.route_request(
            "这个产品开发前后都要做内测，分三轮递增用户，并模拟不同类型的内测用户来收集反馈。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual("beta-feedback-ramp", result["workflow_bundle"])
        self.assertTrue(result["workflow_bundle_bootstrap"]["required"])
        self.assertIn(
            "python scripts/init_beta_validation.py --root . --pretty",
            result["workflow_bundle_bootstrap"]["commands"],
        )
        self.assertIn(
            "python scripts/init_beta_simulation.py --root . --round-id round-0 --phase \"pre-build concept smoke\" --objective \"<objective>\" --pretty",
            result["workflow_bundle_bootstrap"]["commands"],
        )
        self.assertIn(
            ".skill-beta/simulation-configs/round-0.json",
            result["workflow_bundle_bootstrap"]["artifacts"],
        )
        beta_plan = result["beta_validation_plan"]
        self.assertTrue(beta_plan["enabled"])
        self.assertTrue(beta_plan["simulation_allowed"])
        self.assertEqual(".skill-beta/feedback-ledger.md", beta_plan["feedback_anchor"])
        self.assertEqual("assets/beta-cohort-plan-template.json", beta_plan["cohort_plan_template"])
        self.assertEqual("references/beta-cohort-plan.schema.json", beta_plan["cohort_plan_schema"])
        self.assertEqual(".skill-beta/cohort-plan.json", beta_plan["cohort_plan_path"])
        self.assertEqual("assets/beta-ramp-plan-template.json", beta_plan["ramp_plan_template"])
        self.assertEqual("references/beta-ramp-plan.schema.json", beta_plan["ramp_plan_schema"])
        self.assertEqual(".skill-beta/ramp-plan.json", beta_plan["ramp_plan_path"])
        self.assertEqual("assets/simulated-user-profile-template.json", beta_plan["simulation_profile_template"])
        self.assertEqual(".skill-beta/personas", beta_plan["simulation_profile_dir"])
        self.assertEqual("references/simulation-persona-library.json", beta_plan["simulation_persona_library"])
        self.assertEqual("references/simulation-cohort-fixtures.json", beta_plan["simulation_cohort_fixtures"])
        self.assertEqual("assets/beta-simulation-config-template.json", beta_plan["simulation_config_template"])
        self.assertEqual(".skill-beta/simulation-configs", beta_plan["simulation_config_dir"])
        self.assertEqual("references/simulation-scenario-packs.json", beta_plan["simulation_scenario_packs"])
        self.assertEqual("references/simulation-trace-catalog.json", beta_plan["simulation_trace_catalog"])
        self.assertEqual(".skill-beta/fixture-previews", beta_plan["simulation_preview_dir"])
        self.assertEqual(".skill-beta/fixture-diffs", beta_plan["simulation_diff_dir"])
        self.assertEqual(".skill-beta/simulation-runs", beta_plan["simulation_run_dir"])
        self.assertIn("python scripts/init_beta_simulation.py", beta_plan["simulation_init_command_template"])
        self.assertIn("python scripts/preview_beta_simulation_fixture.py", beta_plan["simulation_preview_command_template"])
        self.assertIn("python scripts/compare_beta_simulation_manifests.py", beta_plan["simulation_diff_command_template"])
        self.assertIn("python scripts/run_beta_simulation.py", beta_plan["simulation_run_command_template"])
        self.assertIn("python scripts/summarize_beta_simulation.py", beta_plan["simulation_summary_command_template"])
        self.assertEqual("assets/beta-round-report-template.json", beta_plan["report_template"])
        self.assertEqual(".skill-beta/reports", beta_plan["report_dir"])
        self.assertEqual(".skill-beta/round-decisions", beta_plan["decision_dir"])
        self.assertIn("python scripts/evaluate_beta_round.py", beta_plan["gate_command_template"])
        self.assertEqual(3, len(beta_plan["rounds"]))

    def test_auto_root_cause_request_exposes_auto_profile(self) -> None:
        result = route_request.route_request(
            "/auto fix this repeated regression until stable and keep benchmark evidence",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertTrue(result["auto_mode_enabled"])
        self.assertEqual("/auto", result["auto_mode_source"])
        self.assertEqual("auto-setup", result["execution_mode"])
        self.assertEqual("root-cause-remediate", result["workflow_bundle"])
        auto_profile = result["auto_run_profile"]
        self.assertTrue(auto_profile["workflow_supported"])
        self.assertEqual("setup", auto_profile["requested_phase"])
        self.assertIn("root-cause-remediate", auto_profile["eligible_workflows"])
        bounded_iteration_entry = next(
            item for item in result["process_plan"] if item["skill"] == "bounded-iteration"
        )
        self.assertEqual("setup", bounded_iteration_entry["auto_run"]["requested_phase"])
        self.assertIn("python scripts/run_auto_workflow.py", bounded_iteration_entry["auto_run"]["setup_command"])

    def test_auto_background_request_marks_detached_resume_contract(self) -> None:
        result = route_request.route_request(
            "/auto background fix this repeated regression until stable and keep benchmark evidence",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertTrue(result["auto_mode_enabled"])
        self.assertEqual("auto-setup", result["execution_mode"])
        self.assertEqual("background", result["auto_run_profile"]["run_style"])
        self.assertTrue(result["auto_run_profile"]["detached_ready"])
        bounded_iteration_entry = next(
            item for item in result["process_plan"] if item["skill"] == "bounded-iteration"
        )
        self.assertEqual("background", bounded_iteration_entry["auto_run"]["run_style"])
        self.assertTrue(bounded_iteration_entry["auto_run"]["detached_ready"])

    def test_auto_safe_request_clamps_stop_caps(self) -> None:
        result = route_request.route_request(
            "/auto safe Is this version ready to ship? Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertTrue(result["auto_mode_enabled"])
        self.assertEqual("safe", result["auto_run_profile"]["safety_level"])
        self.assertEqual(1, result["auto_run_profile"]["stop_caps"]["release_hold_loop_max_rounds"])
        self.assertIn(
            "safe mode clamps automation to a single bounded pass before any further escalation",
            result["auto_run_profile"]["safety_guards"],
        )

    def test_auto_resume_go_request_marks_resume_profile(self) -> None:
        result = route_request.route_request(
            "/auto resume go fix this repeated regression until stable and keep benchmark evidence",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertTrue(result["auto_mode_enabled"])
        self.assertEqual("go", result["auto_run_profile"]["requested_phase"])
        self.assertTrue(result["auto_run_profile"]["resume_requested"])

    def test_auto_resume_request_prefers_latest_automation_state_when_available(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto background safe fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )

            result = route_request.route_request(
                "/auto resume background safe fix this repeated regression until stable and keep benchmark evidence",
                load_config(),
                repo_path=root,
            )

            self.assertTrue(result["auto_run_profile"]["resume_requested"])
            self.assertEqual("state-first", result["auto_run_profile"]["resume_strategy"])
            self.assertTrue(result["auto_run_profile"]["state_resume_available"])
            self.assertEqual(
                "resume-explicit-go",
                result["auto_run_profile"]["state_resume_decision_id"],
            )
            self.assertIn(
                "resume_from_automation_state.py",
                result["auto_run_profile"]["state_resume_dry_run_command"],
            )

    def test_auto_release_go_request_requires_saved_plan(self) -> None:
        result = route_request.route_request(
            "/auto go Is this version ready to ship? Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertTrue(result["auto_mode_enabled"])
        self.assertEqual("auto-go", result["execution_mode"])
        self.assertEqual("ship-hold-remediate", result["workflow_bundle"])
        self.assertEqual("go", result["auto_run_profile"]["requested_phase"])
        self.assertTrue(result["auto_run_profile"]["workflow_supported"])
        release_entry = next(item for item in result["process_plan"] if item["skill"] == "release-gate")
        self.assertEqual("go", release_entry["auto_run"]["requested_phase"])

    def test_auto_post_release_request_adds_post_release_process_plan_entry(self) -> None:
        result = route_request.route_request(
            "/auto The release is already live; absorb telemetry and support signals.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("post-release-close-loop", result["workflow_bundle"])
        self.assertTrue(result["auto_run_profile"]["workflow_supported"])
        post_release_entry = next(
            item for item in result["process_plan"] if item["skill"] == "post-release-feedback"
        )
        self.assertEqual(
            "references/post-release-feedback-playbook.md",
            post_release_entry["reference"],
        )
        self.assertIn(
            "python scripts/evaluate_post_release_feedback.py --report .skill-post-release/current-signals.json --pretty",
            post_release_entry["commands"],
        )

    def test_governance_request_routes_to_git_guardian_bundle(self) -> None:
        result = route_request.route_request(
            "Define the rollback plan and branch delivery flow for this core refactor.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertEqual("govern-change-safely", result["workflow_bundle"])
        self.assertTrue(result["workflow_bundle_bootstrap"]["required"])
        self.assertIn(
            "python scripts/init_technical_governance.py --root . --pretty",
            result["workflow_bundle_bootstrap"]["commands"],
        )

    def test_python_fastapi_routes_to_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Use Python and FastAPI to build a backend service.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertIn("python", result["detected_languages"])
        self.assertFalse(result["needs_git_workflow"])

    def test_python_django_review_routes_to_audit_with_python_assistant(self) -> None:
        result = route_request.route_request(
            "Review this Django API for security issues.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertEqual(
            "Code Audit Council",
            (result["reason"]["priority_routing"] or {}).get("agent"),
        )

    def test_python_flask_git_workflow_routes_to_git_guardian(self) -> None:
        result = route_request.route_request(
            "Refactor this Flask service and then commit and push the branch.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertIn("git-workflow", result["process_skills"])

    def test_python_celery_design_routes_to_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Design a Python service with Celery workers and reliability guardrails.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertIn("python", result["detected_languages"])
        self.assertFalse(result["needs_git_workflow"])

    def test_python_pr_audit_keeps_audit_lead_with_git_and_python_assistants(self) -> None:
        result = route_request.route_request(
            "This is a PR. Review this Django service for security issues before merge.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Git Workflow Guardian", result["assistant_agents"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
    def test_python_fastapi_worktree_and_git_routes_to_git_guardian(self) -> None:
        result = route_request.route_request(
            "Use FastAPI for a backend service, then commit, push, and isolate the work in a worktree.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertTrue(result["needs_worktree"])
        self.assertIn("using-git-worktrees", result["process_skills"])
        self.assertIn("git-workflow", result["process_skills"])

    def test_go_gin_design_routes_to_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Design a Go service with Gin and improve concurrency.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertIn("go", result["detected_languages"])
        self.assertFalse(result["needs_git_workflow"])

    def test_go_pr_audit_review_keeps_audit_lead(self) -> None:
        result = route_request.route_request(
            "Review this Go API for security issues before merge.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertEqual(
            "Code Audit Council",
            (result["reason"]["priority_routing"] or {}).get("agent"),
        )

    def test_go_gin_worktree_and_git_routes_to_git_guardian(self) -> None:
        result = route_request.route_request(
            "Use Go with Gin, then commit, push, and isolate the work in a worktree.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertTrue(result["needs_worktree"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertIn("using-git-worktrees", result["process_skills"])
        self.assertIn("git-workflow", result["process_skills"])

    def test_node_nest_design_routes_to_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Design a Node.js service with NestJS.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Technical Trinity", result["lead_agent"])
        self.assertIn("nodejs", result["detected_languages"])
        self.assertFalse(result["needs_git_workflow"])

    def test_node_pr_audit_review_adds_node_assistant(self) -> None:
        result = route_request.route_request(
            "Review this NestJS API for security issues before merge.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertTrue(result["needs_git_workflow"])

    def test_node_nest_worktree_and_git_routes_to_git_guardian(self) -> None:
        result = route_request.route_request(
            "Use Node.js with NestJS, then commit, push, and isolate the work in a worktree.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertTrue(result["needs_worktree"])
        self.assertTrue(result["needs_git_workflow"])

    def test_frontend_react_redesign_stays_with_product_architect(self) -> None:
        result = route_request.route_request(
            "Redesign this React dashboard UI and improve the interaction flow.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_dashboard_responsive_routes_to_product_architect(self) -> None:
        result = route_request.route_request(
            "Redesign this analytics dashboard for mobile responsiveness and better information hierarchy.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_next_shadcn_design_routes_to_product_architect(self) -> None:
        result = route_request.route_request(
            "Design a Next.js admin console with shadcn/ui and Tailwind.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_motion_design_routes_to_product_architect(self) -> None:
        result = route_request.route_request(
            "Improve the Framer Motion transitions and loading states in this React onboarding flow.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_form_ux_accessibility_routes_to_product_architect(self) -> None:
        result = route_request.route_request(
            "Audit this signup form UX for accessibility, validation, and conversion friction.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_backend_contract_adds_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Redesign this React admin page and align the frontend flow with the backend API contract.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_auth_api_error_states_adds_technical_trinity(self) -> None:
        result = route_request.route_request(
            "Redesign the login flow, align auth UX with the backend API, and handle error states clearly.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_chinese_next_tailwind_routes_to_product_architect(self) -> None:
        result = route_request.route_request(
            "用 Next.js 和 Tailwind 重做这个后台页面的交互和视觉层次。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_chinese_form_api_feedback_adds_technical_trinity(self) -> None:
        result = route_request.route_request(
            "优化这个表单的错误提示、空状态和接口失败反馈，并和后端 API 契约对齐。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_git_dashboard_mixed_request_keeps_product_lead_with_git_assistant(self) -> None:
        result = route_request.route_request(
            "帮我提个 commit 然后 push，那个 dashboard 也顺手改下。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Git Workflow Guardian", result["assistant_agents"])
        self.assertTrue(result["needs_git_workflow"])

    def test_product_colloquial_contract_request_adds_technical_trinity(self) -> None:
        result = route_request.route_request(
            "把这个注册流程需求拆一下，验收标准和接口契约也一起落一下。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_review_nest_auth_flow_adds_technical_trinity(self) -> None:
        result = route_request.route_request(
            "review 下这个 nest 接口，顺便看下 auth flow。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_review_djagno_form_api_contract_adds_technical_trinity(self) -> None:
        result = route_request.route_request(
            "给这个 djagno 登录表单做个 ux review，并和后端 api 对齐。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Technical Trinity", result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_frontend_tailwind_git_worktree_routes_to_product_lead_with_git_assistant(self) -> None:
        result = route_request.route_request(
            "Improve the Tailwind admin UI, then commit, push, and isolate the work in a worktree.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("World-Class Product Architect", result["lead_agent"])
        self.assertIn("Git Workflow Guardian", result["assistant_agents"])
        self.assertTrue(result["needs_worktree"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertIn("using-git-worktrees", result["process_skills"])
        self.assertIn("git-workflow", result["process_skills"])

    def test_java_spring_design_routes_to_java_virtuoso(self) -> None:
        result = route_request.route_request(
            "Design a Java Spring Boot service for order processing.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Java Virtuoso", result["lead_agent"])
        self.assertEqual([], result["assistant_agents"])
        self.assertFalse(result["needs_git_workflow"])

    def test_java_spring_pr_audit_review_adds_java_and_git_assistants(self) -> None:
        result = route_request.route_request(
            "Review this Spring Boot API for security issues before merge.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Code Audit Council", result["lead_agent"])
        self.assertIn("Java Virtuoso", result["assistant_agents"])
        self.assertIn("Git Workflow Guardian", result["assistant_agents"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertEqual(
            "Code Audit Council",
            (result["reason"]["priority_routing"] or {}).get("agent"),
        )

    def test_java_spring_worktree_and_git_routes_to_git_guardian(self) -> None:
        result = route_request.route_request(
            "Use Java with Spring Boot, then commit, push, and isolate the work in a worktree.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        self.assertEqual("Git Workflow Guardian", result["lead_agent"])
        self.assertIn("Java Virtuoso", result["assistant_agents"])
        self.assertTrue(result["needs_worktree"])
        self.assertTrue(result["needs_git_workflow"])
        self.assertIn("using-git-worktrees", result["process_skills"])
        self.assertIn("git-workflow", result["process_skills"])


class GuardrailTests(unittest.TestCase):
    def test_g0_blocks_preexisting_staged_changes(self) -> None:
        with make_tempdir() as tmp:
            repo = Path(tmp)
            git("init", cwd=repo)
            configure_repo(repo)
            (repo / "demo.txt").write_text("base\n", encoding="utf-8")
            git("add", "demo.txt", cwd=repo)
            git("commit", "-m", "chore: init repo", cwd=repo)
            (repo / "demo.txt").write_text("base\nchange\n", encoding="utf-8")
            git("add", "demo.txt", cwd=repo)

            with self.assertRaisesRegex(RuntimeError, "pre-existing staged changes"):
                guardrail.validate_stage(repo=repo, stage="G0", commit_message=None, max_staged_files=20)

    def test_g3_reports_when_branch_is_behind(self) -> None:
        with make_tempdir() as tmp:
            repo = Path(tmp)
            git("init", cwd=repo)
            configure_repo(repo)
            git("checkout", "-b", "main", cwd=repo)
            (repo / "demo.txt").write_text("v1\n", encoding="utf-8")
            git("add", "demo.txt", cwd=repo)
            git("commit", "-m", "feat: add demo file", cwd=repo)
            base_sha = git("rev-parse", "HEAD", cwd=repo).stdout.strip()

            git("branch", "upstream-main", cwd=repo)
            git("checkout", "upstream-main", cwd=repo)
            (repo / "demo.txt").write_text("v1\nv2\n", encoding="utf-8")
            git("add", "demo.txt", cwd=repo)
            git("commit", "-m", "fix: update demo file", cwd=repo)

            git("checkout", "main", cwd=repo)
            git("reset", "--hard", base_sha, cwd=repo)
            git("branch", "--set-upstream-to=upstream-main", "main", cwd=repo)
            result = guardrail.validate_stage(
                repo=repo,
                stage="G3",
                commit_message=None,
                max_staged_files=20,
            )

            self.assertTrue(result["passed"])
            self.assertEqual(1, result["details"]["behind"])
            self.assertTrue(result["details"]["requires_sync"])


class IterationHelperTests(unittest.TestCase):
    def test_init_pre_development_plan_creates_expected_artifacts(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp) / "planning-root"
            payload = planning_init.initialize_pre_development_plan(
                root=root,
                task_name="Rust Rewrite",
                task_description="Rewrite the monolith into a Rust service stack.",
                phase_name="Foundation",
            )

            master_path = Path(payload["artifacts"]["master"])
            overview_path = Path(payload["artifacts"]["project_overview"])
            phase_path = Path(payload["artifacts"]["phase"])
            phase_files = [Path(item) for item in payload["artifacts"]["phase_files"]]

            self.assertTrue(master_path.exists())
            self.assertTrue(overview_path.exists())
            self.assertTrue(phase_path.exists())
            self.assertEqual(4, payload["phase_count"])
            self.assertEqual(4, len(phase_files))
            self.assertTrue(all(path.exists() for path in phase_files))
            self.assertIn("Rust Rewrite", master_path.read_text(encoding="utf-8"))
            self.assertIn("Architecture", master_path.read_text(encoding="utf-8"))
            self.assertIn("Cutover", master_path.read_text(encoding="utf-8"))
            self.assertIn("Rewrite the monolith into a Rust service stack.", overview_path.read_text(encoding="utf-8"))
            self.assertIn("Phase 1: Foundation", phase_path.read_text(encoding="utf-8"))
            self.assertIn("Phase 4: Cutover", phase_files[-1].read_text(encoding="utf-8"))

    def test_init_iteration_round_creates_expected_assets(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            payload = iteration_init.initialize_round(
                workspace=workspace,
                round_id="round-01",
                objective="improve benchmark stability",
                baseline="v4.2.0",
                owner="Technical Trinity",
                candidate="rebalance routing weights",
            )

            ledger_path = Path(payload["ledger"])
            reflection_path = Path(payload["reflection"])
            round_memory_path = Path(payload["round_memory"])
            self_feedback_path = Path(payload["self_feedback"])
            distilled_path = Path(payload["distilled_patterns"])

            self.assertTrue(ledger_path.exists())
            self.assertTrue(reflection_path.exists())
            self.assertTrue(round_memory_path.exists())
            self.assertTrue(self_feedback_path.exists())
            self.assertTrue(distilled_path.exists())
            self.assertIn("improve benchmark stability", ledger_path.read_text(encoding="utf-8"))
            self.assertIn("rebalance routing weights", reflection_path.read_text(encoding="utf-8"))
            self.assertIn("round-01", round_memory_path.read_text(encoding="utf-8"))

    def test_compare_benchmark_results_returns_keep_for_resolved_failures(self) -> None:
        baseline = {
            "summary": {"overall_passed": False},
            "eval_run": {
                "passed": 53,
                "total": 54,
                "cases": [
                    {"id": 1, "prompt": "a", "passed": False, "failures": ["x"]},
                    {"id": 2, "prompt": "b", "passed": True, "failures": []},
                ],
                "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
            },
        }
        candidate = {
            "summary": {"overall_passed": True},
            "eval_run": {
                "passed": 54,
                "total": 54,
                "cases": [
                    {"id": 1, "prompt": "a", "passed": True, "failures": []},
                    {"id": 2, "prompt": "b", "passed": True, "failures": []},
                ],
                "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
            },
        }

        result = benchmark_compare.compare_results(baseline=baseline, candidate=candidate)
        self.assertEqual("keep", result["decision"])

    def test_compare_benchmark_results_returns_rollback_for_new_failures(self) -> None:
        baseline = {
            "summary": {"overall_passed": True},
            "eval_run": {
                "passed": 54,
                "total": 54,
                "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
            },
        }
        candidate = {
            "summary": {"overall_passed": False},
            "eval_run": {
                "passed": 53,
                "total": 54,
                "cases": [
                    {"id": 1, "prompt": "a", "passed": True, "failures": []},
                    {"id": 2, "prompt": "b", "passed": False, "failures": ["new failure"]},
                ],
                "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
            },
        }

        result = benchmark_compare.compare_results(baseline=baseline, candidate=candidate)
        self.assertEqual("rollback", result["decision"])

    def test_compare_benchmark_load_json_rejects_invalid_report_fixture(self) -> None:
        with make_tempdir() as tmp:
            report = Path(tmp) / "invalid-benchmark.json"
            report.write_text(json.dumps({"summary": {"overall_passed": True}}, ensure_ascii=False), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "benchmark run result schema validation failed"):
                benchmark_compare.load_json(report)

    def test_register_baseline_creates_registry_and_stored_report(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            source_report = workspace / "source.json"
            source_report.parent.mkdir(parents=True, exist_ok=True)
            source_report.write_text(
                json.dumps(
                    {
                        "summary": {"overall_passed": True},
                        "eval_run": {"passed": 54, "total": 54},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=source_report,
                notes="accepted baseline",
            )

            self.assertTrue(Path(result["registry"]).exists())
            self.assertTrue(Path(result["stored_report"]).exists())

    def test_register_baseline_rejects_invalid_report_fixture(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            source_report = workspace / "source.json"
            source_report.parent.mkdir(parents=True, exist_ok=True)
            source_report.write_text(
                json.dumps({"summary": {"overall_passed": True}}, ensure_ascii=False),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "benchmark run result schema validation failed"):
                baseline_registry.register_baseline(
                    workspace=workspace,
                    label="stable",
                    report_path=source_report,
                )

    def test_run_iteration_cycle_writes_state_and_open_loops(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            baseline_report = workspace / "baseline.json"
            candidate_report = workspace / "candidate.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_report.write_text(
                json.dumps(
                    {
                        "summary": {"overall_passed": True},
                        "eval_run": {
                            "passed": 54,
                            "total": 54,
                            "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                            "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            candidate_report.write_text(
                json.dumps(
                    {
                        "summary": {"overall_passed": False},
                        "eval_run": {
                            "passed": 53,
                            "total": 54,
                            "cases": [
                                {"id": 1, "prompt": "a", "passed": True, "failures": []},
                                {"id": 2, "prompt": "b", "passed": False, "failures": ["new failure"]},
                            ],
                            "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=baseline_report,
            )

            result = iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="protect benchmark stability",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="test new routing delta",
                candidate_report=candidate_report,
            )

            self.assertEqual("rollback", result["decision"])
            self.assertTrue(Path(result["state"]).exists())
            self.assertTrue(Path(result["open_loops"]).exists())
            self.assertTrue(Path(result["round_memory"]).exists())
            self.assertTrue(Path(result["self_feedback"]).exists())
            self.assertTrue(Path(result["memory_chain"]).exists())
            self.assertIn("rollback", Path(result["ledger"]).read_text(encoding="utf-8"))
            memory_chain = Path(result["memory_chain"]).read_text(encoding="utf-8")
            self.assertIn("round-01", memory_chain)
            self.assertIn("## Current Open Loops", memory_chain)
            self.assertIn("## Distilled Patterns", memory_chain)

    def test_run_iteration_cycle_promotes_and_syncs_on_keep(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            baseline_report = workspace / "baseline.json"
            candidate_report = workspace / "candidate.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_payload = {
                "summary": {"overall_passed": False},
                "eval_run": {
                    "passed": 53,
                    "total": 54,
                    "cases": [
                        {"id": 1, "prompt": "a", "passed": False, "failures": ["old failure"]},
                        {"id": 2, "prompt": "b", "passed": True, "failures": []},
                    ],
                    "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
                },
            }
            candidate_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [
                        {"id": 1, "prompt": "a", "passed": True, "failures": []},
                        {"id": 2, "prompt": "b", "passed": True, "failures": []},
                    ],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }
            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            candidate_report.write_text(json.dumps(candidate_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=baseline_report,
            )

            result = iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="keep stable benchmark quality",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="retain accepted routing weights",
                candidate_report=candidate_report,
                promote_label="accepted-round-01",
                sync_patterns_enabled=True,
            )

            self.assertTrue(result["promotion_eligible"])
            self.assertEqual("keep", result["decision"])
            self.assertIsNotNone(result["promotion"])
            self.assertIsNotNone(result["pattern_sync"])
            self.assertTrue(Path(result["promotion"]["stored_report"]).exists())
            self.assertTrue(Path(result["pattern_sync"]["distilled_patterns"]).exists())

    def test_run_iteration_cycle_tracks_open_loop_lifecycle_across_rounds(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            baseline_report = workspace / "baseline.json"
            rollback_report = workspace / "rollback.json"
            keep_report = workspace / "keep.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }
            rollback_payload = {
                "summary": {"overall_passed": False},
                "eval_run": {
                    "passed": 53,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": False, "failures": ["new failure"]}],
                    "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
                },
            }
            keep_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }
            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            rollback_report.write_text(json.dumps(rollback_payload, ensure_ascii=False), encoding="utf-8")
            keep_report.write_text(json.dumps(keep_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(workspace=workspace, label="stable", report_path=baseline_report)

            iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="track unresolved loops until a keep closes them",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="introduce regression",
                candidate_report=rollback_report,
            )
            first_open_loops = (workspace / "open-loops.md").read_text(encoding="utf-8")
            self.assertIn("## Active", first_open_loops)
            self.assertIn("[round-01][rollback] candidate benchmark no longer passes overall checks", first_open_loops)
            self.assertIn("## Recently Resolved", first_open_loops)

            iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-02",
                objective="close the unresolved loop after a keep",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="restore accepted baseline",
                candidate_report=keep_report,
            )
            second_open_loops = (workspace / "open-loops.md").read_text(encoding="utf-8")
            self.assertIn("## Active", second_open_loops)
            self.assertIn("## Recently Resolved", second_open_loops)
            self.assertIn("- None.", second_open_loops)
            self.assertIn("resolved-by round-02", second_open_loops)

    def test_run_iteration_cycle_runs_candidate_worktree_benchmarks(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            candidate_repo = Path(tmp) / "candidate-worktree"
            baseline_report = workspace / "baseline.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_payload = {
                "summary": {"overall_passed": False},
                "eval_run": {
                    "passed": 53,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": False, "failures": ["old failure"]}],
                    "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
                },
            }
            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=baseline_report,
            )

            benchmark_script = candidate_repo / "scripts" / "run_benchmarks.py"
            benchmark_script.parent.mkdir(parents=True, exist_ok=True)
            benchmark_script.write_text(
                "import argparse\n"
                "import json\n"
                "from pathlib import Path\n"
                "\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--output-dir', required=True)\n"
                "parser.add_argument('--pretty', action='store_true')\n"
                "args = parser.parse_args()\n"
                "output_dir = Path(args.output_dir)\n"
                "output_dir.mkdir(parents=True, exist_ok=True)\n"
                "payload = {\n"
                "    'summary': {'overall_passed': True},\n"
                "    'eval_run': {\n"
                "        'passed': 54,\n"
                "        'total': 54,\n"
                "        'cases': [{'id': 1, 'prompt': 'a', 'passed': True, 'failures': []}],\n"
                "        'category_breakdown': [{'category': 'iteration', 'passed': 1, 'total': 1}],\n"
                "    },\n"
                "}\n"
                "(output_dir / 'benchmark-results.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')\n"
                "print(json.dumps({'ok': True}, ensure_ascii=False))\n",
                encoding="utf-8",
            )

            result = iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="validate candidate worktree benchmark execution",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="run benchmark from candidate worktree",
                candidate_repo=candidate_repo,
                candidate_output_dir=workspace / "runs" / "round-01",
            )

            state = baseline_registry.load_json(workspace / "round-01" / "state.json")
            self.assertEqual("keep", result["decision"])
            self.assertTrue(Path(result["candidate_report"]).exists())
            self.assertEqual(str(candidate_repo.resolve()), result["candidate_repo"])
            self.assertEqual(str(candidate_repo.resolve()), state["candidate_repo"])

    def test_run_iteration_cycle_supports_custom_benchmark_command(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            candidate_repo = Path(tmp) / "candidate-repo"
            baseline_report = workspace / "baseline.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_payload = {
                "summary": {"overall_passed": False},
                "eval_run": {
                    "passed": 53,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": False, "failures": ["old failure"]}],
                    "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
                },
            }
            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=baseline_report,
            )
            candidate_repo.mkdir(parents=True, exist_ok=True)

            benchmark_command = (
                "python -c \"import json, pathlib; "
                "out = pathlib.Path(r'{output_dir}'); "
                "out.mkdir(parents=True, exist_ok=True); "
                "payload = {'summary': {'overall_passed': True}, 'eval_run': {'passed': 54, 'total': 54, "
                "'cases': [{'id': 1, 'prompt': 'a', 'passed': True, 'failures': []}], "
                "'category_breakdown': [{'category': 'iteration', 'passed': 1, 'total': 1}]}}; "
                "(out / 'benchmark-results.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')\""
            )

            result = iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="validate custom benchmark command",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="use a repo-specific benchmark entrypoint",
                candidate_repo=candidate_repo,
                benchmark_command=benchmark_command,
            )

            state = baseline_registry.load_json(workspace / "round-01" / "state.json")
            self.assertEqual("keep", result["decision"])
            self.assertEqual(benchmark_command, result["benchmark_command"])
            self.assertEqual(benchmark_command, state["benchmark_command"])

    def test_run_iteration_cycle_applies_and_rolls_back_workspace_with_snapshots(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            candidate_repo = Path(tmp) / "candidate-repo"
            baseline_report = workspace / "baseline.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }
            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=baseline_report,
            )

            candidate_repo.mkdir(parents=True, exist_ok=True)
            git("init", cwd=candidate_repo)
            configure_repo(candidate_repo)
            tracked_file = candidate_repo / "candidate.txt"
            tracked_file.write_text("base\n", encoding="utf-8")
            git("add", "candidate.txt", cwd=candidate_repo)
            git("commit", "-m", "chore: init candidate", cwd=candidate_repo)

            benchmark_command = (
                "python -c \"import json, pathlib; "
                "out = pathlib.Path(r'{output_dir}'); "
                "out.mkdir(parents=True, exist_ok=True); "
                "payload = {'summary': {'overall_passed': False}, 'eval_run': {'passed': 53, 'total': 54, "
                "'cases': [{'id': 1, 'prompt': 'a', 'passed': False, 'failures': ['regressed']}], "
                "'category_breakdown': [{'category': 'iteration', 'passed': 0, 'total': 1}]}}; "
                "(out / 'benchmark-results.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')\""
            )
            apply_command = (
                "python -c \"from pathlib import Path; "
                "Path('candidate.txt').write_text('base\\nchanged\\n', encoding='utf-8')\""
            )
            rollback_command = (
                "python -c \"from pathlib import Path; "
                "Path('candidate.txt').write_text('base\\n', encoding='utf-8')\""
            )

            result = iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="apply and rollback candidate workspace safely",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="change file and rollback on regression",
                candidate_repo=candidate_repo,
                benchmark_command=benchmark_command,
                apply_command=apply_command,
                rollback_command=rollback_command,
                auto_apply_rollback=True,
            )

            state = baseline_registry.load_json(workspace / "round-01" / "state.json")
            self.assertEqual("rollback", result["decision"])
            self.assertEqual("base\n", tracked_file.read_text(encoding="utf-8"))
            self.assertTrue(result["apply_result"]["passed"])
            self.assertTrue(result["rollback_result"]["passed"])
            self.assertIn("before-apply", result["workspace_snapshots"])
            self.assertIn("after-apply", result["workspace_snapshots"])
            self.assertIn("after-rollback", result["workspace_snapshots"])
            self.assertTrue(Path(result["workspace_snapshots"]["after-rollback"]["snapshot"]).exists())
            self.assertEqual(apply_command, state["apply_command"])
            self.assertEqual(rollback_command, state["rollback_command"])
            self.assertTrue(state["auto_apply_rollback"])

    def test_run_iteration_cycle_applies_patch_and_auto_reverse_rollback(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            candidate_repo = Path(tmp) / "candidate-repo"
            patch_path = workspace / "candidate.patch"
            baseline_report = workspace / "baseline.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)
            baseline_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }
            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(
                workspace=workspace,
                label="stable",
                report_path=baseline_report,
            )

            candidate_repo.mkdir(parents=True, exist_ok=True)
            git("init", cwd=candidate_repo)
            configure_repo(candidate_repo)
            tracked_file = candidate_repo / "candidate.txt"
            tracked_file.write_text("base\n", encoding="utf-8")
            git("add", "candidate.txt", cwd=candidate_repo)
            git("commit", "-m", "chore: init candidate", cwd=candidate_repo)

            tracked_file.write_text("base\npatched\n", encoding="utf-8")
            patch_text = git("diff", "--", "candidate.txt", cwd=candidate_repo).stdout
            patch_path.write_text(patch_text, encoding="utf-8")
            tracked_file.write_text("base\n", encoding="utf-8")

            benchmark_command = (
                "python -c \"import json, pathlib; "
                "out = pathlib.Path(r'{output_dir}'); "
                "out.mkdir(parents=True, exist_ok=True); "
                "payload = {'summary': {'overall_passed': False}, 'eval_run': {'passed': 53, 'total': 54, "
                "'cases': [{'id': 1, 'prompt': 'a', 'passed': False, 'failures': ['regressed']}], "
                "'category_breakdown': [{'category': 'iteration', 'passed': 0, 'total': 1}]}}; "
                "(out / 'benchmark-results.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')\""
            )

            result = iteration_cycle.run_cycle(
                workspace=workspace,
                round_id="round-01",
                objective="apply patch and auto reverse on rollback",
                baseline_label="stable",
                owner="Technical Trinity",
                candidate="apply patch artifact",
                candidate_repo=candidate_repo,
                candidate_patch=patch_path,
                benchmark_command=benchmark_command,
                auto_apply_rollback=True,
            )

            state = baseline_registry.load_json(workspace / "round-01" / "state.json")
            self.assertEqual("rollback", result["decision"])
            self.assertEqual("base\n", tracked_file.read_text(encoding="utf-8"))
            self.assertTrue(result["apply_result"]["passed"])
            self.assertTrue(result["rollback_result"]["passed"])
            self.assertEqual(str(patch_path.resolve()), result["candidate_patch"])
            self.assertEqual(str(patch_path.resolve()), state["candidate_patch"])
            self.assertIn("after-rollback", result["workspace_snapshots"])

    def test_promote_round_requires_keep_decision(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            round_dir = workspace / "round-01"
            round_dir.mkdir(parents=True, exist_ok=True)
            (round_dir / "state.json").write_text(
                json.dumps(
                    {
                        "round_id": "round-01",
                        "decision": "rollback",
                        "candidate_report": str(round_dir / "candidate.json"),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "not eligible for promotion"):
                baseline_promotion.promote_round(
                    workspace=workspace,
                    round_id="round-01",
                    label="accepted-round-01",
                )

    def test_sync_patterns_collects_only_kept_rounds(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            keep_dir = workspace / "round-01"
            rollback_dir = workspace / "round-02"
            keep_dir.mkdir(parents=True, exist_ok=True)
            rollback_dir.mkdir(parents=True, exist_ok=True)
            (keep_dir / "state.json").write_text(
                json.dumps(
                    {
                        "round_id": "round-01",
                        "decision": "keep",
                        "objective": "improve stability",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate": "accepted change",
                        "decision_reason": ["resolved failures without regressions"],
                        "comparison": {
                            "baseline": {
                                "overall_passed": False,
                                "evals_passed": 53,
                                "evals_total": 54,
                            },
                            "candidate": {
                                "overall_passed": True,
                                "evals_passed": 54,
                                "evals_total": 54,
                            },
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (rollback_dir / "state.json").write_text(
                json.dumps(
                    {
                        "round_id": "round-02",
                        "decision": "rollback",
                        "objective": "another attempt",
                        "candidate": "rejected change",
                        "decision_reason": ["introduced regression"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = pattern_sync.sync_patterns(workspace=workspace)
            content = Path(result["distilled_patterns"]).read_text(encoding="utf-8")
            self.assertEqual(1, result["kept_rounds"])
            self.assertIn("round-01", content)
            self.assertNotIn("round-02", content)
            self.assertIn("Owner: Technical Trinity", content)
            self.assertIn("Baseline label: stable", content)
            self.assertIn("Evidence snapshot", content)

    def test_run_iteration_loop_advances_baseline_after_keep(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            baseline_report = workspace / "baseline.json"
            candidate_a = workspace / "candidate-a.json"
            candidate_b = workspace / "candidate-b.json"
            plan_path = workspace / "iteration-plan.json"
            baseline_report.parent.mkdir(parents=True, exist_ok=True)

            baseline_payload = {
                "summary": {"overall_passed": False},
                "eval_run": {
                    "passed": 53,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": False, "failures": ["old failure"]}],
                    "category_breakdown": [{"category": "iteration", "passed": 0, "total": 1}],
                },
            }
            keep_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }
            stop_payload = {
                "summary": {"overall_passed": True},
                "eval_run": {
                    "passed": 54,
                    "total": 54,
                    "cases": [{"id": 1, "prompt": "a", "passed": True, "failures": []}],
                    "category_breakdown": [{"category": "iteration", "passed": 1, "total": 1}],
                },
            }

            baseline_report.write_text(json.dumps(baseline_payload, ensure_ascii=False), encoding="utf-8")
            candidate_a.write_text(json.dumps(keep_payload, ensure_ascii=False), encoding="utf-8")
            candidate_b.write_text(json.dumps(stop_payload, ensure_ascii=False), encoding="utf-8")
            baseline_registry.register_baseline(workspace=workspace, label="stable", report_path=baseline_report)

            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "stabilize benchmark quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 2,
                            "advance_baseline_on_keep": True,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": True,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "first candidate",
                                "candidate_report": str(candidate_a),
                                "promote_label": "accepted-round-01",
                            },
                            {
                                "round_id": "round-02",
                                "candidate": "second candidate",
                                "candidate_report": str(candidate_b),
                                "promote_label": "accepted-round-02",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)
            self.assertEqual(2, result["round_count"])
            self.assertEqual("accepted-round-01", result["final_baseline_label"])
            self.assertTrue(Path(result["summary"]).exists())
            self.assertEqual("World-Class Product Architect", result["owner"])
            first_state = baseline_registry.load_json(workspace / "round-01" / "state.json")
            self.assertEqual("World-Class Product Architect", first_state["owner"])

    def test_run_iteration_loop_stops_after_same_hypothesis_retry_budget(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "stabilize retry-heavy loop",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 4,
                            "max_same_hypothesis_retries": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "attempt 1", "hypothesis_key": "same-focus"},
                            {"round_id": "round-02", "candidate": "attempt 2", "hypothesis_key": "same-focus"},
                            {"round_id": "round-03", "candidate": "attempt 3", "hypothesis_key": "same-focus"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                round_dir = workspace / str(kwargs["round_id"])
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": kwargs["round_id"],
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "retry",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "retry", "decision_reason": ["still inconclusive"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(2, result["round_count"])
            self.assertEqual("same hypothesis retry budget exhausted: same-focus", result["halt_reason"])
            self.assertEqual({"same-focus": 2}, result["hypothesis_attempts"])
            self.assertEqual(2, len(calls))

    def test_run_iteration_loop_stops_after_consecutive_non_keep_budget(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "stop deep loops after repeated non-progress",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 4,
                            "max_consecutive_non_keep_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "attempt 1", "hypothesis_key": "focus-1"},
                            {"round_id": "round-02", "candidate": "attempt 2", "hypothesis_key": "focus-2"},
                            {"round_id": "round-03", "candidate": "attempt 3", "hypothesis_key": "focus-3"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []
            decisions = {
                "round-01": ("retry", ["needs stronger evidence"]),
                "round-02": ("rollback", ["regressed the benchmark"]),
                "round-03": ("stop", ["should not execute"]),
            }

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                decision, reasons = decisions[str(kwargs["round_id"])]
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(2, result["round_count"])
            self.assertEqual("consecutive non-keep budget exhausted: 2", result["halt_reason"])
            self.assertEqual(2, result["consecutive_non_keep_rounds"])
            self.assertEqual(
                {"keep": 0, "retry": 1, "rollback": 1, "stop": 0},
                result["decision_counts"],
            )
            self.assertEqual(2, len(calls))

    def test_run_iteration_loop_resets_non_keep_streak_after_keep(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "reset stagnation tracking after a keep",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 4,
                            "max_consecutive_non_keep_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "attempt 1", "hypothesis_key": "focus-1"},
                            {"round_id": "round-02", "candidate": "attempt 2", "hypothesis_key": "focus-2"},
                            {"round_id": "round-03", "candidate": "attempt 3", "hypothesis_key": "focus-3"},
                            {"round_id": "round-04", "candidate": "attempt 4", "hypothesis_key": "focus-4"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[str] = []
            decisions = {
                "round-01": ("retry", ["needs stronger evidence"]),
                "round-02": ("keep", ["improved without regressions"]),
                "round-03": ("retry", ["next bottleneck needs another pass"]),
                "round-04": ("stop", ["loop reached a stable stopping point"]),
            }

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                calls.append(round_id)
                decision, reasons = decisions[round_id]
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(4, result["round_count"])
            self.assertEqual("halted on decision: stop", result["halt_reason"])
            self.assertEqual(0, result["consecutive_non_keep_rounds"])
            self.assertEqual(
                {"keep": 1, "retry": 2, "rollback": 0, "stop": 1},
                result["decision_counts"],
            )
            self.assertEqual(["round-01", "round-02", "round-03", "round-04"], calls)

    def test_run_iteration_loop_renders_workspace_command_templates(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "drive repo mutation commands from the plan",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate_worktree_template": "../wt-{round_id}",
                        "benchmark_command_template": "python scripts/bench.py --round {round_id} --output-dir {output_dir}",
                        "apply_command_template": "python scripts/apply_change.py --round {round_id}",
                        "rollback_command_template": "python scripts/rollback_change.py --round {round_id}",
                        "auto_apply_rollback": True,
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "candidate with workspace commands",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(1, result["round_count"])
            self.assertEqual(1, len(calls))
            self.assertEqual(
                "python scripts/apply_change.py --round round-01",
                calls[0]["apply_command"],
            )
            self.assertEqual(
                "python scripts/rollback_change.py --round round-01",
                calls[0]["rollback_command"],
            )
            self.assertEqual(
                "python scripts/bench.py --round round-01 --output-dir {output_dir}",
                calls[0]["benchmark_command"],
            )
            self.assertTrue(calls[0]["auto_apply_rollback"])

    def test_run_iteration_loop_renders_candidate_patch_templates(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "drive patch artifacts from the plan",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate_worktree_template": "../wt-{round_id}",
                        "candidate_patch_template": "./patches/{round_id}.patch",
                        "patch_strip": 1,
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "candidate with patch artifact",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(1, result["round_count"])
            self.assertEqual(1, len(calls))
            self.assertEqual(
                str((workspace / "patches" / "round-01.patch").resolve()),
                str(calls[0]["candidate_patch"]),
            )
            self.assertEqual(1, calls[0]["patch_strip"])

    def test_run_iteration_loop_writes_candidate_brief_and_runs_materializer(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            materialize_command = (
                "python -c \"import json; from pathlib import Path; "
                "brief = json.loads(Path(r'{candidate_brief}').read_text(encoding='utf-8')); "
                "patch_path = Path(r'{candidate_patch}'); "
                "patch_path.parent.mkdir(parents=True, exist_ok=True); "
                "patch_path.write_text('PATCH:' + brief['candidate'], encoding='utf-8')\""
            )
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "materialize the candidate into a patch artifact",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate_worktree_template": "../wt-{round_id}",
                        "candidate_patch_template": "./patches/{round_id}.patch",
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "materialize_command_template": materialize_command,
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "candidate materialized through brief",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(1, result["round_count"])
            self.assertEqual(1, len(calls))
            brief_path = workspace / "briefs" / "round-01.json"
            patch_path = workspace / "patches" / "round-01.patch"
            self.assertTrue(brief_path.exists())
            self.assertTrue(patch_path.exists())
            brief = baseline_registry.load_json(brief_path)
            self.assertEqual("candidate materialized through brief", brief["candidate"])
            self.assertEqual("plan", brief["candidate_source"])
            self.assertEqual(str(patch_path.resolve()), str(calls[0]["candidate_patch"]))
            self.assertEqual(str(brief_path.resolve()), result["rounds_run"][0]["candidate_brief"])
            self.assertTrue(result["rounds_run"][0]["materialize_result"]["passed"])
            self.assertEqual(
                "PATCH:candidate materialized through brief",
                patch_path.read_text(encoding="utf-8"),
            )

    def test_run_iteration_loop_builtin_materializer_creates_patch_from_mutation_plan(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            candidate_repo = Path(tmp) / "candidate-repo"
            candidate_repo.mkdir(parents=True, exist_ok=True)
            target_file = candidate_repo / "settings.py"
            target_file.write_text("FEATURE_FLAG = False\n", encoding="utf-8")
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "turn a mutation plan into a patch without an external materializer",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "candidate_patch_template": "./patches/{round_id}.patch",
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "enable the feature flag",
                                "candidate_repo": str(candidate_repo),
                                "mutation_plan": {
                                    "mode": "patch",
                                    "operations": [
                                        {
                                            "op": "replace_text",
                                            "path": "settings.py",
                                            "old": "FEATURE_FLAG = False\n",
                                            "new": "FEATURE_FLAG = True\n",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(1, result["round_count"])
            self.assertEqual(1, len(calls))
            brief_path = workspace / "briefs" / "round-01.json"
            patch_path = workspace / "patches" / "round-01.patch"
            self.assertTrue(brief_path.exists())
            self.assertTrue(patch_path.exists())
            brief = baseline_registry.load_json(brief_path)
            self.assertEqual("patch", brief["mutation_plan"]["mode"])
            self.assertEqual(
                "replace_text",
                brief["mutation_plan"]["operations"][0]["op"],
            )
            self.assertEqual(str(patch_path.resolve()), str(calls[0]["candidate_patch"]))
            self.assertEqual(
                "builtin-materialize-candidate-patch",
                result["rounds_run"][0]["materialize_result"]["engine"],
            )
            patch_text = patch_path.read_text(encoding="utf-8")
            self.assertIn("diff --git a/settings.py b/settings.py", patch_text)
            self.assertIn("+FEATURE_FLAG = True", patch_text)

    def test_builtin_materializer_supports_json_operations_for_skill_self_optimization(self) -> None:
        with make_tempdir() as tmp:
            candidate_repo = Path(tmp) / "candidate-repo"
            references_dir = candidate_repo / "references"
            evals_dir = candidate_repo / "evals"
            references_dir.mkdir(parents=True, exist_ok=True)
            evals_dir.mkdir(parents=True, exist_ok=True)
            (references_dir / "routing-rules.json").write_text(
                json.dumps(
                    {
                        "weights": {
                            "git_workflow": 2,
                            "frontend": 5,
                        },
                        "negative_keywords": {
                            "git": ["checkout"],
                        },
                        "obsolete_rule": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (evals_dir / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "virtual-intelligent-dev-team",
                        "evals": [
                            {
                                "id": 1,
                                "prompt": "existing case",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            patch_path = Path(tmp) / "candidate.patch"

            result = iteration_loop.candidate_materializer.materialize_payload(
                payload={
                    "mutation_plan": {
                        "mode": "patch",
                        "operations": [
                            {
                                "op": "json_set",
                                "path": "references/routing-rules.json",
                                "pointer": "/weights/git_workflow",
                                "value": 4,
                            },
                            {
                                "op": "json_merge",
                                "path": "references/routing-rules.json",
                                "pointer": "/negative_keywords",
                                "value": {
                                    "product": ["checkout"],
                                },
                            },
                            {
                                "op": "json_delete",
                                "path": "references/routing-rules.json",
                                "pointer": "/obsolete_rule",
                            },
                            {
                                "op": "json_append_unique",
                                "path": "evals/evals.json",
                                "pointer": "/evals",
                                "match_keys": ["id"],
                                "value": {
                                    "id": 99,
                                    "prompt": "new regression coverage",
                                },
                            },
                            {
                                "op": "json_append_unique",
                                "path": "evals/evals.json",
                                "pointer": "/evals",
                                "match_keys": ["id"],
                                "value": {
                                    "id": 99,
                                    "prompt": "new regression coverage",
                                },
                            },
                        ],
                    }
                },
                candidate_root=candidate_repo,
                patch_output=patch_path,
            )

            self.assertTrue(result["passed"])
            self.assertEqual(
                sorted(["evals/evals.json", "references/routing-rules.json"]),
                result["changed_files"],
            )
            patch_text = patch_path.read_text(encoding="utf-8")
            self.assertIn("diff --git a/references/routing-rules.json b/references/routing-rules.json", patch_text)
            self.assertIn("diff --git a/evals/evals.json b/evals/evals.json", patch_text)
            self.assertIn('"git_workflow": 4', patch_text)
            self.assertIn('"product": [', patch_text)
            self.assertIn('-  "obsolete_rule": true', patch_text)
            self.assertEqual(1, patch_text.count('"id": 99'))

    def test_run_iteration_loop_renders_explicit_mutation_plan_templates(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            candidate_repo = Path(tmp) / "candidate-repo"
            candidate_repo.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "render explicit mutation plan placeholders safely",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "candidate_patch_template": "./patches/{round_id}.patch",
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "seed explicit templated remediation",
                                "candidate_repo": str(candidate_repo),
                                "mutation_focus": "unit-test bootstrap",
                                "mutation_plan": {
                                    "mode": "patch",
                                    "operations": [
                                        {
                                            "op": "write_file",
                                            "path": "artifacts/{round_id}-note.md",
                                            "content": "Focus={focus}; round={round_id}; hypothesis={hypothesis_key}",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                iteration_loop.iteration_cycle,
                "run_cycle",
                return_value={"decision": "stop", "decision_reason": ["done"]},
            ):
                iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            brief = baseline_registry.load_json(workspace / "briefs" / "round-01.json")
            operation = brief["mutation_plan"]["operations"][0]
            self.assertEqual("artifacts/round-01-note.md", operation["path"])
            self.assertIn("Focus=unit-test bootstrap", operation["content"])
            self.assertIn("round=round-01", operation["content"])
            self.assertIn("hypothesis=seed-explicit-templated-remediation", operation["content"])
            self.assertEqual("explicit", brief["mutation_plan_source"])

    def test_builtin_materializer_patch_applies_to_git_repo_without_final_newline(self) -> None:
        with make_tempdir() as tmp:
            candidate_repo = Path(tmp) / "candidate-repo"
            candidate_repo.mkdir(parents=True, exist_ok=True)
            git("init", cwd=candidate_repo)
            configure_repo(candidate_repo)
            target_file = candidate_repo / "signals.json"
            target_file.write_text('{"mode":"baseline"}', encoding="utf-8")
            git("add", "signals.json", cwd=candidate_repo)
            git("commit", "-m", "chore: init signals", cwd=candidate_repo)

            patch_path = Path(tmp) / "candidate.patch"
            result = iteration_loop.candidate_materializer.materialize_payload(
                payload={
                    "mutation_plan": {
                        "mode": "patch",
                        "operations": [
                            {
                                "op": "json_set",
                                "path": "signals.json",
                                "pointer": "/mode",
                                "value": "improve",
                            }
                        ],
                    }
                },
                candidate_root=candidate_repo,
                patch_output=patch_path,
            )

            self.assertTrue(result["passed"])
            apply_result = iteration_cycle.apply_patch_file(
                candidate_root=candidate_repo,
                patch_path=patch_path,
                patch_strip=1,
            )
            self.assertTrue(apply_result["passed"])
            self.assertIn('"mode": "improve"', target_file.read_text(encoding="utf-8"))
            rollback_result = iteration_cycle.apply_patch_file(
                candidate_root=candidate_repo,
                patch_path=patch_path,
                patch_strip=1,
                reverse=True,
            )
            self.assertTrue(rollback_result["passed"])
            self.assertEqual('{"mode":"baseline"}', target_file.read_text(encoding="utf-8"))

    def test_is_git_repo_rejects_nested_copy_without_own_git_metadata(self) -> None:
        with make_tempdir() as tmp:
            outer_repo = Path(tmp) / "outer-repo"
            nested_copy = outer_repo / "nested-copy"
            outer_repo.mkdir(parents=True, exist_ok=True)
            nested_copy.mkdir(parents=True, exist_ok=True)
            git("init", cwd=outer_repo)
            configure_repo(outer_repo)
            (outer_repo / "README.md").write_text("demo\n", encoding="utf-8")
            git("add", "README.md", cwd=outer_repo)
            git("commit", "-m", "chore: init outer repo", cwd=outer_repo)

            self.assertTrue(iteration_cycle.is_git_repo(outer_repo))
            self.assertFalse((nested_copy / ".git").exists())
            self.assertFalse(iteration_cycle.is_git_repo(nested_copy))

    def test_run_iteration_loop_plan_candidate_can_synthesize_mutation_plan_from_catalog(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            candidate_repo = Path(tmp) / "candidate-repo"
            candidate_repo.mkdir(parents=True, exist_ok=True)
            (candidate_repo / "layout.css").write_text("gap: 8px;\n", encoding="utf-8")
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "improve frontend spacing quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "mutation_catalog": [
                            {
                                "id": "mobile-spacing-fix",
                                "priority": 10,
                                "when_any_keywords": ["mobile spacing", "mobile", "spacing"],
                                "mutation_plan": {
                                    "mode": "patch",
                                    "operations": [
                                        {
                                            "op": "replace_text",
                                            "path": "layout.css",
                                            "old": "gap: 8px;\n",
                                            "new": "gap: 12px;\n",
                                        }
                                    ],
                                },
                            }
                        ],
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "tighten mobile spacing on small screens",
                                "candidate_repo": str(candidate_repo),
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(1, result["round_count"])
            self.assertEqual(1, len(calls))
            brief_path = workspace / "briefs" / "round-01.json"
            patch_path = workspace / "patches" / "round-01.patch"
            self.assertTrue(brief_path.exists())
            self.assertTrue(patch_path.exists())
            brief = baseline_registry.load_json(brief_path)
            self.assertEqual("catalog:mobile-spacing-fix", brief["mutation_plan_source"])
            self.assertEqual(str(patch_path.resolve()), str(calls[0]["candidate_patch"]))
            self.assertEqual(
                "builtin-materialize-candidate-patch",
                result["rounds_run"][0]["materialize_result"]["engine"],
            )
            self.assertEqual("catalog:mobile-spacing-fix", result["rounds_run"][0]["mutation_plan_source"])

    def test_run_iteration_loop_can_synthesize_json_mutation_plan_for_skill_self_optimization(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            candidate_repo = Path(tmp) / "candidate-repo"
            (candidate_repo / "references").mkdir(parents=True, exist_ok=True)
            (candidate_repo / "evals").mkdir(parents=True, exist_ok=True)
            (candidate_repo / "references" / "routing-rules.json").write_text(
                json.dumps(
                    {
                        "weights": {
                            "git_workflow": 2,
                            "frontend": 5,
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (candidate_repo / "evals" / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "virtual-intelligent-dev-team",
                        "evals": [],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "self-optimize routing guardrails without manual patch writing",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "mutation_catalog": [
                            {
                                "id": "checkout-false-positive-self-fix",
                                "priority": 10,
                                "when_any_keywords": ["checkout false positive", "eval coverage", "routing regression"],
                                "mutation_plan": {
                                    "mode": "patch",
                                    "operations": [
                                        {
                                            "op": "json_set",
                                            "path": "references/routing-rules.json",
                                            "pointer": "/weights/git_workflow",
                                            "value": 1,
                                        },
                                        {
                                            "op": "json_append_unique",
                                            "path": "evals/evals.json",
                                            "pointer": "/evals",
                                            "match_keys": ["id"],
                                            "value": {
                                                "id": 101,
                                                "prompt": "Audit this checkout UX for accessibility and mobile responsiveness.",
                                                "expected_output": "Checkout UX should stay with World-Class Product Architect instead of Git workflow routing.",
                                            },
                                        },
                                    ],
                                },
                            }
                        ],
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "fix checkout false positive routing regression and add eval coverage",
                                "candidate_repo": str(candidate_repo),
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                calls.append(dict(kwargs))
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(1, result["round_count"])
            self.assertEqual(1, len(calls))
            brief_path = workspace / "briefs" / "round-01.json"
            patch_path = workspace / "patches" / "round-01.patch"
            self.assertTrue(brief_path.exists())
            self.assertTrue(patch_path.exists())
            brief = baseline_registry.load_json(brief_path)
            self.assertEqual("catalog:checkout-false-positive-self-fix", brief["mutation_plan_source"])
            self.assertEqual(str(patch_path.resolve()), str(calls[0]["candidate_patch"]))
            self.assertEqual(
                "builtin-materialize-candidate-patch",
                result["rounds_run"][0]["materialize_result"]["engine"],
            )
            patch_text = patch_path.read_text(encoding="utf-8")
            self.assertIn("diff --git a/references/routing-rules.json b/references/routing-rules.json", patch_text)
            self.assertIn("diff --git a/evals/evals.json b/evals/evals.json", patch_text)
            self.assertIn('"git_workflow": 1', patch_text)
            self.assertIn('"id": 101', patch_text)

    def test_run_iteration_loop_auto_generates_candidate_from_feedback_chain(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "improve frontend iteration quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "autonomous_candidate_generation": True,
                        "candidate_worktree_template": "../wt-{round_id}",
                        "candidate_output_dir_template": "./runs/{round_id}",
                        "loop_policy": {
                            "max_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "initial frontend hypothesis",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                candidate = str(kwargs["candidate"])
                calls.append(dict(kwargs))
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                decision = "retry" if round_id == "round-01" else "stop"
                reasons = ["missing mobile evidence"] if decision == "retry" else ["candidate is materially unchanged from baseline"]
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "decision": decision,
                            "candidate": candidate,
                            "decision_reason": reasons,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                (round_dir / "round-memory.md").write_text(
                    "# Round Memory\n\n- Open loops: missing mobile evidence\n- Suggested next move: tighten mobile layout evidence\n",
                    encoding="utf-8",
                )
                (round_dir / "self-feedback.md").write_text(
                    "# Self Feedback\n\n- Signals that regressed or blocked progress: missing mobile evidence\n- One variable to change next: mobile spacing\n",
                    encoding="utf-8",
                )
                (workspace / "open-loops.md").write_text(
                    "# Open Loops\n\n- [round-01] missing mobile evidence\n",
                    encoding="utf-8",
                )
                (workspace / "distilled-patterns.md").write_text(
                    "# Distilled Patterns\n\n- Keep the semantic owner stable.\n",
                    encoding="utf-8",
                )
                (workspace / "iteration-context-chain.md").write_text(
                    "# Iteration Context Chain\n\n- missing mobile evidence\n",
                    encoding="utf-8",
                )
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(2, result["round_count"])
            self.assertEqual(1, result["auto_generated_rounds"])
            self.assertEqual("auto-generated", result["rounds_run"][1]["candidate_source"])
            self.assertIn("missing mobile evidence", str(calls[1]["candidate"]))
            self.assertEqual("World-Class Product Architect", calls[1]["owner"])
            self.assertEqual(str((workspace.parent / "wt-round-02").resolve()), str(calls[1]["candidate_repo"]))
            self.assertEqual(str((workspace / "runs" / "round-02").resolve()), str(calls[1]["candidate_output_dir"]))

    def test_run_iteration_loop_auto_pivots_after_same_hypothesis_budget(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            mobile_focus = "mobile spacing still needs stronger evidence"
            latency_focus = "form latency still blocks checkout submit"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "improve frontend iteration quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "autonomous_candidate_generation": True,
                        "loop_policy": {
                            "max_rounds": 3,
                            "max_same_hypothesis_retries": 1,
                            "auto_pivot_on_stagnation": True,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "initial frontend hypothesis",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                candidate = str(kwargs["candidate"])
                calls.append(dict(kwargs))
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                decision = {"round-01": "retry", "round-02": "retry"}.get(round_id, "stop")
                reasons = (
                    [mobile_focus]
                    if decision != "stop"
                    else ["loop reached a stable stopping point"]
                )
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "decision": decision,
                            "candidate": candidate,
                            "decision_reason": reasons,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                if round_id in {"round-01", "round-02"}:
                    (round_dir / "round-memory.md").write_text(
                        f"# Round Memory\n\n- Open loops: {mobile_focus}\n- Suggested next move: {latency_focus}\n",
                        encoding="utf-8",
                    )
                    (round_dir / "self-feedback.md").write_text(
                        f"# Self Feedback\n\n- Signals that regressed or blocked progress: {mobile_focus}\n- One variable to change next: mobile spacing\n",
                        encoding="utf-8",
                    )
                    (workspace / "open-loops.md").write_text(
                        f"# Open Loops\n\n- [round-02] {mobile_focus}\n- [round-02] {latency_focus}\n",
                        encoding="utf-8",
                    )
                    (workspace / "distilled-patterns.md").write_text(
                        "# Distilled Patterns\n\n- Preserve semantic ownership.\n",
                        encoding="utf-8",
                    )
                    (workspace / "iteration-context-chain.md").write_text(
                        f"# Iteration Context Chain\n\n- {mobile_focus}\n- {latency_focus}\n",
                        encoding="utf-8",
                    )
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(3, result["round_count"])
            self.assertEqual(2, result["auto_generated_rounds"])
            self.assertEqual(1, result["pivot_count"])
            self.assertIn(iteration_loop.hypothesis_key_from_text(mobile_focus), result["blocked_hypothesis_keys"])
            self.assertEqual("auto-generated", result["rounds_run"][2]["candidate_source"])
            self.assertIn(latency_focus, str(calls[2]["candidate"]))
            self.assertIn("same hypothesis retry budget exhausted", str(result["rounds_run"][2]["generation_reason"]))

    def test_run_iteration_loop_auto_pivots_after_consecutive_non_keep_budget(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            mobile_focus = "mobile spacing still needs stronger evidence"
            latency_focus = "form latency still blocks checkout submit"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "improve frontend iteration quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "autonomous_candidate_generation": True,
                        "loop_policy": {
                            "max_rounds": 3,
                            "max_same_hypothesis_retries": 3,
                            "max_consecutive_non_keep_rounds": 2,
                            "auto_pivot_on_stagnation": True,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "initial frontend hypothesis",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                candidate = str(kwargs["candidate"])
                calls.append(dict(kwargs))
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                decision = {"round-01": "retry", "round-02": "rollback"}.get(round_id, "stop")
                reasons = (
                    [mobile_focus]
                    if decision != "stop"
                    else ["loop reached a stable stopping point"]
                )
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "decision": decision,
                            "candidate": candidate,
                            "decision_reason": reasons,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                if round_id in {"round-01", "round-02"}:
                    (round_dir / "round-memory.md").write_text(
                        f"# Round Memory\n\n- Open loops: {mobile_focus}\n- Suggested next move: {latency_focus}\n",
                        encoding="utf-8",
                    )
                    (round_dir / "self-feedback.md").write_text(
                        f"# Self Feedback\n\n- Signals that regressed or blocked progress: {mobile_focus}\n- One variable to change next: mobile spacing\n",
                        encoding="utf-8",
                    )
                    (workspace / "open-loops.md").write_text(
                        f"# Open Loops\n\n- [round-02] {mobile_focus}\n- [round-02] {latency_focus}\n",
                        encoding="utf-8",
                    )
                    (workspace / "distilled-patterns.md").write_text(
                        "# Distilled Patterns\n\n- Preserve semantic ownership.\n",
                        encoding="utf-8",
                    )
                    (workspace / "iteration-context-chain.md").write_text(
                        f"# Iteration Context Chain\n\n- {mobile_focus}\n- {latency_focus}\n",
                        encoding="utf-8",
                    )
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(3, result["round_count"])
            self.assertEqual(2, result["auto_generated_rounds"])
            self.assertEqual(1, result["pivot_count"])
            self.assertEqual("halted on decision: stop", result["halt_reason"])
            self.assertEqual(0, result["consecutive_non_keep_rounds"])
            self.assertIn(iteration_loop.hypothesis_key_from_text(mobile_focus), result["blocked_hypothesis_keys"])
            self.assertEqual("auto-generated", result["rounds_run"][2]["candidate_source"])
            self.assertIn(latency_focus, str(calls[2]["candidate"]))
            self.assertIn("consecutive non-keep budget exhausted", str(result["rounds_run"][2]["generation_reason"]))

    def test_run_iteration_loop_auto_synthesizes_mutation_plan_from_catalog(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            candidate_repo = Path(tmp) / "wt-round-02"
            candidate_repo.mkdir(parents=True, exist_ok=True)
            (candidate_repo / "layout.css").write_text("gap: 8px;\n", encoding="utf-8")
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "improve frontend iteration quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "autonomous_candidate_generation": True,
                        "candidate_worktree_template": "../wt-{round_id}",
                        "candidate_patch_template": "./patches/{round_id}.patch",
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "mutation_catalog": [
                            {
                                "id": "mobile-spacing-fix",
                                "priority": 10,
                                "when_any_keywords": ["mobile spacing", "mobile", "spacing"],
                                "mutation_plan": {
                                    "mode": "patch",
                                    "operations": [
                                        {
                                            "op": "replace_text",
                                            "path": "layout.css",
                                            "old": "gap: 8px;\n",
                                            "new": "gap: 12px;\n",
                                        }
                                    ],
                                },
                            }
                        ],
                        "loop_policy": {
                            "max_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "initial frontend hypothesis",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            calls: list[dict[str, object]] = []

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                candidate = str(kwargs["candidate"])
                calls.append(dict(kwargs))
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                decision = "retry" if round_id == "round-01" else "stop"
                reasons = (
                    ["mobile spacing still feels cramped on small screens"]
                    if decision == "retry"
                    else ["done"]
                )
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "decision": decision,
                            "candidate": candidate,
                            "decision_reason": reasons,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                if round_id == "round-01":
                    (round_dir / "round-memory.md").write_text(
                        "# Round Memory\n\n- Open loops: mobile spacing still feels cramped on small screens\n- Suggested next move: increase mobile spacing\n",
                        encoding="utf-8",
                    )
                    (round_dir / "self-feedback.md").write_text(
                        "# Self Feedback\n\n- Signals that regressed or blocked progress: mobile spacing still feels cramped on small screens\n- One variable to change next: mobile spacing\n",
                        encoding="utf-8",
                    )
                    (workspace / "open-loops.md").write_text(
                        "# Open Loops\n\n- [round-01] mobile spacing still feels cramped on small screens\n",
                        encoding="utf-8",
                    )
                    (workspace / "distilled-patterns.md").write_text(
                        "# Distilled Patterns\n\n- Preserve the semantic owner and optimize mobile spacing next.\n",
                        encoding="utf-8",
                    )
                    (workspace / "iteration-context-chain.md").write_text(
                        "# Iteration Context Chain\n\n- mobile spacing still feels cramped on small screens\n",
                        encoding="utf-8",
                    )
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(2, result["round_count"])
            self.assertEqual(2, len(calls))
            brief_path = workspace / "briefs" / "round-02.json"
            patch_path = workspace / "patches" / "round-02.patch"
            self.assertTrue(brief_path.exists())
            self.assertTrue(patch_path.exists())
            brief = baseline_registry.load_json(brief_path)
            self.assertEqual("catalog:mobile-spacing-fix", brief["mutation_plan_source"])
            self.assertIsNotNone(brief["mutation_focus"])
            self.assertEqual("patch", brief["mutation_plan"]["mode"])
            self.assertEqual(
                "replace_text",
                brief["mutation_plan"]["operations"][0]["op"],
            )
            self.assertEqual(str(patch_path.resolve()), str(calls[1]["candidate_patch"]))
            self.assertEqual(
                "builtin-materialize-candidate-patch",
                result["rounds_run"][1]["materialize_result"]["engine"],
            )
            self.assertEqual("catalog:mobile-spacing-fix", result["rounds_run"][1]["mutation_plan_source"])
            patch_text = patch_path.read_text(encoding="utf-8")
            self.assertIn("diff --git a/layout.css b/layout.css", patch_text)
            self.assertIn("+gap: 12px;", patch_text)

    def test_run_iteration_loop_auto_generated_brief_contains_generation_metadata(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "improve frontend iteration quality",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "autonomous_candidate_generation": True,
                        "candidate_brief_template": "./briefs/{round_id}.json",
                        "loop_policy": {
                            "max_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {
                                "round_id": "round-01",
                                "candidate": "initial frontend hypothesis",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                decision = "retry" if round_id == "round-01" else "stop"
                reasons = ["missing mobile evidence"] if decision == "retry" else ["done"]
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "decision": decision,
                            "candidate": kwargs["candidate"],
                            "decision_reason": reasons,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                (round_dir / "round-memory.md").write_text(
                    "# Round Memory\n\n- Open loops: missing mobile evidence\n- Suggested next move: tighten mobile layout evidence\n",
                    encoding="utf-8",
                )
                (round_dir / "self-feedback.md").write_text(
                    "# Self Feedback\n\n- Signals that regressed or blocked progress: missing mobile evidence\n- One variable to change next: mobile spacing\n",
                    encoding="utf-8",
                )
                (workspace / "open-loops.md").write_text(
                    "# Open Loops\n\n- [round-01] missing mobile evidence\n",
                    encoding="utf-8",
                )
                (workspace / "distilled-patterns.md").write_text(
                    "# Distilled Patterns\n\n- Keep the semantic owner stable.\n",
                    encoding="utf-8",
                )
                (workspace / "iteration-context-chain.md").write_text(
                    "# Iteration Context Chain\n\n- missing mobile evidence\n",
                    encoding="utf-8",
                )
                return {"decision": decision, "decision_reason": reasons}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            self.assertEqual(2, result["round_count"])
            brief_path = workspace / "briefs" / "round-02.json"
            self.assertTrue(brief_path.exists())
            brief = baseline_registry.load_json(brief_path)
            self.assertEqual("auto-generated", brief["candidate_source"])
            self.assertEqual("retry", brief["generation_reason"])
            self.assertTrue(any("open-loops.md" in item for item in brief["generated_from"]))
            self.assertEqual("World-Class Product Architect", brief["owner"])

    def test_run_iteration_loop_resume_continues_from_persisted_state(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "resume a deep offline loop after interruption",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 3,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "first attempt"},
                            {"round_id": "round-02", "candidate": "second attempt"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def interrupted_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                if round_id == "round-02":
                    raise RuntimeError("simulated interruption")
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "retry",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "retry", "decision_reason": ["need one more round"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=interrupted_run_cycle):
                with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                    iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            loop_state = baseline_registry.load_json(workspace / "loops" / "iteration-plan-state.json")
            self.assertEqual("running", loop_state["status"])
            self.assertEqual(1, loop_state["round_count"])
            self.assertEqual(2, loop_state["next_round_number"])
            self.assertEqual("round-01", loop_state["last_round_id"])

            resume_calls: list[str] = []

            def resumed_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                resume_calls.append(round_id)
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "stop",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "stop", "decision_reason": ["loop reached a stable stopping point"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=resumed_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path, resume=True)

            self.assertEqual("completed", result["status"])
            self.assertTrue(result["resume_requested"])
            self.assertTrue(result["resumed_from_existing"])
            self.assertEqual(2, result["round_count"])
            self.assertEqual(["round-02"], resume_calls)
            self.assertEqual("round-02", result["last_round_id"])
            self.assertTrue(Path(result["summary"]).exists())

    def test_run_iteration_loop_resume_preserves_non_keep_streak_budget(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "resume stagnation tracking safely",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 3,
                            "max_consecutive_non_keep_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "first attempt"},
                            {"round_id": "round-02", "candidate": "second attempt"},
                            {"round_id": "round-03", "candidate": "third attempt"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def interrupted_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                if round_id == "round-02":
                    raise RuntimeError("simulated interruption")
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "retry",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "retry", "decision_reason": ["need another round"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=interrupted_run_cycle):
                with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                    iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            resume_calls: list[str] = []

            def resumed_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                resume_calls.append(round_id)
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "retry",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "retry", "decision_reason": ["still inconclusive"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=resumed_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path, resume=True)

            self.assertEqual("completed", result["status"])
            self.assertTrue(result["resume_requested"])
            self.assertTrue(result["resumed_from_existing"])
            self.assertEqual(2, result["round_count"])
            self.assertEqual(["round-02"], resume_calls)
            self.assertEqual("consecutive non-keep budget exhausted: 2", result["halt_reason"])
            self.assertEqual(2, result["consecutive_non_keep_rounds"])
            self.assertEqual({"keep": 0, "retry": 2, "rollback": 0, "stop": 0}, result["decision_counts"])

    def test_run_iteration_loop_resume_preserves_pending_pivot_generation_reason(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            mobile_focus = "mobile spacing still needs stronger evidence"
            latency_focus = "form latency still blocks checkout submit"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "resume pivot intent safely",
                        "owner": "World-Class Product Architect",
                        "baseline_label": "stable",
                        "autonomous_candidate_generation": True,
                        "loop_policy": {
                            "max_rounds": 3,
                            "max_same_hypothesis_retries": 3,
                            "max_consecutive_non_keep_rounds": 2,
                            "auto_pivot_on_stagnation": True,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "initial frontend hypothesis"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                candidate = str(kwargs["candidate"])
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                decision = {"round-01": "retry", "round-02": "rollback"}.get(round_id, "stop")
                reasons = [mobile_focus] if decision != "stop" else ["loop reached a stable stopping point"]
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "decision": decision,
                            "candidate": candidate,
                            "decision_reason": reasons,
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                if round_id in {"round-01", "round-02"}:
                    (round_dir / "round-memory.md").write_text(
                        f"# Round Memory\n\n- Open loops: {mobile_focus}\n- Suggested next move: {latency_focus}\n",
                        encoding="utf-8",
                    )
                    (round_dir / "self-feedback.md").write_text(
                        f"# Self Feedback\n\n- Signals that regressed or blocked progress: {mobile_focus}\n- One variable to change next: mobile spacing\n",
                        encoding="utf-8",
                    )
                    (workspace / "open-loops.md").write_text(
                        f"# Open Loops\n\n- [round-02] {mobile_focus}\n- [round-02] {latency_focus}\n",
                        encoding="utf-8",
                    )
                    (workspace / "distilled-patterns.md").write_text(
                        "# Distilled Patterns\n\n- Preserve semantic ownership.\n",
                        encoding="utf-8",
                    )
                    (workspace / "iteration-context-chain.md").write_text(
                        f"# Iteration Context Chain\n\n- {mobile_focus}\n- {latency_focus}\n",
                        encoding="utf-8",
                    )
                return {"decision": decision, "decision_reason": reasons}

            original_synthesize_candidate = iteration_loop.synthesize_candidate
            interrupted = {"raised": False}

            def interrupted_synthesize_candidate(*args, **kwargs):
                if kwargs.get("pivot_reason") is not None and not interrupted["raised"]:
                    interrupted["raised"] = True
                    raise RuntimeError("simulated pivot synthesis interruption")
                return original_synthesize_candidate(*args, **kwargs)

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                with mock.patch.object(
                    iteration_loop,
                    "synthesize_candidate",
                    side_effect=interrupted_synthesize_candidate,
                ):
                    with self.assertRaisesRegex(RuntimeError, "simulated pivot synthesis interruption"):
                        iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            loop_state = baseline_registry.load_json(workspace / "loops" / "iteration-plan-state.json")
            self.assertIn(
                "consecutive non-keep budget exhausted",
                str(loop_state["pending_generation_reason"]),
            )
            self.assertIn(
                iteration_loop.hypothesis_key_from_text(mobile_focus),
                loop_state["blocked_hypothesis_keys"],
            )

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path, resume=True)

            self.assertTrue(result["resume_requested"])
            self.assertTrue(result["resumed_from_existing"])
            self.assertEqual(3, result["round_count"])
            self.assertIsNone(result["pending_generation_reason"])
            self.assertIn(latency_focus, str(result["rounds_run"][2]["candidate"]))
            self.assertIn("consecutive non-keep budget exhausted", str(result["rounds_run"][2]["generation_reason"]))

    def test_run_iteration_loop_resume_returns_completed_summary_without_rerun(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "avoid rerunning a completed loop",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 1,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "single attempt"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def fake_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "stop",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "stop", "decision_reason": ["done"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=fake_run_cycle):
                first_result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            with mock.patch.object(
                iteration_loop.iteration_cycle,
                "run_cycle",
                side_effect=AssertionError("resume should not rerun a completed loop"),
            ):
                resumed_result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path, resume=True)

            self.assertEqual("completed", first_result["status"])
            self.assertEqual("completed", resumed_result["status"])
            self.assertTrue(resumed_result["resume_requested"])
            self.assertTrue(resumed_result["resumed_from_existing"])
            self.assertEqual(1, resumed_result["round_count"])
            self.assertEqual(first_result["summary"], resumed_result["summary"])
            self.assertTrue(Path(resumed_result["summary"]).exists())

    def test_run_iteration_loop_resume_rejects_changed_plan_content(self) -> None:
        with make_tempdir() as tmp:
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            plan_path = workspace / "iteration-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "resume safety for deep loops",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "first attempt"},
                            {"round_id": "round-02", "candidate": "second attempt"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            def interrupted_run_cycle(**kwargs):
                round_id = str(kwargs["round_id"])
                if round_id == "round-02":
                    raise RuntimeError("simulated interruption")
                round_dir = workspace / round_id
                round_dir.mkdir(parents=True, exist_ok=True)
                (round_dir / "state.json").write_text(
                    json.dumps(
                        {
                            "round_id": round_id,
                            "candidate": kwargs["candidate"],
                            "hypothesis_key": kwargs["hypothesis_key"],
                            "decision": "retry",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return {"decision": "retry", "decision_reason": ["need another round"]}

            with mock.patch.object(iteration_loop.iteration_cycle, "run_cycle", side_effect=interrupted_run_cycle):
                with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                    iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

            plan_path.write_text(
                json.dumps(
                    {
                        "objective": "resume safety for deep loops",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "loop_policy": {
                            "max_rounds": 2,
                            "advance_baseline_on_keep": False,
                            "halt_on_decisions": ["stop"],
                            "sync_patterns_at_end": False,
                        },
                        "candidates": [
                            {"round_id": "round-01", "candidate": "first attempt"},
                            {"round_id": "round-02", "candidate": "changed second attempt"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "current plan content"):
                iteration_loop.run_loop(workspace=workspace, plan_path=plan_path, resume=True)


class ValidatorScriptTests(unittest.TestCase):
    def test_verify_action_outputs_match_json_schema(self) -> None:
        cases = [
            (
                "process-skill",
                "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
                {"process_skill": "pre-development-planning"},
            ),
            (
                "git-workflow",
                "Refactor this Flask service and then commit and push the branch.",
                {},
            ),
            (
                "worktree",
                "Use FastAPI for a backend service, then commit, push, and isolate the work in a worktree.",
                {},
            ),
            (
                "lead-assignment",
                "Review this Django API for security issues.",
                {"lead_agent": "Technical Trinity", "assistant_agents": []},
            ),
            (
                "release-gate",
                "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
                {},
            ),
            (
                "iteration",
                "Run another iteration, benchmark it against the baseline, and stop if the result regresses.",
                {},
            ),
            (
                "workflow-bundle",
                "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
                {},
            ),
            (
                "bundle-bootstrap",
                "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
                {},
            ),
            (
                "assistant-delta-contract",
                "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
                {},
            ),
            (
                "auto-mode",
                "/auto fix this repeated regression until stable and keep benchmark evidence",
                {},
            ),
        ]

        for check, text, kwargs in cases:
            with self.subTest(check=check):
                result = verify_action.verify_action(
                    text=text,
                    config=load_config(),
                    repo_path=REPO_ROOT,
                    check=check,
                    **kwargs,
                )
                response_contract.validate_verify_action_result(result)

    def test_verify_action_accepts_planning_process_skill(self) -> None:
        result = verify_action.verify_action(
            text="Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="process-skill",
            process_skill="pre-development-planning",
        )

        self.assertTrue(result["allowed"])
        self.assertEqual("process-skill", result["check"])
        self.assertIn("pre-development-planning", result["router_snapshot"]["process_skills"])
        assert_field_expectation(
            self,
            "workflow_bundle is plan-first-build",
            result["explanation_card"],
            label="verify_action.explanation_card",
        )
        assert_field_expectation(
            self,
            "workflow_source_explanation contains primary execution journey",
            result["explanation_card"],
            label="verify_action.explanation_card",
        )
        assert_field_expectation(
            self,
            "progress_anchor is docs/progress/MASTER.md",
            result["explanation_card"],
            label="verify_action.explanation_card",
        )

    def test_verify_action_accepts_git_workflow(self) -> None:
        result = verify_action.verify_action(
            text="Refactor this Flask service and then commit and push the branch.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="git-workflow",
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["details"]["needs_git_workflow"])
        self.assertIn("git-workflow", result["router_snapshot"]["process_skills"])

    def test_verify_action_accepts_worktree(self) -> None:
        result = verify_action.verify_action(
            text="Use FastAPI for a backend service, then commit, push, and isolate the work in a worktree.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="worktree",
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["details"]["needs_worktree"])
        self.assertEqual(
            result["details"]["repo_strategy"]["base_branch"],
            result["details"]["base_branch"],
        )

    def test_verify_action_rejects_wrong_lead_assignment(self) -> None:
        result = verify_action.verify_action(
            text="Review this Django API for security issues.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="lead-assignment",
            lead_agent="Technical Trinity",
            assistant_agents=[],
        )

        self.assertFalse(result["allowed"])
        self.assertEqual("Code Audit Council", result["details"]["expected_lead_agent"])

    def test_verify_action_auto_mode_requires_setup_before_go(self) -> None:
        result = verify_action.verify_action(
            text="/auto go Is this version ready to ship? Run the formal release gate.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="auto-mode",
        )

        self.assertFalse(result["allowed"])
        self.assertTrue(result["details"]["auto_mode_enabled"])
        self.assertEqual("go", result["details"]["requested_phase"])
        self.assertFalse(result["details"]["plan_exists"])
        self.assertIn("Run auto setup first", result["recommended_next_step"])

    def test_verify_action_auto_mode_exposes_safe_background_resume_details(self) -> None:
        result = verify_action.verify_action(
            text="/auto resume background safe fix this repeated regression until stable and keep benchmark evidence.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="auto-mode",
        )

        self.assertTrue(result["allowed"])
        self.assertEqual("background", result["details"]["run_style"])
        self.assertEqual("safe", result["details"]["safety_level"])
        self.assertTrue(result["details"]["resume_requested"])
        self.assertTrue(result["details"]["detached_ready"])
        self.assertEqual(".skill-auto/state", result["details"]["state_dir"])
        self.assertEqual(
            "references/automation-state.schema.json",
            result["details"]["automation_state_schema"],
        )

    def test_contract_lint_passes(self) -> None:
        result = contract_lint.lint_contract(SKILL_DIR)

        self.assertTrue(result["ok"], msg="\n".join(result["errors"]))

    def test_contract_lint_fails_on_version_mismatch_fixture(self) -> None:
        with make_tempdir() as tmp:
            fixture_dir = Path(tmp) / "virtual-intelligent-dev-team-fixture"
            shutil.copytree(SKILL_DIR, fixture_dir)
            (fixture_dir / "VERSION").write_text("v0.0.0\n", encoding="utf-8")

            result = contract_lint.lint_contract(fixture_dir)

            self.assertFalse(result["ok"])
            self.assertTrue(
                any("VERSION mismatch" in message for message in result["errors"]),
                msg="\n".join(result["errors"]),
            )

    def test_contract_lint_fails_on_process_skill_key_drift_fixture(self) -> None:
        with make_tempdir() as tmp:
            fixture_dir = Path(tmp) / "virtual-intelligent-dev-team-fixture"
            shutil.copytree(SKILL_DIR, fixture_dir)
            config_path = fixture_dir / "references" / "routing-rules.json"
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["process_skill_lead_agents"]["fake-skill"] = "Technical Trinity"
            config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = contract_lint.lint_contract(fixture_dir)

            self.assertFalse(result["ok"])
            self.assertTrue(
                any("process_skill_lead_agents has no matching process_skill_rules" in message for message in result["errors"]),
                msg="\n".join(result["errors"]),
            )

    def test_contract_lint_fails_on_missing_index_script_fixture(self) -> None:
        with make_tempdir() as tmp:
            fixture_dir = Path(tmp) / "virtual-intelligent-dev-team-fixture"
            shutil.copytree(SKILL_DIR, fixture_dir)
            index_path = fixture_dir / "references" / "tooling-command-index.md"
            index_path.write_text(
                index_path.read_text(encoding="utf-8")
                + "\n```bash\npython scripts/does_not_exist.py --pretty\n```\n",
                encoding="utf-8",
            )

            result = contract_lint.lint_contract(fixture_dir)

            self.assertFalse(result["ok"])
            self.assertTrue(
                any("contains commands for missing scripts" in message for message in result["errors"]),
                msg="\n".join(result["errors"]),
            )

    def test_contract_lint_fails_on_sidecar_schema_version_mismatch_fixture(self) -> None:
        with make_tempdir() as tmp:
            fixture_dir = Path(tmp) / "virtual-intelligent-dev-team-fixture"
            shutil.copytree(SKILL_DIR, fixture_dir)
            schema_path = fixture_dir / "references" / "response-pack-sidecar-schema.md"
            schema_path.write_text(
                schema_path.read_text(encoding="utf-8").replace(
                    "版本：`response-pack-sidecar/v1`",
                    "版本：`response-pack-sidecar/v999`",
                ),
                encoding="utf-8",
            )

            result = contract_lint.lint_contract(fixture_dir)

            self.assertFalse(result["ok"])
            self.assertTrue(
                any("Sidecar schema version mismatch" in message for message in result["errors"]),
                msg="\n".join(result["errors"]),
            )

    def test_contract_lint_fails_on_duplicate_eval_id_fixture(self) -> None:
        with make_tempdir() as tmp:
            fixture_dir = Path(tmp) / "virtual-intelligent-dev-team-fixture"
            shutil.copytree(SKILL_DIR, fixture_dir)
            evals_path = fixture_dir / "evals" / "evals.json"
            payload = json.loads(evals_path.read_text(encoding="utf-8"))
            payload["evals"][1]["id"] = payload["evals"][0]["id"]
            evals_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = contract_lint.lint_contract(fixture_dir)

            self.assertFalse(result["ok"])
            self.assertTrue(
                any("benchmark evals contract validation failed" in message for message in result["errors"]),
                msg="\n".join(result["errors"]),
            )

    def test_validator_script_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            cwd=str(REPO_ROOT),
            check=False,
            text=True,
            capture_output=True,
            encoding="utf-8",
        )

        self.assertEqual(0, proc.returncode, msg=proc.stdout + proc.stderr)


class OfflineLoopDrillScriptTests(unittest.TestCase):
    def test_offline_drill_covers_release_gate_hold_bootstrap(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp) / "offline-drill"

            result = offline_loop_drill.run_drill(workspace=root)

            self.assertTrue(result["ok"])
            scenarios = {
                item["scenario"]: item
                for item in result["scenarios"]
                if isinstance(item, dict) and "scenario" in item
            }
            self.assertIn("release-gate-hold-bootstrap", scenarios)
            hold_scenario = scenarios["release-gate-hold-bootstrap"]
            self.assertEqual("passed", hold_scenario["status"])
            self.assertTrue(Path(hold_scenario["plan"]).exists())
            self.assertTrue(Path(hold_scenario["brief_round_01"]).exists())
            self.assertTrue(Path(hold_scenario["remediation"]).exists())
            self.assertTrue(Path(hold_scenario["patch"]).exists())
            self.assertEqual(1, hold_scenario["round_count"])
            self.assertEqual(1, hold_scenario["decision_counts"]["keep"])


class BenchmarkAndReleaseGateTests(unittest.TestCase):
    def test_benchmark_expectation_supports_response_pack_contains(self) -> None:
        result = route_request.route_request(
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )
        markdown = response_pack.build_response_pack(result)
        payload = response_pack.build_response_pack_payload(result)

        ok, detail = benchmark_runner.parse_expectation(
            "response_pack contains Workflow source explanation: This bundle is activated by an explicit process skill, so it should be treated as the primary execution journey.",
            result,
            markdown,
            payload,
        )

        self.assertTrue(ok, detail)

    def test_benchmark_expectation_supports_response_pack_json(self) -> None:
        result = route_request.route_request(
            "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            load_config(),
            repo_path=REPO_ROOT,
        )
        markdown = response_pack.build_response_pack(result)
        payload = response_pack.build_response_pack_payload(result)

        ok, detail = benchmark_runner.parse_expectation(
            "response_pack_json resume.progress_anchor is docs/progress/MASTER.md",
            result,
            markdown,
            payload,
        )

        self.assertTrue(ok, detail)

    def test_benchmark_expectation_supports_verify_action_json(self) -> None:
        result = verify_action.verify_action(
            text="Refactor this Flask service and then commit and push the branch.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="git-workflow",
        )

        ok, detail = benchmark_runner.parse_expectation(
            "verify_action_json details.needs_git_workflow is true",
            result,
            "",
            {},
            {"verify_action_json": result},
        )

        self.assertTrue(ok, detail)

    def test_benchmark_expectation_supports_release_gate_json(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": False,
                        "overall_passed": False,
                    },
                    "json_report": str(output_dir / "benchmark-results.json"),
                    "markdown_report": str(output_dir / "benchmark-report.md"),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                result = release_gate.run_release_gate(output_dir=output_dir)

        ok, detail = benchmark_runner.parse_expectation(
            "release_gate_json follow_up.loop_state is reopened",
            result,
            "",
            {},
            {"release_gate_json": result},
        )

        self.assertTrue(ok, detail)

    def test_benchmark_field_expectation_supports_exists_length_and_comparison(self) -> None:
        result = route_request.route_request(
            "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            load_config(),
            repo_path=REPO_ROOT,
        )
        payload = response_pack.build_response_pack_payload(result)

        for expectation in [
            "planning_pack exists",
            "optimization_loop does not exist",
            "team_dispatch.assistant_agents length is 0",
            "team_dispatch.bundle_confidence >= 0.95",
            "resume.progress_anchor is not null",
        ]:
            with self.subTest(expectation=expectation):
                assert_field_expectation(self, expectation, payload, label="response_pack_json")

    def test_benchmark_field_expectation_supports_null_on_router_snapshot(self) -> None:
        result = verify_action.verify_action(
            text="Refactor this Flask service and then commit and push the branch.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="git-workflow",
        )

        assert_field_expectation(
            self,
            "progress_anchor_recommended is .skill-governance/change-plan.md",
            result["router_snapshot"],
            label="router_snapshot",
        )

    def test_run_benchmark_suite_can_include_offline_drill(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "benchmark-output"
            fake_eval_run = {
                "passed": 2,
                "total": 2,
                "cases": [
                    {
                        "id": 1,
                        "prompt": "a",
                        "lead_agent": "Technical Trinity",
                        "assistant_agents": [],
                        "passed": True,
                        "failures": [],
                    },
                    {
                        "id": 2,
                        "prompt": "b",
                        "lead_agent": "World-Class Product Architect",
                        "assistant_agents": ["Technical Trinity"],
                        "passed": True,
                        "failures": [],
                    },
                ],
                "category_breakdown": [
                    {"category": "iteration", "passed": 1, "total": 1, "pass_rate": 1.0},
                    {"category": "frontend", "passed": 1, "total": 1, "pass_rate": 1.0},
                ],
            }

            def fake_run_command(command, cwd):
                return {
                    "command": command,
                    "cwd": str(cwd),
                    "returncode": 0,
                    "stdout": "{}",
                    "stderr": "",
                    "passed": True,
                }

            with mock.patch.object(benchmark_runner, "run_command", side_effect=fake_run_command), \
                 mock.patch.object(benchmark_runner, "evaluate_evals", return_value=fake_eval_run), \
                 mock.patch.object(
                     benchmark_runner.offline_loop_drill,
                     "run_drill",
                     return_value={
                         "ok": True,
                         "workspace": str(output_dir / "offline-loop-drill"),
                         "markdown_report": str(output_dir / "offline-loop-drill" / "offline-loop-drill-report.md"),
                         "scenarios": [],
                     },
                 ):
                result = benchmark_runner.run_benchmark_suite(
                    output_dir=output_dir,
                    include_offline_drill=True,
                )

            self.assertTrue(result["summary"]["offline_drill_enabled"])
            self.assertTrue(result["summary"]["offline_drill_passed"])
            self.assertTrue(result["summary"]["overall_passed"])
            self.assertIn("offline_drill_run", result)
            self.assertTrue(Path(result["json_report"]).exists())
            report_payload = json.loads(Path(result["json_report"]).read_text(encoding="utf-8"))
            response_contract.validate_benchmark_run_result(report_payload)
            report = Path(result["markdown_report"]).read_text(encoding="utf-8")
            self.assertIn("Offline loop drill", report)

    def test_evaluate_evals_supports_verify_action_and_release_gate_runners(self) -> None:
        config = load_config()
        fixture = {
            "skill_name": "virtual-intelligent-dev-team",
            "evals": [
                {
                    "id": 9001,
                    "runner": "verify_action",
                    "check": "git-workflow",
                    "prompt": "Refactor this Flask service and then commit and push the branch.",
                    "expected_output": "verify_action runner should stay schema-valid for git-workflow decisions.",
                    "files": [],
                    "expectations": [
                        "allowed is true",
                        "verify_action_json details.needs_git_workflow is true"
                    ],
                    "categories": ["git-workflow"]
                },
                {
                    "id": 9002,
                    "runner": "release_gate",
                    "prompt": "Release gate fixture hold path",
                    "expected_output": "release_gate runner should return a hold decision when offline drill evidence fails.",
                    "files": [],
                    "release_gate_summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": False,
                        "overall_passed": False
                    },
                    "expectations": [
                        "decision is hold",
                        "release_gate_json follow_up.loop_state is reopened"
                    ],
                    "categories": ["release-gate"]
                }
            ]
        }
        with make_tempdir() as tmp:
            fixture_path = Path(tmp) / "evals.json"
            fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
            with mock.patch.object(benchmark_runner, "EVALS_PATH", fixture_path):
                result = benchmark_runner.evaluate_evals(config)

        self.assertEqual(2, result["passed"])
        self.assertEqual(2, result["total"])

    def test_evaluate_evals_rejects_invalid_verify_action_fixture_before_execution(self) -> None:
        config = load_config()
        fixture = {
            "skill_name": "virtual-intelligent-dev-team",
            "evals": [
                {
                    "id": 9101,
                    "runner": "verify_action",
                    "prompt": "Refactor this Flask service and then commit and push the branch.",
                    "expected_output": "invalid fixture should fail schema validation before execution.",
                    "files": [],
                    "expectations": ["allowed is true"],
                    "categories": ["git-workflow"]
                }
            ]
        }
        with make_tempdir() as tmp:
            fixture_path = Path(tmp) / "evals.json"
            fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
            with mock.patch.object(benchmark_runner, "EVALS_PATH", fixture_path):
                with self.assertRaisesRegex(ValueError, "benchmark evals schema validation failed"):
                    benchmark_runner.evaluate_evals(config)

    def test_evaluate_evals_rejects_duplicate_eval_ids_before_execution(self) -> None:
        config = load_config()
        fixture = {
            "skill_name": "virtual-intelligent-dev-team",
            "evals": [
                {
                    "id": 9201,
                    "prompt": "Please review this Java GC issue and give recommendations.",
                    "expected_output": "route runner baseline fixture.",
                    "files": [],
                    "expectations": ["lead_agent is Code Audit Council"],
                    "categories": ["review"]
                },
                {
                    "id": 9201,
                    "prompt": "Design a Go plus Gin high-concurrency API gateway.",
                    "expected_output": "duplicate id fixture should be rejected.",
                    "files": [],
                    "expectations": ["lead_agent is Technical Trinity"],
                    "categories": ["backend-stack"]
                }
            ]
        }
        with make_tempdir() as tmp:
            fixture_path = Path(tmp) / "evals.json"
            fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
            with mock.patch.object(benchmark_runner, "EVALS_PATH", fixture_path):
                with self.assertRaisesRegex(ValueError, "duplicate eval ids"):
                    benchmark_runner.evaluate_evals(config)

    def test_release_gate_holds_when_offline_drill_fails(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"
            benchmark_output = output_dir / "benchmark-results.json"
            benchmark_report = output_dir / "benchmark-report.md"

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": False,
                        "overall_passed": False,
                    },
                    "json_report": str(benchmark_output),
                    "markdown_report": str(benchmark_report),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                result = release_gate.run_release_gate(output_dir=output_dir)

            response_contract.validate_release_gate_result(result)
            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertEqual("offline loop drill failed", result["reason"])
            self.assertTrue(Path(result["json_report"]).exists())
            self.assertTrue(Path(result["markdown_report"]).exists())
            self.assertTrue(Path(result["automation_state"]["state_paths"]["primary"]).exists())
            self.assertEqual("release-gate-result", result["automation_state"]["state_kind"])
            self.assertEqual("reopened", result["follow_up"]["loop_state"])
            self.assertEqual("bounded-iteration", result["follow_up"]["next_action"])
            assert_field_expectation(
                self,
                "workflow_bundle is ship-hold-remediate",
                result["explanation_card"],
                label="release_gate.explanation_card",
            )
            assert_field_expectation(
                self,
                "workflow_source_explanation contains Release gate is the active acceptance lane",
                result["explanation_card"],
                label="release_gate.explanation_card",
            )
            self.assertTrue(Path(result["follow_up"]["brief_json"]).exists())
            self.assertTrue(Path(result["follow_up"]["brief_markdown"]).exists())
            markdown = Path(result["markdown_report"]).read_text(encoding="utf-8")
            self.assertIn("## Evidence", markdown)
            self.assertIn("## Resume", markdown)

    def test_release_gate_holds_when_beta_gate_is_not_advanced(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"
            beta_root = Path(tmp) / ".skill-beta"
            beta_gate_result = write_beta_gate_fixture(
                beta_root,
                round_id="round-02",
                decision="hold",
                reason="This round has not yet cleared the minimum sample, success-rate, or blocker thresholds.",
            )

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": True,
                    },
                    "json_report": str(output_dir / "benchmark-results.json"),
                    "markdown_report": str(output_dir / "benchmark-report.md"),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                benchmark_payload = {
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": True,
                    },
                    "eval_run": {"passed": 56, "total": 56, "cases": [], "category_breakdown": []},
                }
                Path(output_dir / "benchmark-results.json").parent.mkdir(parents=True, exist_ok=True)
                (output_dir / "benchmark-results.json").write_text(
                    json.dumps(benchmark_payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                (output_dir / "benchmark-report.md").write_text("# Benchmark Report\n", encoding="utf-8")
                result = release_gate.run_release_gate(
                    output_dir=output_dir,
                    beta_gate_result=beta_gate_result,
                )

            response_contract.validate_release_gate_result(result)
            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertIn("latest beta round gate is `hold`", result["reason"])
            self.assertTrue(result["summary"]["beta_gate_enabled"])
            self.assertFalse(result["summary"]["beta_gate_passed"])
            self.assertEqual("hold", result["summary"]["beta_gate_decision"])
            self.assertEqual("round-02", result["summary"]["beta_gate_round_id"])
            self.assertEqual("hold", result["beta_gate"]["decision"])
            self.assertEqual("round-02", result["beta_gate"]["round_id"])
            self.assertEqual(str(beta_gate_result), result["beta_gate"]["json_report"])
            self.assertIn("blocker_breakdown", result["beta_gate"])
            brief = baseline_registry.load_json(Path(result["follow_up"]["brief_json"]))
            self.assertIn("beta_gate_context", brief)
            self.assertEqual("hold", brief["beta_gate_context"]["decision"])
            self.assertEqual(
                "First-Time Novice",
                brief["beta_gate_context"]["blocker_breakdown"]["by_persona"][0]["label"],
            )
            self.assertTrue(any("beta round round-02" in item for item in result["follow_up"]["blockers"]))
            self.assertIn(str(beta_gate_result), result["explanation_card"]["resume_artifacts"])

    def test_release_gate_can_resolve_latest_beta_report_from_report_dir(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            output_dir = root / "release-gate-output"
            beta_round_report_init.init_beta_round_report(
                root=root,
                round_id="round-01",
                phase="closed beta",
                sample_size=8,
                participant_mode="seed users",
                goal="Validate onboarding basics.",
                exit_criteria="Advance only when the flow is stable.",
            )
            beta_round_report_init.init_beta_round_report(
                root=root,
                round_id="round-02",
                phase="expanded internal beta",
                sample_size=16,
                participant_mode="internal beta users",
                goal="Validate cross-role onboarding.",
                exit_criteria="Advance only when blocker count is zero.",
            )

            report_path = root / ".skill-beta" / "reports" / "round-02.json"
            report_payload = baseline_registry.load_json(report_path)
            report_payload["completed_sessions"] = 16
            report_payload["task_success_count"] = 12
            report_payload["blocker_issue_count"] = 1
            report_payload["critical_issue_count"] = 0
            report_payload["high_severity_issue_count"] = 1
            report_payload["top_feedback_themes"] = ["permission confusion"]
            report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            benchmark_payload = {
                "summary": {
                    "tests_passed": True,
                    "validator_passed": True,
                    "evals_passed": True,
                    "offline_drill_enabled": True,
                    "offline_drill_passed": True,
                    "overall_passed": True,
                },
                "eval_run": {"passed": 56, "total": 56, "cases": [], "category_breakdown": []},
            }
            Path(output_dir / "benchmark-results.json").parent.mkdir(parents=True, exist_ok=True)
            (output_dir / "benchmark-results.json").write_text(
                json.dumps(benchmark_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (output_dir / "benchmark-report.md").write_text("# Benchmark Report\n", encoding="utf-8")
            (output_dir / "offline-loop-drill-report.md").write_text("# Offline Loop Drill Report\n", encoding="utf-8")

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": benchmark_payload["summary"],
                    "json_report": str(output_dir / "benchmark-results.json"),
                    "markdown_report": str(output_dir / "benchmark-report.md"),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                result = release_gate.run_release_gate(
                    output_dir=output_dir,
                    beta_report_dir=root / ".skill-beta" / "reports",
                )

            response_contract.validate_release_gate_result(result)
            self.assertEqual("hold", result["decision"])
            self.assertEqual("beta-report-dir", result["beta_gate"]["source"])
            self.assertEqual("round-02", result["beta_gate"]["round_id"])
            self.assertEqual("hold", result["beta_gate"]["decision"])
            self.assertTrue(Path(result["beta_gate"]["json_report"]).exists())

    def test_release_gate_hold_absorbs_beta_remediation_brief(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"
            beta_root = Path(tmp) / ".skill-beta"
            round_id = "round-02"
            beta_decision_dir = beta_root / "round-decisions" / round_id
            beta_decision_dir.mkdir(parents=True, exist_ok=True)
            beta_brief_json = beta_decision_dir / "next-round-remediation-brief.json"
            beta_brief_markdown = beta_decision_dir / "next-round-remediation-brief.md"
            product_writeback = beta_decision_dir / "product-writeback.md"
            governance_writeback = beta_decision_dir / "governance-writeback.md"
            beta_brief_payload = {
                "schema_version": "beta-remediation-brief/v1",
                "generated_at": "2026-04-08T12:00:00Z",
                "source_gate": "beta-round-gate",
                "decision": "hold",
                "loop_state": "reopened",
                "owner": "World-Class Product Architect",
                "round_id": round_id,
                "reason": "Cohort plan does not match the resolved fixture.",
                "objective": "repair the beta blockers for round-02",
                "objective_hints": [
                    "reconcile the cohort plan with the fixture manifest"
                ],
                "blockers": [
                    {
                        "id": "cohort-plan-mismatch",
                        "label": "cohort plan does not match the resolved fixture",
                        "objective_hint": "update the cohort plan so planned sessions and persona counts align",
                        "evidence_required": "python scripts/evaluate_beta_round.py --report .skill-beta/reports/round-02.json --pretty"
                    }
                ],
                "gate_context": {
                    "cohort_gate_status": "mismatch",
                    "ramp_gate_status": "passed",
                    "diff_gate_status": "passed",
                    "continue_beta": False,
                    "release_governance_recommended": False,
                    "next_round_recommended": round_id
                },
                "blocker_breakdown": {
                    "by_persona": [
                        {
                            "label": "First-Time Novice",
                            "session_count": 2,
                            "blocker_issue_count": 1,
                            "critical_issue_count": 0,
                            "high_severity_issue_count": 1,
                            "session_ids": ["session-01", "session-02"],
                            "top_feedback_themes": ["onboarding confusion"]
                        }
                    ],
                    "by_scenario": [
                        {
                            "label": "first meaningful task",
                            "session_count": 2,
                            "blocker_issue_count": 1,
                            "critical_issue_count": 0,
                            "high_severity_issue_count": 1,
                            "session_ids": ["session-01", "session-02"],
                            "top_feedback_themes": ["onboarding confusion"]
                        }
                    ]
                },
                "report_context": {
                    "report_path": str(beta_root / "reports" / f"{round_id}.json"),
                    "source_simulation_run": str(beta_root / "simulation-runs" / round_id / "beta-simulation-run.json"),
                    "feedback_ledger_markdown": str(beta_root / "feedback-ledger.md"),
                    "fixture_manifest_json": str(beta_root / "fixture-previews" / round_id / "beta-simulation-manifest.json"),
                    "cohort_plan_json": str(beta_root / "cohort-plan.json"),
                    "ramp_plan_json": str(beta_root / "ramp-plan.json"),
                    "fixture_diff_json": str(beta_root / "fixture-diffs" / f"round-01-to-{round_id}" / "beta-simulation-diff.json")
                },
                "recommended_commands": [
                    "python scripts/preview_beta_simulation_fixture.py --config .skill-beta/simulation-configs/round-02.json --pretty",
                    "python scripts/evaluate_beta_round.py --report .skill-beta/reports/round-02.json --pretty"
                ],
                "required_evidence": [
                    "python scripts/evaluate_beta_round.py --report .skill-beta/reports/round-02.json --pretty"
                ],
                "resume_artifacts": [
                    str(product_writeback),
                    str(governance_writeback)
                ]
            }
            response_contract.validate_beta_remediation_brief(beta_brief_payload)
            beta_brief_json.write_text(json.dumps(beta_brief_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            beta_brief_markdown.write_text("# Beta Remediation Brief\n", encoding="utf-8")
            product_writeback.write_text("# Product Writeback\n", encoding="utf-8")
            governance_writeback.write_text("# Governance Writeback\n", encoding="utf-8")
            beta_gate_result = write_beta_gate_fixture(
                beta_root,
                round_id=round_id,
                decision="hold",
                reason="This round has not yet cleared the minimum sample, success-rate, or blocker thresholds.",
                follow_up_extra={
                    "loop_state": "reopened",
                    "blockers": ["cohort plan does not match the resolved fixture"],
                    "brief_json": str(beta_brief_json),
                    "brief_markdown": str(beta_brief_markdown),
                    "resume_artifacts": [str(product_writeback), str(governance_writeback)]
                },
            )

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": True,
                    },
                    "json_report": str(output_dir / "benchmark-results.json"),
                    "markdown_report": str(output_dir / "benchmark-report.md"),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                benchmark_payload = {
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": True,
                    },
                    "eval_run": {"passed": 56, "total": 56, "cases": [], "category_breakdown": []},
                }
                Path(output_dir / "benchmark-results.json").parent.mkdir(parents=True, exist_ok=True)
                (output_dir / "benchmark-results.json").write_text(
                    json.dumps(benchmark_payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                (output_dir / "benchmark-report.md").write_text("# Benchmark Report\n", encoding="utf-8")
                result = release_gate.run_release_gate(
                    output_dir=output_dir,
                    beta_gate_result=beta_gate_result,
                )

            response_contract.validate_release_gate_result(result)
            brief = baseline_registry.load_json(Path(result["follow_up"]["brief_json"]))
            self.assertIn("beta remediation: cohort plan does not match the resolved fixture", " ".join(item["label"] for item in brief["blockers"]))
            self.assertIn(str(beta_brief_json), result["explanation_card"]["resume_artifacts"])
            self.assertIn(str(product_writeback), result["explanation_card"]["resume_artifacts"])
            self.assertIn(str(governance_writeback), result["explanation_card"]["resume_artifacts"])
            self.assertIn(str(product_writeback), brief["resume_artifacts"])
            self.assertTrue(any("preview_beta_simulation_fixture.py" in item for item in brief["recommended_commands"]))

    def test_release_gate_hold_emits_next_iteration_brief(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": False,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": False,
                    },
                    "json_report": str(output_dir / "benchmark-results.json"),
                    "markdown_report": str(output_dir / "benchmark-report.md"),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                result = release_gate.run_release_gate(output_dir=output_dir)

            response_contract.validate_release_gate_result(result)
            brief = baseline_registry.load_json(Path(result["follow_up"]["brief_json"]))
            self.assertEqual("hold", result["decision"])
            self.assertEqual("reopened", brief["loop_state"])
            self.assertEqual("Technical Trinity", brief["owner"])
            self.assertIn("unit tests failed", " ".join(brief["blockers"][0]["label"] for _ in [0]))
            self.assertIn("benchmark_context", brief)
            self.assertFalse(brief["benchmark_context"]["unit_tests"]["passed"])
            self.assertTrue(any("run_release_gate.py" in item for item in brief["recommended_commands"]))

    def test_release_gate_hold_bootstraps_iteration_workspace_when_provided(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"
            workspace = Path(tmp) / "rounds"

            benchmark_output = output_dir / "benchmark-results.json"
            benchmark_report = output_dir / "benchmark-report.md"
            benchmark_output.parent.mkdir(parents=True, exist_ok=True)
            benchmark_output.write_text(
                json.dumps(
                    {
                        "summary": {"overall_passed": False},
                        "eval_run": {"passed": 55, "total": 56},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            benchmark_report.write_text("# Benchmark Report\n", encoding="utf-8")

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": False,
                        "validator_passed": True,
                        "evals_passed": False,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": False,
                    },
                    "json_report": str(benchmark_output),
                    "markdown_report": str(benchmark_report),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                result = release_gate.run_release_gate(
                    output_dir=output_dir,
                    iteration_workspace=workspace,
                )

            response_contract.validate_release_gate_result(result)
            bootstrap = result["follow_up"]["bootstrap"]
            self.assertTrue(Path(bootstrap["candidate_repo"]).exists())
            self.assertTrue((Path(bootstrap["candidate_repo"]) / "scripts" / "run_release_gate.py").exists())
            self.assertFalse((Path(bootstrap["candidate_repo"]) / ".git").exists())
            self.assertTrue(Path(bootstrap["plan_json"]).exists())
            self.assertTrue(Path(bootstrap["open_loops"]).exists())
            self.assertTrue(Path(bootstrap["iteration_context_chain"]).exists())
            self.assertIn("run_iteration_loop.py", bootstrap["recommended_command"])
            baseline_result = bootstrap["baseline_registration"]
            self.assertEqual("stable", baseline_result["label"])
            self.assertTrue(Path(baseline_result["stored_report"]).exists())
            plan_payload = baseline_registry.load_json(Path(bootstrap["plan_json"]))
            self.assertEqual("./repo-copy", plan_payload["candidate_repo_template"])
            self.assertEqual("./patches/{round_id}.patch", plan_payload["candidate_patch_template"])
            self.assertEqual("./candidate-briefs/{round_id}.json", plan_payload["candidate_brief_template"])
            self.assertTrue(plan_payload["autonomous_candidate_generation"])
            self.assertTrue(plan_payload["auto_apply_rollback"])
            self.assertTrue(len(plan_payload["mutation_catalog"]) >= 1)
            catalog_ids = {item["id"] for item in plan_payload["mutation_catalog"]}
            self.assertIn("release-gate-unit-tests-remediation", catalog_ids)
            self.assertIn("release-gate-eval-suite-remediation", catalog_ids)
            self.assertEqual("round-01", plan_payload["candidates"][0]["round_id"])
            self.assertIn("mutation_plan", plan_payload["candidates"][0])
            candidate_paths = {
                item["path"]
                for item in plan_payload["candidates"][0]["mutation_plan"]["operations"]
                if isinstance(item, dict) and "path" in item
            }
            self.assertIn(
                "artifacts/release-gate-hold/{round_id}-unit-tests-remediation.md",
                candidate_paths,
            )

            eval_rule = next(
                item
                for item in plan_payload["mutation_catalog"]
                if item["id"] == "release-gate-eval-suite-remediation"
            )
            eval_targets_content = next(
                op["content"]
                for op in eval_rule["mutation_plan"]["operations"]
                if op["path"] == "artifacts/release-gate-hold/{round_id}-eval-suite-targets.json"
            )
            eval_targets = json.loads(eval_targets_content)
            self.assertIn("evals/evals.json", eval_targets["target_files"])
            self.assertIn("json_append_unique", eval_targets["preferred_mutation_ops"])

    def test_release_gate_hold_mutation_catalog_is_blocker_specific(self) -> None:
        brief = {
            "objective": "恢复 release gate 就绪状态",
            "reason": "semantic regression validator failed",
            "owner": "Technical Trinity",
            "blockers": [
                {
                    "id": "semantic-regression",
                    "label": "semantic regression validator failed",
                    "objective_hint": "修复语义回归后，再验证路由与流程闭环",
                    "evidence_required": "python scripts/validate_virtual_team.py --pretty",
                },
                {
                    "id": "offline-loop-drill",
                    "label": "offline loop drill failed",
                    "objective_hint": "修复 rollback / pivot / resume 闭环问题，再重新验收",
                    "evidence_required": "python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty",
                },
            ],
            "benchmark_context": {
                "semantic_regression": {
                    "passed": False,
                    "output_excerpt": [
                        "validator mismatch on routing-rules version",
                    ],
                },
                "offline_loop_drill": {
                    "enabled": True,
                    "passed": False,
                    "markdown_report": "/tmp/offline-loop-drill-report.md",
                },
            },
            "required_evidence": [
                "python scripts/validate_virtual_team.py --pretty",
                "python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty",
            ],
        }

        catalog = release_gate.build_hold_mutation_catalog(brief)
        catalog_ids = {item["id"] for item in catalog}
        self.assertIn("release-gate-semantic-regression-remediation", catalog_ids)
        self.assertIn("release-gate-offline-loop-drill-remediation", catalog_ids)

        semantic_rule = next(
            item for item in catalog if item["id"] == "release-gate-semantic-regression-remediation"
        )
        self.assertIn(
            "validator mismatch on routing-rules version",
            " ".join(semantic_rule["when_any_keywords"]),
        )
        semantic_targets_content = next(
            op["content"]
            for op in semantic_rule["mutation_plan"]["operations"]
            if op["path"] == "artifacts/release-gate-hold/{round_id}-semantic-regression-targets.json"
        )
        semantic_targets = json.loads(semantic_targets_content)
        self.assertIn("scripts/route_request.py", semantic_targets["target_files"])
        self.assertIn("json_set", semantic_targets["preferred_mutation_ops"])

        offline_rule = next(
            item for item in catalog if item["id"] == "release-gate-offline-loop-drill-remediation"
        )
        offline_targets_content = next(
            op["content"]
            for op in offline_rule["mutation_plan"]["operations"]
            if op["path"] == "artifacts/release-gate-hold/{round_id}-offline-loop-drill-targets.json"
        )
        offline_targets = json.loads(offline_targets_content)
        self.assertIn("scripts/run_iteration_loop.py", offline_targets["target_files"])
        self.assertIn("write_file", offline_targets["preferred_mutation_ops"])

    def test_release_gate_hold_can_auto_run_next_iteration_loop(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"
            workspace = Path(tmp) / "rounds"
            benchmark_output = output_dir / "benchmark-results.json"
            benchmark_report = output_dir / "benchmark-report.md"
            benchmark_output.parent.mkdir(parents=True, exist_ok=True)
            benchmark_output.write_text(
                json.dumps(
                    {
                        "summary": {"overall_passed": False},
                        "eval_run": {"passed": 55, "total": 56},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            benchmark_report.write_text("# Benchmark Report\n", encoding="utf-8")

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": False,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": False,
                    },
                    "json_report": str(benchmark_output),
                    "markdown_report": str(benchmark_report),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ), mock.patch.object(
                release_gate.iteration_loop,
                "run_loop",
                return_value={"status": "completed", "round_count": 1},
            ) as run_loop_mock:
                result = release_gate.run_release_gate(
                    output_dir=output_dir,
                    iteration_workspace=workspace,
                    auto_run_next_iteration_on_hold=True,
                )

            response_contract.validate_release_gate_result(result)
            bootstrap = result["follow_up"]["bootstrap"]
            self.assertEqual("completed", bootstrap["auto_iteration"]["status"])
            self.assertEqual(1, bootstrap["auto_iteration"]["result"]["round_count"])
            run_loop_mock.assert_called_once()

    def test_release_gate_ship_can_archive_release_ready_baseline(self) -> None:
        with make_tempdir() as tmp:
            output_dir = Path(tmp) / "release-gate-output"
            workspace = Path(tmp) / "rounds"
            workspace.mkdir(parents=True, exist_ok=True)
            benchmark_output = output_dir / "benchmark-results.json"
            benchmark_report = output_dir / "benchmark-report.md"
            benchmark_output.parent.mkdir(parents=True, exist_ok=True)
            benchmark_output.write_text(
                json.dumps(
                    {
                        "summary": {"overall_passed": True},
                        "eval_run": {"passed": 56, "total": 56},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            benchmark_report.write_text("# Benchmark Report\n", encoding="utf-8")
            round_dir = workspace / "round-01"
            round_dir.mkdir(parents=True, exist_ok=True)
            (round_dir / "state.json").write_text(
                json.dumps(
                    {
                        "round_id": "round-01",
                        "decision": "keep",
                        "objective": "stabilize release gate",
                        "owner": "Technical Trinity",
                        "baseline_label": "stable",
                        "candidate": "tighten release follow-up loop",
                        "decision_reason": ["keep only after all release gates pass"],
                        "comparison": {
                            "baseline": {"overall_passed": True, "evals_passed": 54, "evals_total": 54},
                            "candidate": {"overall_passed": True, "evals_passed": 56, "evals_total": 56},
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": True,
                    },
                    "json_report": str(benchmark_output),
                    "markdown_report": str(benchmark_report),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                result = release_gate.run_release_gate(
                    output_dir=output_dir,
                    iteration_workspace=workspace,
                    release_label="v4.20.0",
                )

            response_contract.validate_release_gate_result(result)
            self.assertTrue(result["ok"])
            self.assertEqual("ship", result["decision"])
            self.assertEqual("closed", result["follow_up"]["loop_state"])
            self.assertEqual("v4.20.0", result["follow_up"]["release_label"])
            self.assertTrue(Path(result["follow_up"]["closure_json"]).exists())
            self.assertTrue(Path(result["follow_up"]["closure_markdown"]).exists())
            baseline_result = result["follow_up"]["baseline_registration"]
            self.assertEqual("v4.20.0", baseline_result["label"])
            self.assertTrue(Path(baseline_result["stored_report"]).exists())
            sync_result = result["follow_up"]["distilled_pattern_sync"]
            self.assertTrue(Path(sync_result["distilled_patterns"]).exists())
            self.assertEqual(1, sync_result["kept_rounds"])
            post_release_bootstrap = result["follow_up"]["post_release_bootstrap"]
            self.assertTrue(Path(post_release_bootstrap["resume_anchor"]).exists())
            self.assertTrue(Path(post_release_bootstrap["signal_report"]).exists())
            self.assertTrue(any(item.endswith(".skill-post-release/triage-summary.md") for item in result["explanation_card"]["resume_artifacts"]))


class ProjectMemoryInitTests(unittest.TestCase):
    def test_init_project_memory_all_creates_expected_anchors(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = project_memory_init.init_project_memory(root=root, mode="all", overwrite=False)

            self.assertTrue(result["ok"])
            self.assertEqual("all", result["mode"])
            self.assertTrue((root / "docs" / "progress" / "MASTER.md").exists())
            self.assertTrue((root / ".skill-iterations" / "current-round-memory.md").exists())
            self.assertTrue((root / ".skill-iterations" / "distilled-patterns.md").exists())

    def test_init_project_memory_respects_no_overwrite(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            target = root / ".skill-iterations" / "current-round-memory.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("custom\n", encoding="utf-8")

            result = project_memory_init.init_project_memory(root=root, mode="iteration", overwrite=False)

            self.assertEqual("custom\n", target.read_text(encoding="utf-8"))
            statuses = {item["target"]: item["status"] for item in result["actions"]}
            self.assertEqual("skipped", statuses[".skill-iterations/current-round-memory.md"])

    def test_init_product_delivery_creates_expected_anchors(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = product_delivery_init.init_product_delivery(root=root, overwrite=False)

            self.assertTrue(result["ok"])
            self.assertTrue((root / ".skill-product" / "current-slice.md").exists())
            self.assertTrue((root / ".skill-product" / "acceptance-criteria.md").exists())
            self.assertTrue((root / ".skill-product" / "contract-questions.md").exists())
            self.assertEqual(".skill-product/current-slice.md", result["resume_anchor"])

    def test_init_beta_validation_creates_expected_anchors(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = beta_validation_init.init_beta_validation(root=root, overwrite=False)

            self.assertTrue(result["ok"])
            self.assertTrue((root / ".skill-beta" / "program-overview.md").exists())
            self.assertTrue((root / ".skill-beta" / "cohort-matrix.md").exists())
            self.assertTrue((root / ".skill-beta" / "feedback-ledger.md").exists())
            self.assertTrue((root / ".skill-beta" / "cohort-plan.json").exists())
            self.assertTrue((root / ".skill-beta" / "ramp-plan.json").exists())
            cohort_plan = json.loads((root / ".skill-beta" / "cohort-plan.json").read_text(encoding="utf-8"))
            response_contract.validate_beta_cohort_plan(cohort_plan)
            ramp_plan = json.loads((root / ".skill-beta" / "ramp-plan.json").read_text(encoding="utf-8"))
            response_contract.validate_beta_ramp_plan(ramp_plan)
            self.assertEqual(".skill-beta/program-overview.md", result["resume_anchor"])

    def test_init_beta_round_report_creates_machine_readable_report(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = beta_round_report_init.init_beta_round_report(
                root=root,
                round_id="round-1",
                phase="closed beta",
                sample_size=12,
                participant_mode="seed users",
                goal="validate the implemented slice",
                exit_criteria="no blocker-level failures remain",
                overwrite=False,
            )

            target = root / ".skill-beta" / "reports" / "round-1.json"
            self.assertTrue(result["ok"])
            self.assertEqual(".skill-beta/reports/round-1.json", result["report_path"])
            self.assertTrue(target.exists())
            payload = json.loads(target.read_text(encoding="utf-8"))
            response_contract.validate_beta_round_report(payload)
            self.assertEqual("round-1", payload["round_id"])

    def test_init_beta_simulation_creates_profiles_and_config(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-0",
                phase="pre-build concept smoke",
                objective="validate the promise before implementation hardens",
                overwrite=False,
            )

            config_path = root / ".skill-beta" / "simulation-configs" / "round-0.json"
            self.assertTrue(result["ok"])
            self.assertEqual(".skill-beta/simulation-configs/round-0.json", result["config_path"])
            self.assertTrue(config_path.exists())
            config_payload = json.loads(config_path.read_text(encoding="utf-8"))
            response_contract.validate_beta_simulation_config(config_payload)
            self.assertEqual(".skill-beta/feedback-ledger.md", config_payload["feedback_ledger_out"])
            self.assertIn("--feedback-ledger-out .skill-beta/feedback-ledger.md", config_payload["summary_command_template"])
            self.assertEqual("references/simulation-cohort-fixtures.json", config_payload["cohort_fixture_source"])
            self.assertEqual("references/simulation-trace-catalog.json", config_payload["trace_catalog_source"])
            self.assertEqual("round-0-default", result["cohort_fixture_id"])
            self.assertTrue((root / result["fixture_manifest_json"]).exists())
            self.assertTrue((root / result["fixture_manifest_markdown"]).exists())
            self.assertIsNone(result["fixture_diff_json"])
            self.assertIsNone(result["fixture_diff_markdown"])
            self.assertTrue((root / ".skill-beta" / "personas" / "first-time-novice.json").exists())
            self.assertTrue((REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-persona-library.json").exists())
            self.assertTrue((REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-cohort-fixtures.json").exists())
            self.assertTrue((REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-scenario-packs.json").exists())
            self.assertTrue((REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-trace-catalog.json").exists())
            self.assertTrue(all("trace_id" in item for item in config_payload["session_plan"]))
            self.assertGreaterEqual(result["session_count"], 3)

    def test_simulation_reference_schemas_validate_repository_resources(self) -> None:
        persona_library = json.loads(
            (REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-persona-library.json").read_text(
                encoding="utf-8"
            )
        )
        cohort_fixtures = json.loads(
            (REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-cohort-fixtures.json").read_text(
                encoding="utf-8"
            )
        )
        scenario_packs = json.loads(
            (REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-scenario-packs.json").read_text(
                encoding="utf-8"
            )
        )
        trace_catalog = json.loads(
            (REPO_ROOT / "virtual-intelligent-dev-team" / "references" / "simulation-trace-catalog.json").read_text(
                encoding="utf-8"
            )
        )

        response_contract.validate_simulation_persona_library(persona_library)
        response_contract.validate_simulation_cohort_fixtures(cohort_fixtures)
        response_contract.validate_simulation_scenario_packs(scenario_packs)
        response_contract.validate_simulation_trace_catalog(trace_catalog)

    def test_preview_beta_simulation_fixture_emits_manifest(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            init_result = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                overwrite=False,
            )

            result = beta_simulation_preview.preview_beta_simulation_fixture(
                config_path=root / init_result["config_path"],
            )

            self.assertEqual("beta-simulation-manifest/v1", result["schema_version"])
            response_contract.validate_beta_simulation_manifest(result)
            self.assertTrue(Path(result["json_report"]).exists())
            self.assertTrue(Path(result["markdown_report"]).exists())
            self.assertTrue(all(session["trace_id"] for session in result["sessions"]))

    def test_compare_beta_simulation_manifests_emits_structured_diff(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            round_0 = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-0",
                phase="pre-build concept smoke",
                objective="validate the promise before implementation hardens",
                overwrite=False,
            )
            round_1 = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                overwrite=False,
            )

            result = beta_simulation_compare.compare_beta_simulation_manifests(
                previous_manifest_path=root / round_0["fixture_manifest_json"],
                current_manifest_path=root / round_1["fixture_manifest_json"],
            )

            self.assertEqual("beta-simulation-diff/v1", result["schema_version"])
            response_contract.validate_beta_simulation_diff(result)
            self.assertEqual("round-0", result["previous_round_id"])
            self.assertEqual("round-1", result["current_round_id"])
            self.assertTrue(Path(result["json_report"]).exists())
            self.assertTrue(Path(result["markdown_report"]).exists())
            self.assertGreaterEqual(result["session_count_delta"], 1)
            self.assertGreaterEqual(len(result["new_session_matrix"]), 1)
            self.assertIn(
                result["coverage_shift_summary"]["expansion_mode"],
                {"expanded", "mixed"},
            )

    def test_init_beta_simulation_emits_fixture_diff_when_previous_manifest_exists(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-0",
                phase="pre-build concept smoke",
                objective="validate the promise before implementation hardens",
                overwrite=False,
            )
            result = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                overwrite=False,
            )

            self.assertEqual(
                ".skill-beta/fixture-previews/round-0/beta-simulation-manifest.json",
                result["previous_fixture_manifest_json"],
            )
            self.assertIsNotNone(result["fixture_diff_json"])
            self.assertIsNotNone(result["fixture_diff_markdown"])
            diff_payload = json.loads((root / str(result["fixture_diff_json"])).read_text(encoding="utf-8"))
            response_contract.validate_beta_simulation_diff(diff_payload)
            self.assertEqual("round-0", diff_payload["previous_round_id"])
            self.assertEqual("round-1", diff_payload["current_round_id"])
            self.assertTrue((root / str(result["fixture_diff_markdown"])).exists())

    def test_run_beta_simulation_emits_machine_readable_trace(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            init_result = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                overwrite=False,
            )
            config_path = root / init_result["config_path"]

            result = beta_simulation_runner.run_beta_simulation(config_path=config_path)

            self.assertEqual("beta-simulation-run/v1", result["schema_version"])
            self.assertTrue(Path(result["json_report"]).exists())
            self.assertTrue(Path(result["markdown_report"]).exists())
            response_contract.validate_beta_simulation_run(result)
            self.assertGreaterEqual(len(result["sessions"]), 4)
            self.assertTrue(any(session["blocker_detected"] for session in result["sessions"]))
            self.assertTrue(any(len(session["events"]) >= 2 for session in result["sessions"]))
            self.assertEqual("references/simulation-trace-catalog.json", result["trace_catalog_source"])
            self.assertTrue(all(session.get("trace_id") for session in result["sessions"]))

    def test_summarize_beta_simulation_can_write_round_report(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            beta_validation_init.init_beta_validation(root=root, overwrite=False)
            beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-0",
                phase="pre-build concept smoke",
                objective="validate the promise before implementation hardens",
                overwrite=False,
            )
            init_result = beta_simulation_init.init_beta_simulation(
                root=root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                overwrite=False,
            )
            run_result = beta_simulation_runner.run_beta_simulation(
                config_path=root / init_result["config_path"],
            )

            summary_result = beta_simulation_summary.summarize_beta_simulation(
                run_path=Path(run_result["json_report"]),
                feedback_ledger_out=root / ".skill-beta" / "feedback-ledger.md",
                round_report_out=root / ".skill-beta" / "reports" / "round-1.json",
            )

            self.assertTrue(summary_result["ok"])
            self.assertTrue(Path(summary_result["summary_json"]).exists())
            self.assertTrue(Path(summary_result["feedback_ledger_out"]).exists())
            self.assertTrue(Path(summary_result["round_report_out"]).exists())
            self.assertIn("by_persona", summary_result["blocker_breakdown"])
            round_report_payload = json.loads(Path(summary_result["round_report_out"]).read_text(encoding="utf-8"))
            response_contract.validate_beta_round_report(round_report_payload)
            self.assertEqual("round-1", round_report_payload["round_id"])
            self.assertIn("blocker_breakdown", round_report_payload)
            self.assertIn("evidence_artifacts", round_report_payload)
            self.assertTrue(round_report_payload["evidence_artifacts"]["fixture_manifest_json"])
            self.assertTrue(round_report_payload["evidence_artifacts"]["fixture_diff_json"])
            self.assertTrue(round_report_payload["evidence_artifacts"]["cohort_plan_json"])
            self.assertTrue(round_report_payload["evidence_artifacts"]["ramp_plan_json"])
            ledger_markdown = Path(summary_result["feedback_ledger_out"]).read_text(encoding="utf-8")
            self.assertIn("## Generated Entries", ledger_markdown)
            self.assertIn("| round-1 |", ledger_markdown)

    def test_evaluate_beta_round_emits_advance_decision(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            manifest_path = write_beta_manifest(
                root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                sessions=[
                    {
                        "session_id": "session-01",
                        "persona_id": "first-time-novice",
                        "persona_name": "First-Time Novice",
                        "scenario_id": "scenario-1",
                        "scenario_title": "first meaningful task",
                        "trace_id": "novice-cta-hesitation",
                        "trace_label": "Novice CTA hesitation",
                    },
                    {
                        "session_id": "session-02",
                        "persona_id": "daily-operator",
                        "persona_name": "Daily Operator",
                        "scenario_id": "scenario-2",
                        "scenario_title": "resume a daily workflow",
                        "trace_id": "operator-reentry-friction",
                        "trace_label": "Operator re-entry friction",
                    },
                    {
                        "session_id": "session-03",
                        "persona_id": "goal-driven-power-user",
                        "persona_name": "Goal-Driven Power User",
                        "scenario_id": "scenario-2",
                        "scenario_title": "resume a daily workflow",
                        "trace_id": "power-user-fast-path-friction",
                        "trace_label": "Power-user fast-path friction",
                    },
                    {
                        "session_id": "session-04",
                        "persona_id": "edge-case-breaker",
                        "persona_name": "Edge-Case Breaker",
                        "scenario_id": "scenario-3",
                        "scenario_title": "recover from a rough edge",
                        "trace_id": "edge-recovery-break",
                        "trace_label": "Edge recovery break",
                    },
                    {
                        "session_id": "session-05",
                        "persona_id": "edge-case-breaker",
                        "persona_name": "Edge-Case Breaker",
                        "scenario_id": "scenario-3",
                        "scenario_title": "recover from a rough edge",
                        "trace_id": "edge-recovery-break",
                        "trace_label": "Edge recovery break",
                    },
                ],
            )
            cohort_plan_path = write_beta_cohort_plan(
                root,
                rounds=[
                    {
                        "round_id": "round-1",
                        "fixture_id": "round-1-expanded",
                        "planned_sessions": 5,
                        "persona_targets": [
                            {"persona_id": "daily-operator", "session_count": 1},
                            {"persona_id": "edge-case-breaker", "session_count": 2},
                            {"persona_id": "first-time-novice", "session_count": 1},
                            {"persona_id": "goal-driven-power-user", "session_count": 1},
                        ],
                        "required_scenario_ids": ["scenario-1", "scenario-2", "scenario-3"],
                        "required_trace_ids": [
                            "edge-recovery-break",
                            "novice-cta-hesitation",
                            "operator-reentry-friction",
                            "power-user-fast-path-friction",
                        ],
                    }
                ],
            )
            ramp_plan_path = write_beta_ramp_plan(
                root,
                rounds=[
                    {
                        "round_id": "round-0",
                        "phase": "pre-build concept smoke",
                        "sample_size": 5,
                        "participant_mode": "simulated target users",
                        "archetypes": ["first-time novice"],
                        "goal": "validate the promise",
                        "exit_criteria": "coherent flow",
                    },
                    {
                        "round_id": "round-1",
                        "phase": "closed beta",
                        "sample_size": 12,
                        "participant_mode": "seed users",
                        "archetypes": ["daily operator", "edge-case breaker"],
                        "goal": "validate the implemented slice",
                        "exit_criteria": "no blocker-level failures remain",
                    },
                ],
            )
            diff_path = write_beta_fixture_diff(
                root,
                previous_round_id="round-0",
                current_round_id="round-1",
                previous_session_count=3,
                current_session_count=5,
                previous_persona_count=3,
                current_persona_count=4,
                previous_scenario_count=3,
                current_scenario_count=4,
                previous_trace_count=3,
                current_trace_count=4,
            )
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "seed users",
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "task_success_count": 9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
                "exit_criteria": "no blocker-level failures remain",
                "gate_thresholds": {
                    "min_completed_sessions": 8,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "evidence_artifacts": {
                    "simulation_run_json": str(root / ".skill-beta" / "simulation-runs" / "round-1" / "beta-simulation-run.json"),
                    "simulation_run_markdown": str(root / ".skill-beta" / "simulation-runs" / "round-1" / "beta-simulation-run.md"),
                    "simulation_summary_json": str(root / ".skill-beta" / "simulation-runs" / "round-1" / "beta-simulation-summary.json"),
                    "feedback_ledger_markdown": str(root / ".skill-beta" / "feedback-ledger.md"),
                    "fixture_manifest_json": str(manifest_path),
                    "fixture_manifest_markdown": str(manifest_path.with_suffix(".md")),
                    "fixture_diff_json": str(diff_path),
                    "fixture_diff_markdown": str(diff_path.with_suffix(".md")),
                    "cohort_plan_json": str(cohort_plan_path),
                    "ramp_plan_json": str(ramp_plan_path),
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertTrue(result["ok"])
            self.assertEqual("advance", result["decision"])
            self.assertEqual("round-2", result["follow_up"]["next_round_recommended"])
            self.assertEqual("passed", result["cohort_gate"]["status"])
            self.assertEqual("passed", result["ramp_gate"]["status"])
            self.assertEqual("passed", result["diff_gate"]["status"])
            self.assertTrue(Path(result["json_report"]).exists())
            self.assertTrue(Path(result["markdown_report"]).exists())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_emits_escalate_for_critical_issues(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            technical_governance_init.init_technical_governance(root=root, overwrite=False)
            report = root / ".skill-beta" / "reports" / "round-2.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-2",
                "phase": "expanded internal beta",
                "goal": "pressure-test stability",
                "participant_mode": "mixed internal and trusted external users",
                "planned_sample_size": 30,
                "completed_sessions": 24,
                "task_success_count": 20,
                "blocker_issue_count": 1,
                "critical_issue_count": 2,
                "high_severity_issue_count": 3,
                "top_feedback_themes": ["data loss", "session corruption"],
                "exit_criteria": "no new critical failures appear",
                "gate_thresholds": {
                    "min_completed_sessions": 20,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 1,
                    "max_critical_issue_count": 0,
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertFalse(result["ok"])
            self.assertEqual("escalate", result["decision"])
            self.assertTrue(result["follow_up"]["release_governance_recommended"])
            self.assertIsNone(result["follow_up"]["next_round_recommended"])
            self.assertEqual("missing", result["ramp_gate"]["status"])
            self.assertEqual("missing", result["diff_gate"]["status"])
            self.assertEqual("escalated", result["follow_up"]["loop_state"])
            self.assertTrue(Path(result["follow_up"]["brief_json"]).exists())
            brief = json.loads(Path(result["follow_up"]["brief_json"]).read_text(encoding="utf-8"))
            response_contract.validate_beta_remediation_brief(brief)
            self.assertEqual("escalate", brief["decision"])
            self.assertEqual("Sentinel Architect (NB)", brief["owner"])
            change_plan = (root / ".skill-governance" / "change-plan.md").read_text(encoding="utf-8")
            self.assertIn("## Beta Gate Escalation Writeback", change_plan)
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_holds_when_ramp_plan_is_missing(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "seed users",
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "task_success_count": 9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
                "exit_criteria": "no blocker-level failures remain",
                "gate_thresholds": {
                    "min_completed_sessions": 8,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertEqual("missing", result["ramp_gate"]["status"])
            self.assertIn("ramp plan", result["reason"].lower())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_holds_when_cohort_plan_is_missing(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            manifest_path = write_beta_manifest(
                root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                sessions=[
                    {
                        "session_id": "session-01",
                        "persona_id": "first-time-novice",
                        "persona_name": "First-Time Novice",
                        "scenario_id": "scenario-1",
                        "scenario_title": "first meaningful task",
                        "trace_id": "novice-cta-hesitation",
                        "trace_label": "Novice CTA hesitation",
                    }
                ],
            )
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "seed users",
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "task_success_count": 9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
                "exit_criteria": "no blocker-level failures remain",
                "gate_thresholds": {
                    "min_completed_sessions": 8,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "evidence_artifacts": {
                    "simulation_run_json": "",
                    "simulation_run_markdown": "",
                    "simulation_summary_json": "",
                    "feedback_ledger_markdown": "",
                    "fixture_manifest_json": str(manifest_path),
                    "fixture_manifest_markdown": str(manifest_path.with_suffix(".md")),
                    "fixture_diff_json": "",
                    "fixture_diff_markdown": "",
                    "cohort_plan_json": "",
                    "ramp_plan_json": "",
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertEqual("missing", result["cohort_gate"]["status"])
            self.assertIn("cohort plan", result["reason"].lower())
            self.assertEqual("reopened", result["follow_up"]["loop_state"])
            self.assertTrue(Path(result["follow_up"]["brief_json"]).exists())
            brief = json.loads(Path(result["follow_up"]["brief_json"]).read_text(encoding="utf-8"))
            response_contract.validate_beta_remediation_brief(brief)
            self.assertEqual("hold", brief["decision"])
            self.assertTrue(any("cohort plan" in item["label"].lower() for item in brief["blockers"]))
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_holds_when_cohort_plan_mismatches_manifest(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            manifest_path = write_beta_manifest(
                root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                sessions=[
                    {
                        "session_id": "session-01",
                        "persona_id": "first-time-novice",
                        "persona_name": "First-Time Novice",
                        "scenario_id": "scenario-1",
                        "scenario_title": "first meaningful task",
                        "trace_id": "novice-cta-hesitation",
                        "trace_label": "Novice CTA hesitation",
                    },
                    {
                        "session_id": "session-02",
                        "persona_id": "daily-operator",
                        "persona_name": "Daily Operator",
                        "scenario_id": "scenario-2",
                        "scenario_title": "resume a daily workflow",
                        "trace_id": "operator-reentry-friction",
                        "trace_label": "Operator re-entry friction",
                    },
                ],
            )
            cohort_plan_path = write_beta_cohort_plan(
                root,
                rounds=[
                    {
                        "round_id": "round-1",
                        "fixture_id": "round-1-default",
                        "planned_sessions": 3,
                        "persona_targets": [
                            {"persona_id": "first-time-novice", "session_count": 1},
                            {"persona_id": "daily-operator", "session_count": 1},
                            {"persona_id": "goal-driven-power-user", "session_count": 1},
                        ],
                        "required_scenario_ids": ["scenario-1", "scenario-2", "scenario-3"],
                        "required_trace_ids": [
                            "novice-cta-hesitation",
                            "operator-reentry-friction",
                            "power-user-fast-path-friction",
                        ],
                    }
                ],
            )
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "seed users",
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "task_success_count": 9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
                "exit_criteria": "no blocker-level failures remain",
                "gate_thresholds": {
                    "min_completed_sessions": 8,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "evidence_artifacts": {
                    "simulation_run_json": "",
                    "simulation_run_markdown": "",
                    "simulation_summary_json": "",
                    "feedback_ledger_markdown": "",
                    "fixture_manifest_json": str(manifest_path),
                    "fixture_manifest_markdown": str(manifest_path.with_suffix(".md")),
                    "fixture_diff_json": "",
                    "fixture_diff_markdown": "",
                    "cohort_plan_json": str(cohort_plan_path),
                    "ramp_plan_json": "",
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertEqual("mismatch", result["cohort_gate"]["status"])
            self.assertIn("persona counts", result["reason"].lower())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_holds_when_ramp_plan_mismatches_round_report(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            ramp_plan_path = root / ".skill-beta" / "ramp-plan.json"
            ramp_plan_path.parent.mkdir(parents=True, exist_ok=True)
            ramp_plan_payload = {
                "schema_version": "beta-ramp-plan/v1",
                "skill_name": "virtual-intelligent-dev-team",
                "rounds": [
                    {
                        "round_id": "round-1",
                        "phase": "closed beta",
                        "sample_size": 20,
                        "participant_mode": "seed users",
                        "archetypes": ["daily operator"],
                        "goal": "validate the implemented slice",
                        "exit_criteria": "no blocker-level failures remain",
                    }
                ],
            }
            ramp_plan_path.write_text(json.dumps(ramp_plan_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "seed users",
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "task_success_count": 9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
                "exit_criteria": "no blocker-level failures remain",
                "gate_thresholds": {
                    "min_completed_sessions": 8,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "evidence_artifacts": {
                    "simulation_run_json": "",
                    "simulation_run_markdown": "",
                    "simulation_summary_json": "",
                    "feedback_ledger_markdown": "",
                    "fixture_manifest_json": "",
                    "fixture_manifest_markdown": "",
                    "fixture_diff_json": "",
                    "fixture_diff_markdown": "",
                    "ramp_plan_json": str(ramp_plan_path),
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertEqual("mismatch", result["ramp_gate"]["status"])
            self.assertIn("sample size", result["reason"].lower())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_holds_when_fixture_diff_is_missing(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            ramp_plan_path = root / ".skill-beta" / "ramp-plan.json"
            ramp_plan_path.parent.mkdir(parents=True, exist_ok=True)
            ramp_plan_payload = {
                "schema_version": "beta-ramp-plan/v1",
                "skill_name": "virtual-intelligent-dev-team",
                "rounds": [
                    {
                        "round_id": "round-1",
                        "phase": "closed beta",
                        "sample_size": 12,
                        "participant_mode": "seed users",
                        "archetypes": ["daily operator"],
                        "goal": "validate the implemented slice",
                        "exit_criteria": "no blocker-level failures remain",
                    }
                ],
            }
            ramp_plan_path.write_text(json.dumps(ramp_plan_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "seed users",
                "planned_sample_size": 12,
                "completed_sessions": 10,
                "task_success_count": 9,
                "blocker_issue_count": 0,
                "critical_issue_count": 0,
                "high_severity_issue_count": 1,
                "top_feedback_themes": ["copy clarity"],
                "exit_criteria": "no blocker-level failures remain",
                "gate_thresholds": {
                    "min_completed_sessions": 8,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "evidence_artifacts": {
                    "simulation_run_json": "",
                    "simulation_run_markdown": "",
                    "simulation_summary_json": "",
                    "feedback_ledger_markdown": "",
                    "fixture_manifest_json": "",
                    "fixture_manifest_markdown": "",
                    "fixture_diff_json": "",
                    "fixture_diff_markdown": "",
                    "ramp_plan_json": str(ramp_plan_path),
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertFalse(result["ok"])
            self.assertEqual("hold", result["decision"])
            self.assertEqual("missing", result["diff_gate"]["status"])
            self.assertIn("fixture diff", result["reason"].lower())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_preserves_blocker_breakdown(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            product_delivery_init.init_product_delivery(root=root, overwrite=False)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            manifest_path = write_beta_manifest(
                root,
                round_id="round-1",
                phase="closed beta",
                objective="validate the implemented slice",
                sessions=[
                    {
                        "session_id": "session-01",
                        "persona_id": "first-time-novice",
                        "persona_name": "First-Time Novice",
                        "scenario_id": "scenario-1",
                        "scenario_title": "first meaningful task",
                        "trace_id": "novice-cta-hesitation",
                        "trace_label": "Novice CTA hesitation",
                    },
                    {
                        "session_id": "session-02",
                        "persona_id": "daily-operator",
                        "persona_name": "Daily Operator",
                        "scenario_id": "scenario-2",
                        "scenario_title": "resume a daily workflow",
                        "trace_id": "operator-reentry-friction",
                        "trace_label": "Operator re-entry friction",
                    },
                    {
                        "session_id": "session-03",
                        "persona_id": "goal-driven-power-user",
                        "persona_name": "Goal-Driven Power User",
                        "scenario_id": "scenario-2",
                        "scenario_title": "resume a daily workflow",
                        "trace_id": "power-user-fast-path-friction",
                        "trace_label": "Power-user fast-path friction",
                    },
                    {
                        "session_id": "session-04",
                        "persona_id": "edge-case-breaker",
                        "persona_name": "Edge-Case Breaker",
                        "scenario_id": "scenario-3",
                        "scenario_title": "recover from a rough edge",
                        "trace_id": "edge-recovery-break",
                        "trace_label": "Edge recovery break",
                    },
                    {
                        "session_id": "session-05",
                        "persona_id": "edge-case-breaker",
                        "persona_name": "Edge-Case Breaker",
                        "scenario_id": "scenario-3",
                        "scenario_title": "recover from a rough edge",
                        "trace_id": "edge-recovery-break",
                        "trace_label": "Edge recovery break",
                    },
                    {
                        "session_id": "session-06",
                        "persona_id": "daily-operator",
                        "persona_name": "Daily Operator",
                        "scenario_id": "scenario-2",
                        "scenario_title": "resume a daily workflow",
                        "trace_id": "operator-reentry-friction",
                        "trace_label": "Operator re-entry friction",
                    },
                ],
            )
            cohort_plan_path = write_beta_cohort_plan(
                root,
                rounds=[
                    {
                        "round_id": "round-1",
                        "fixture_id": "round-1-expanded",
                        "planned_sessions": 6,
                        "persona_targets": [
                            {"persona_id": "daily-operator", "session_count": 2},
                            {"persona_id": "edge-case-breaker", "session_count": 2},
                            {"persona_id": "first-time-novice", "session_count": 1},
                            {"persona_id": "goal-driven-power-user", "session_count": 1},
                        ],
                        "required_scenario_ids": ["scenario-1", "scenario-2", "scenario-3"],
                        "required_trace_ids": [
                            "edge-recovery-break",
                            "novice-cta-hesitation",
                            "operator-reentry-friction",
                            "power-user-fast-path-friction",
                        ],
                    }
                ],
            )
            ramp_plan_path = write_beta_ramp_plan(
                root,
                rounds=[
                    {
                        "round_id": "round-1",
                        "phase": "closed beta",
                        "sample_size": 6,
                        "participant_mode": "simulated users",
                        "archetypes": ["edge-case breaker"],
                        "goal": "validate the implemented slice",
                        "exit_criteria": "blocker paths are closed",
                    }
                ],
            )
            diff_path = write_beta_fixture_diff(
                root,
                previous_round_id="round-0",
                current_round_id="round-1",
                previous_session_count=4,
                current_session_count=6,
                previous_persona_count=3,
                current_persona_count=4,
                previous_scenario_count=3,
                current_scenario_count=4,
                previous_trace_count=3,
                current_trace_count=4,
            )
            payload = {
                "schema_version": "beta-round-report/v1",
                "round_id": "round-1",
                "phase": "closed beta",
                "goal": "validate the implemented slice",
                "participant_mode": "simulated users",
                "planned_sample_size": 6,
                "completed_sessions": 6,
                "task_success_count": 4,
                "blocker_issue_count": 1,
                "critical_issue_count": 0,
                "high_severity_issue_count": 2,
                "top_feedback_themes": ["edge-case handling", "efficiency friction"],
                "exit_criteria": "blocker paths are closed",
                "gate_thresholds": {
                    "min_completed_sessions": 5,
                    "min_success_rate": 0.8,
                    "max_blocker_issue_count": 0,
                    "max_critical_issue_count": 0,
                },
                "source_simulation_run": ".skill-beta/simulation-runs/round-1/beta-simulation-run.json",
                "evidence_artifacts": {
                    "simulation_run_json": str(root / ".skill-beta" / "simulation-runs" / "round-1" / "beta-simulation-run.json"),
                    "simulation_run_markdown": str(root / ".skill-beta" / "simulation-runs" / "round-1" / "beta-simulation-run.md"),
                    "simulation_summary_json": str(root / ".skill-beta" / "simulation-runs" / "round-1" / "beta-simulation-summary.json"),
                    "feedback_ledger_markdown": str(root / ".skill-beta" / "feedback-ledger.md"),
                    "fixture_manifest_json": str(manifest_path),
                    "fixture_manifest_markdown": str(manifest_path.with_suffix(".md")),
                    "fixture_diff_json": str(diff_path),
                    "fixture_diff_markdown": str(diff_path.with_suffix(".md")),
                    "cohort_plan_json": str(cohort_plan_path),
                    "ramp_plan_json": str(ramp_plan_path)
                },
                "blocker_breakdown": {
                    "by_persona": [
                        {
                            "label": "Edge-Case Breaker",
                            "session_count": 2,
                            "blocker_issue_count": 1,
                            "critical_issue_count": 0,
                            "high_severity_issue_count": 1,
                            "session_ids": ["session-01", "session-05"],
                            "top_feedback_themes": ["edge-case handling"]
                        }
                    ],
                    "by_scenario": [
                        {
                            "label": "recover from a rough edge",
                            "session_count": 2,
                            "blocker_issue_count": 1,
                            "critical_issue_count": 0,
                            "high_severity_issue_count": 1,
                            "session_ids": ["session-05", "session-06"],
                            "top_feedback_themes": ["edge-case handling", "efficiency friction"]
                        }
                    ]
                },
                "notes": "Derived from simulation evidence."
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertEqual("hold", result["decision"])
            self.assertIn("blocker_breakdown", result)
            self.assertEqual("passed", result["cohort_gate"]["status"])
            self.assertEqual("passed", result["ramp_gate"]["status"])
            self.assertEqual("passed", result["diff_gate"]["status"])
            self.assertEqual("Edge-Case Breaker", result["blocker_breakdown"]["by_persona"][0]["label"])
            self.assertTrue(Path(result["follow_up"]["brief_json"]).exists())
            brief = json.loads(Path(result["follow_up"]["brief_json"]).read_text(encoding="utf-8"))
            response_contract.validate_beta_remediation_brief(brief)
            self.assertIn("blocker_breakdown", brief)
            self.assertEqual("Edge-Case Breaker", brief["blocker_breakdown"]["by_persona"][0]["label"])
            current_slice = (root / ".skill-product" / "current-slice.md").read_text(encoding="utf-8")
            acceptance = (root / ".skill-product" / "acceptance-criteria.md").read_text(encoding="utf-8")
            contract_questions = (root / ".skill-product" / "contract-questions.md").read_text(encoding="utf-8")
            self.assertIn("## Beta Gate Writeback", current_slice)
            self.assertIn("## Beta Gate Writeback", acceptance)
            self.assertIn("## Beta Gate Writeback", contract_questions)
            markdown = Path(result["markdown_report"]).read_text(encoding="utf-8")
            self.assertIn("## Cohort Plan Gate", markdown)
            self.assertIn("## Ramp Plan Gate", markdown)
            self.assertIn("## Fixture Diff Gate", markdown)
            self.assertIn("## Blocker Breakdown By Persona", markdown)
            self.assertIn("## Blocker Breakdown By Scenario", markdown)
            brief_markdown = Path(result["follow_up"]["brief_markdown"]).read_text(encoding="utf-8")
            self.assertIn("## Blocker Breakdown By Persona", brief_markdown)
            self.assertIn("## Recommended Commands", brief_markdown)
            self.assertTrue(any(item.endswith("product-writeback.md") for item in result["follow_up"]["resume_artifacts"]))

    def test_init_technical_governance_creates_expected_anchors(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = technical_governance_init.init_technical_governance(
                root=root, overwrite=False
            )

            self.assertTrue(result["ok"])
            self.assertTrue((root / ".skill-governance" / "change-plan.md").exists())
            self.assertTrue((root / ".skill-governance" / "release-checklist.md").exists())
            self.assertEqual(".skill-governance/change-plan.md", result["resume_anchor"])

    def test_init_post_release_feedback_creates_expected_anchors(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = post_release_feedback_init.init_post_release_feedback(root=root, overwrite=False)

            self.assertTrue(result["ok"])
            self.assertTrue((root / ".skill-post-release" / "rollout-summary.md").exists())
            self.assertTrue((root / ".skill-post-release" / "feedback-ledger.md").exists())
            self.assertTrue((root / ".skill-post-release" / "current-signals.json").exists())
            self.assertTrue((root / ".skill-post-release" / "triage-summary.md").exists())
            self.assertTrue(result["resume_anchor"].endswith(".skill-post-release/triage-summary.md"))

    def test_evaluate_post_release_feedback_iterates_and_writes_back_product_assets(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            product_delivery_init.init_product_delivery(root=root, overwrite=False)
            post_release_feedback_init.init_post_release_feedback(root=root, overwrite=False)
            report = root / ".skill-post-release" / "current-signals.json"
            payload = {
                "schema_version": "post-release-feedback-report/v1",
                "generated_at": "2026-04-08T12:00:00Z",
                "release_label": "v4.46.0",
                "observation_window": {
                    "start": "2026-04-08T00:00:00Z",
                    "end": "2026-04-09T00:00:00Z"
                },
                "signal_summary": {
                    "total_feedback_items": 2,
                    "unique_users_affected": 8,
                    "blocker_issue_count": 1,
                    "escalation_issue_count": 0,
                    "telemetry_status": "warning",
                    "adoption_trend": "stable",
                    "satisfaction_trend": "worsening"
                },
                "feedback_items": [
                    {
                        "id": "feedback-001",
                        "source": "support",
                        "severity": "high",
                        "status": "new",
                        "affected_area": "onboarding",
                        "label": "onboarding stalls after first task",
                        "summary": "Users hesitate after account creation.",
                        "recommended_action": "tighten first-task guidance",
                        "evidence_artifacts": [
                            ".skill-post-release/feedback-ledger.md"
                        ]
                    }
                ],
                "report_context": {
                    "feedback_ledger_markdown": ".skill-post-release/feedback-ledger.md",
                    "release_closure_json": "evals/release-gate/release-closure.json",
                    "release_gate_json": "evals/release-gate/release-gate-results.json"
                }
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            result = post_release_feedback_evaluator.evaluate_post_release_feedback(report_path=report)

            response_contract.validate_post_release_feedback_result(result)
            self.assertFalse(result["ok"])
            self.assertEqual("iterate", result["decision"])
            self.assertEqual("bounded-iteration", result["follow_up"]["next_action"])
            self.assertTrue(Path(result["automation_state"]["state_paths"]["primary"]).exists())
            self.assertEqual("post-release-feedback-result", result["automation_state"]["state_kind"])
            self.assertTrue(Path(result["follow_up"]["brief_json"]).exists())
            current_slice = (root / ".skill-product" / "current-slice.md").read_text(encoding="utf-8")
            self.assertIn("## Post-Release Feedback Writeback", current_slice)
            triage = (root / ".skill-post-release" / "triage-summary.md").read_text(encoding="utf-8")
            self.assertIn("Current decision: `iterate`", triage)

    def test_evaluate_post_release_feedback_escalates_and_writes_back_governance_assets(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            technical_governance_init.init_technical_governance(root=root, overwrite=False)
            post_release_feedback_init.init_post_release_feedback(root=root, overwrite=False)
            report = root / ".skill-post-release" / "current-signals.json"
            payload = {
                "schema_version": "post-release-feedback-report/v1",
                "generated_at": "2026-04-08T12:00:00Z",
                "release_label": "v4.46.0",
                "observation_window": {
                    "start": "2026-04-08T00:00:00Z",
                    "end": "2026-04-09T00:00:00Z"
                },
                "signal_summary": {
                    "total_feedback_items": 1,
                    "unique_users_affected": 12,
                    "blocker_issue_count": 1,
                    "escalation_issue_count": 1,
                    "telemetry_status": "critical",
                    "adoption_trend": "worsening",
                    "satisfaction_trend": "worsening"
                },
                "feedback_items": [
                    {
                        "id": "feedback-crit-001",
                        "source": "telemetry",
                        "severity": "critical",
                        "status": "new",
                        "affected_area": "checkout",
                        "label": "critical checkout regression",
                        "summary": "Payment completion drops after the latest release.",
                        "recommended_action": "contain rollout and investigate release path",
                        "evidence_artifacts": [
                            ".skill-post-release/current-signals.json"
                        ]
                    }
                ],
                "report_context": {
                    "feedback_ledger_markdown": ".skill-post-release/feedback-ledger.md",
                    "release_closure_json": "evals/release-gate/release-closure.json",
                    "release_gate_json": "evals/release-gate/release-gate-results.json",
                    "telemetry_snapshot_json": ".skill-post-release/telemetry.json"
                }
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            result = post_release_feedback_evaluator.evaluate_post_release_feedback(report_path=report)

            response_contract.validate_post_release_feedback_result(result)
            self.assertFalse(result["ok"])
            self.assertEqual("escalate", result["decision"])
            self.assertEqual("technical-governance", result["follow_up"]["next_action"])
            change_plan = (root / ".skill-governance" / "change-plan.md").read_text(encoding="utf-8")
            self.assertIn("## Post-Release Feedback Escalation", change_plan)


class AutoWorkflowTests(unittest.TestCase):
    def test_auto_workflow_setup_persists_plan(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            result = auto_workflow.build_setup_plan(
                text="/auto fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )

            self.assertTrue(result["ok"])
            self.assertEqual("setup", result["requested_phase"])
            self.assertEqual("root-cause-remediate", result["workflow_bundle"])
            plan_json = root / ".skill-auto" / "auto-run-plan.json"
            plan_markdown = root / ".skill-auto" / "auto-run-plan.md"
            self.assertTrue(plan_json.exists())
            self.assertTrue(plan_markdown.exists())
            self.assertTrue((root / result["automation_state"]["state_paths"]["primary"]).exists())
            self.assertIn("root-cause-remediate", plan_markdown.read_text(encoding="utf-8"))

    def test_auto_workflow_setup_resume_anchors_previous_run(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            first = auto_workflow.build_setup_plan(
                text="/auto fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )

            resumed = auto_workflow.build_setup_plan(
                text="/auto resume background safe fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )

            self.assertEqual(first["run_id"], resumed["parent_run_id"])
            self.assertEqual("background", resumed["run_style"])
            self.assertEqual("safe", resumed["safety_level"])
            self.assertTrue(resumed["resume_requested"])
            self.assertEqual("state-first", resumed["resume_context"]["resume_strategy"])
            self.assertTrue(resumed["resume_context"]["state_resume_available"])
            self.assertEqual(
                "resume-explicit-go",
                resumed["resume_context"]["state_resume_decision_id"],
            )

    def test_auto_workflow_go_runs_root_cause_bundle(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )
            with mock.patch.object(
                auto_workflow.iteration_loop,
                "run_loop",
                return_value={
                    "status": "completed",
                    "halt_reason": "halted on decision: keep",
                    "summary": str(root / ".skill-iterations" / "loops" / "iteration-plan.auto-summary.json"),
                    "rounds_run": [],
                },
            ) as run_loop_mock:
                result = auto_workflow.run_go(root / ".skill-auto" / "auto-run-plan.json", root)

            self.assertTrue(result["ok"])
            self.assertEqual("root-cause-remediate", result["workflow_bundle"])
            self.assertEqual("halted on decision: keep", result["decision"])
            self.assertTrue((root / ".skill-iterations" / "iteration-plan.auto.json").exists())
            run_loop_mock.assert_called_once()
            self.assertTrue((root / ".skill-auto" / "last-run.json").exists())
            self.assertTrue((root / result["automation_state"]["state_paths"]["primary"]).exists())

    def test_auto_workflow_go_resume_reuses_iteration_state(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto resume go fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )
            (root / ".skill-iterations").mkdir(parents=True, exist_ok=True)
            (root / ".skill-iterations" / "iteration-plan.auto.json").write_text("{}", encoding="utf-8")
            with mock.patch.object(
                auto_workflow.iteration_loop,
                "run_loop",
                return_value={
                    "status": "completed",
                    "halt_reason": "halted on decision: keep",
                    "summary": str(root / ".skill-iterations" / "loops" / "iteration-plan.auto-summary.json"),
                    "rounds_run": [],
                },
            ) as run_loop_mock:
                auto_workflow.run_go(root / ".skill-auto" / "auto-run-plan.json", root)

            self.assertTrue(run_loop_mock.call_args.kwargs["resume"])

    def test_auto_workflow_go_resume_can_execute_state_first_path(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            plan = auto_workflow.build_setup_plan(
                text="/auto resume safe Is this version ready to ship? Run the formal release gate.",
                repo_root=root,
                config=load_config(),
            )
            plan_path = root / ".skill-auto" / "auto-run-plan.json"
            plan["resume_context"]["state_resume_available"] = True
            plan["resume_context"]["state_resume_state_path"] = "evals/release-gate/automation-state.json"
            plan["resume_context"]["state_resume_decision_id"] = "release-hold-reopen-iteration"
            plan["resume_context"]["state_resume_command"] = (
                "python scripts/init_iteration_round.py --workspace .skill-iterations --round-id round-01 "
                '--objective "resume hold brief" --baseline stable --pretty'
            )
            plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            state_first_payload = {
                "ok": True,
                "selected_state_path": "evals/release-gate/automation-state.json",
                "selection_mode": "workflow",
                "recommended_command": plan["resume_context"]["state_resume_command"],
                "command_allowed": True,
                "resume_execution_ledger": {
                    "json": ".skill-auto/resume-executions/resume-exec-test.json",
                    "markdown": ".skill-auto/resume-executions/resume-exec-test.md",
                },
                "decision_card": {
                    "decision_id": "release-hold-reopen-iteration",
                    "decision_label": "Release hold requires bounded remediation",
                    "decision_reason": "state-first remediation should reopen bounded iteration",
                    "resume_strategy": "playbook-follow-through",
                    "recommended_command": plan["resume_context"]["state_resume_command"],
                    "resume_anchor": ".skill-iterations/current-round-memory.md",
                    "playbooks": [
                        "references/release-gate-playbook.md",
                        "references/iteration-protocol.md"
                    ],
                    "blocking_conditions": [
                        "Release blockers remain unresolved until the hold brief evidence is satisfied."
                    ],
                    "handoff_target": "",
                    "follow_up_artifacts": [
                        "evals/release-gate/next-iteration-brief.json"
                    ],
                    "companion_payload_path": "evals/release-gate/release-gate-results.json",
                },
                "execution": {
                    "executed": True,
                    "command": [
                        "python",
                        "scripts/init_iteration_round.py",
                        "--workspace",
                        ".skill-iterations",
                        "--round-id",
                        "round-01",
                        "--objective",
                        "resume hold brief",
                        "--baseline",
                        "stable",
                        "--pretty"
                    ],
                    "returncode": 0,
                    "stdout": "{\"ok\": true}\n",
                    "stderr": "",
                },
            }

            with mock.patch.object(
                auto_workflow.automation_state_resumer,
                "build_resume_payload",
                return_value=state_first_payload,
            ) as resume_mock, mock.patch.object(
                auto_workflow.release_gate,
                "run_release_gate",
            ) as release_gate_mock:
                result = auto_workflow.run_go(plan_path, root)

            self.assertTrue(result["ok"])
            self.assertTrue(result["state_first_resume_used"])
            self.assertEqual("release-hold-reopen-iteration", result["decision"])
            self.assertIn(
                ".skill-auto/resume-executions/resume-exec-test.md",
                result["resume_artifacts"],
            )
            resume_mock.assert_called_once()
            release_gate_mock.assert_not_called()

    def test_auto_workflow_go_runs_release_bundle(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto safe Is this version ready to ship? Run the formal release gate.",
                repo_root=root,
                config=load_config(),
            )
            with mock.patch.object(
                auto_workflow.release_gate,
                "run_release_gate",
                return_value={
                    "ok": False,
                    "decision": "hold",
                    "automation_state": {
                        "schema_version": "automation-state/v1",
                        "state_kind": "release-gate-result",
                        "decision": "hold",
                        "state_paths": {
                            "primary": str(root / "evals" / "release-gate" / "automation-state.json"),
                            "related": [],
                        },
                    },
                    "follow_up": {
                        "resume_anchor": str(root / "evals" / "release-gate" / "release-gate-report.md"),
                        "resume_artifacts": [
                            str(root / "evals" / "release-gate" / "release-gate-report.md"),
                        ],
                        "next_action": "read the hold brief",
                    },
                },
            ) as release_gate_mock:
                result = auto_workflow.run_go(root / ".skill-auto" / "auto-run-plan.json", root)

            self.assertFalse(result["ok"])
            self.assertEqual("ship-hold-remediate", result["workflow_bundle"])
            self.assertEqual("hold", result["decision"])
            release_gate_mock.assert_called_once()
            self.assertFalse(release_gate_mock.call_args.kwargs["auto_run_next_iteration_on_hold"])

    def test_auto_workflow_go_runs_post_release_bundle(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto The release is already live; absorb telemetry and support signals.",
                repo_root=root,
                config=load_config(),
            )
            with mock.patch.object(
                auto_workflow.post_release_feedback,
                "evaluate_post_release_feedback",
                return_value={
                    "ok": True,
                    "decision": "monitor",
                    "automation_state": {
                        "schema_version": "automation-state/v1",
                        "state_kind": "post-release-feedback-result",
                        "decision": "monitor",
                        "state_paths": {
                            "primary": str(root / ".skill-post-release" / "decisions" / "automation-state.json"),
                            "related": [],
                        },
                    },
                    "follow_up": {
                        "resume_artifacts": [str(root / ".skill-post-release" / "triage-summary.md")],
                        "next_action": "continue-monitoring",
                    },
                },
            ) as post_release_mock:
                result = auto_workflow.run_go(root / ".skill-auto" / "auto-run-plan.json", root)

            self.assertTrue(result["ok"])
            self.assertEqual("post-release-close-loop", result["workflow_bundle"])
            self.assertEqual("monitor", result["decision"])
            self.assertTrue((root / ".skill-post-release" / "current-signals.json").exists())
            post_release_mock.assert_called_once()


class AutomationStateInspectorTests(unittest.TestCase):
    def test_inspect_automation_state_reads_latest_auto_setup_and_recommends_go(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto background safe fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )

            result = automation_state_inspector.inspect_automation_state(repo_root=root)

            self.assertTrue(result["ok"])
            self.assertEqual("latest", result["selection_mode"])
            self.assertEqual("auto-run-setup", result["selected_state"]["state_kind"])
            self.assertTrue(result["resume_ready"])
            self.assertIn("run_auto_workflow.py --mode go", result["recommended_resume_command"])
            self.assertEqual("resume-explicit-go", result["decision_card"]["decision_id"])
            self.assertIn(
                "references/auto-run-playbook.md",
                result["decision_card"]["playbooks"],
            )
            self.assertIn(
                "references/root-cause-escalation-playbook.md",
                result["decision_card"]["playbooks"],
            )

    def test_inspect_automation_state_can_filter_release_gate_state(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            output_dir = root / "evals" / "release-gate"

            with mock.patch.object(
                release_gate.benchmark_runner,
                "run_benchmark_suite",
                return_value={
                    "summary": {
                        "tests_passed": True,
                        "validator_passed": True,
                        "evals_passed": True,
                        "offline_drill_enabled": True,
                        "offline_drill_passed": True,
                        "overall_passed": True,
                    },
                    "json_report": str(output_dir / "benchmark-results.json"),
                    "markdown_report": str(output_dir / "benchmark-report.md"),
                    "offline_drill_run": {
                        "markdown_report": str(output_dir / "offline-loop-drill-report.md"),
                    },
                },
            ):
                release_gate.run_release_gate(output_dir=output_dir)

            result = automation_state_inspector.inspect_automation_state(
                repo_root=root,
                workflow="ship-hold-remediate",
            )

            self.assertTrue(result["ok"])
            self.assertEqual("workflow", result["selection_mode"])
            self.assertEqual("release-gate-result", result["selected_state"]["state_kind"])
            self.assertIn("run_release_gate.py", result["recommended_resume_command"])
            self.assertEqual(
                "release-ship-continue-post-release",
                result["decision_card"]["decision_id"],
            )
            self.assertIn(
                "references/post-release-feedback-playbook.md",
                result["decision_card"]["playbooks"],
            )
            self.assertIn(
                "evaluate_post_release_feedback.py",
                result["decision_card"]["recommended_command"],
            )

    def test_inspect_automation_state_routes_post_release_escalation_to_governance(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            technical_governance_init.init_technical_governance(root=root, overwrite=False)
            post_release_feedback_init.init_post_release_feedback(root=root, overwrite=False)
            report = root / ".skill-post-release" / "current-signals.json"
            payload = {
                "schema_version": "post-release-feedback-report/v1",
                "generated_at": "2026-04-08T12:00:00Z",
                "release_label": "v4.49.0",
                "observation_window": {
                    "start": "2026-04-08T00:00:00Z",
                    "end": "2026-04-09T00:00:00Z",
                },
                "signal_summary": {
                    "total_feedback_items": 1,
                    "unique_users_affected": 12,
                    "blocker_issue_count": 1,
                    "escalation_issue_count": 1,
                    "telemetry_status": "critical",
                    "adoption_trend": "worsening",
                    "satisfaction_trend": "worsening",
                },
                "feedback_items": [
                    {
                        "id": "feedback-crit-001",
                        "source": "telemetry",
                        "severity": "critical",
                        "status": "new",
                        "affected_area": "checkout",
                        "label": "critical checkout regression",
                        "summary": "Payment completion drops after the latest release.",
                        "recommended_action": "contain rollout and investigate release path",
                        "evidence_artifacts": [
                            ".skill-post-release/current-signals.json"
                        ],
                    }
                ],
                "report_context": {
                    "feedback_ledger_markdown": ".skill-post-release/feedback-ledger.md",
                    "release_closure_json": "evals/release-gate/release-closure.json",
                    "release_gate_json": "evals/release-gate/release-gate-results.json",
                },
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            post_release_feedback_evaluator.evaluate_post_release_feedback(report_path=report)

            result = automation_state_inspector.inspect_automation_state(
                repo_root=root,
                workflow="post-release-close-loop",
            )

            self.assertEqual("post-release-escalate-governance", result["decision_card"]["decision_id"])
            self.assertIn(
                "references/technical-governance-playbook.md",
                result["decision_card"]["playbooks"],
            )
            self.assertEqual("handoff", result["decision_card"]["resume_strategy"])
            self.assertTrue(
                any(
                    token in result["decision_card"]["recommended_command"]
                    for token in ("init_technical_governance.py", "run_release_gate.py")
                )
            )

    def test_inspect_automation_state_cli_supports_explicit_path(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            setup = auto_workflow.build_setup_plan(
                text="/auto fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )
            state_path = root / str(setup["automation_state"]["state_paths"]["primary"])

            proc = subprocess.run(
                [
                    sys.executable,
                    str(INSPECT_AUTOMATION_STATE_SCRIPT),
                    "--repo",
                    str(root),
                    "--state",
                    str(state_path),
                    "--pretty",
                ],
                cwd=str(root),
                text=True,
                capture_output=True,
                encoding="utf-8",
            )

            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual("path", payload["selection_mode"])
            self.assertEqual("auto-run-setup", payload["selected_state"]["state_kind"])


class AutomationStateResumeTests(unittest.TestCase):
    def test_resume_from_automation_state_dry_run_returns_guarded_command(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto background safe fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )

            result = automation_state_resumer.build_resume_payload(repo_root=root)

            self.assertTrue(result["ok"])
            self.assertTrue(result["dry_run"])
            self.assertFalse(result["execute_requested"])
            self.assertTrue(result["command_allowed"])
            self.assertIn("run_auto_workflow.py --mode go", result["recommended_command"])
            self.assertIn("pass --execute", result["next_action"])

    def test_resume_from_automation_state_execute_runs_recommended_command(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            inspection_payload = {
                "ok": True,
                "selection_mode": "workflow",
                "selected_state_path": ".skill-post-release/decisions/current-signals/automation-state.json",
                "decision_card": {
                    "decision_id": "post-release-escalate-governance",
                    "decision_label": "Escalate shipped feedback into governance",
                    "decision_reason": "state-first governance escalation is required",
                    "resume_strategy": "handoff",
                    "recommended_command": "python scripts/init_technical_governance.py --root . --pretty",
                    "resume_anchor": ".skill-governance/change-plan.md",
                    "playbooks": [
                        "references/post-release-feedback-playbook.md",
                        "references/technical-governance-playbook.md",
                    ],
                    "blocking_conditions": [
                        "Do not continue normal rollout while governance escalation is unresolved."
                    ],
                    "handoff_target": "technical-governance",
                    "follow_up_artifacts": [
                        ".skill-post-release/triage-summary.md"
                    ],
                    "companion_payload_path": ".skill-post-release/decisions/post-release-feedback-result.json",
                },
                "recommended_resume_command": "python scripts/init_technical_governance.py --root . --pretty",
            }

            with mock.patch.object(
                automation_state_resumer.automation_state_inspector,
                "inspect_automation_state",
                return_value=inspection_payload,
            ), mock.patch.object(
                automation_state_resumer.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    args=["python", "scripts/init_technical_governance.py", "--root", ".", "--pretty"],
                    returncode=0,
                    stdout='{"ok": true}\n',
                    stderr="",
                ),
            ) as run_mock:
                result = automation_state_resumer.build_resume_payload(repo_root=root, execute=True)

            self.assertTrue(result["ok"])
            self.assertFalse(result["dry_run"])
            self.assertTrue(result["execution"]["executed"])
            self.assertEqual(0, result["execution"]["returncode"])
            self.assertTrue((root / result["resume_execution_ledger"]["json"]).exists())
            self.assertTrue((root / result["resume_execution_ledger"]["markdown"]).exists())
            ledger_payload = json.loads(
                (root / result["resume_execution_ledger"]["json"]).read_text(encoding="utf-8")
            )
            response_contract.validate_automation_resume_execution(ledger_payload)
            run_mock.assert_called_once()

    def test_resume_from_automation_state_blocks_non_allowlisted_command(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            inspection_payload = {
                "ok": True,
                "selection_mode": "workflow",
                "selected_state_path": ".skill-auto/state/fake.json",
                "decision_card": {
                    "decision_id": "manual-review",
                    "recommended_command": "python scripts/git_workflow_guardrail.py",
                },
                "recommended_resume_command": "python scripts/git_workflow_guardrail.py",
            }

            with mock.patch.object(
                automation_state_resumer.automation_state_inspector,
                "inspect_automation_state",
                return_value=inspection_payload,
            ):
                result = automation_state_resumer.build_resume_payload(repo_root=root)

            self.assertFalse(result["ok"])
            self.assertFalse(result["command_allowed"])
            self.assertIn("allowlist", result["error"])


class ResponsePackTests(unittest.TestCase):
    def test_generate_response_pack_payload_matches_json_schema(self) -> None:
        prompts = [
            "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            "Iterate on the React dashboard UX, benchmark the variants, and keep improving until stable.",
            "这个产品开发前后都要做内测，分三轮递增用户，并模拟不同类型的内测用户来收集反馈。",
        ]

        for prompt in prompts:
            with self.subTest(prompt=prompt):
                result = route_request.route_request(
                    prompt,
                    load_config(),
                    repo_path=REPO_ROOT,
                )
                payload = response_pack.build_response_pack_payload(result)
                response_contract.validate_response_pack_payload(payload)

    def test_generate_response_pack_payload_schema_rejects_missing_resume(self) -> None:
        result = route_request.route_request(
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        payload = response_pack.build_response_pack_payload(result)
        payload.pop("resume", None)

        with self.assertRaisesRegex(ValueError, "resume"):
            response_contract.validate_response_pack_payload(payload)

    def test_generate_response_pack_payload_schema_rejects_unexpected_top_level_field(self) -> None:
        result = route_request.route_request(
            "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        payload = response_pack.build_response_pack_payload(result)
        payload["unexpected_extra"] = True

        with self.assertRaisesRegex(ValueError, "Additional properties are not allowed"):
            response_contract.validate_response_pack_payload(payload)

    def test_generate_response_pack_payload_exposes_structured_sections(self) -> None:
        result = route_request.route_request(
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        payload = response_pack.build_response_pack_payload(result)

        self.assertEqual(response_contract.SIDECAR_SCHEMA_VERSION, payload["schema_version"])
        self.assertEqual("en", payload["language"])
        self.assertEqual("release", payload["template"])
        self.assertEqual("ship-hold-remediate", payload["team_dispatch"]["workflow_bundle"])
        self.assertIn("primary execution journey", payload["evidence"]["workflow_source_explanation"])
        self.assertIn("run the release gate first", payload["next_action"]["smallest_executable_action"])
        self.assertEqual("evals/release-gate/release-gate-report.md", payload["resume"]["progress_anchor"])

    def test_generate_response_pack_payload_includes_bundle_bootstrap_for_product_bundle(self) -> None:
        result = route_request.route_request(
            "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        payload = response_pack.build_response_pack_payload(result)

        self.assertIn("bundle_bootstrap", payload)
        self.assertEqual(
            ".skill-product/current-slice.md",
            payload["bundle_bootstrap"]["resume_anchor"],
        )
        self.assertIn(
            "python scripts/init_product_delivery.py --root . --pretty",
            payload["bundle_bootstrap"]["commands"],
        )

    def test_generate_response_pack_payload_includes_beta_program(self) -> None:
        result = route_request.route_request(
            "这个产品开发前后都要做内测，分三轮递增用户，并模拟不同类型的内测用户来收集反馈。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        payload = response_pack.build_response_pack_payload(result)

        self.assertEqual("beta", payload["template"])
        self.assertIn("beta_program", payload)
        self.assertEqual(".skill-beta/feedback-ledger.md", payload["beta_program"]["feedback_anchor"])
        self.assertEqual("assets/beta-cohort-plan-template.json", payload["beta_program"]["cohort_plan_template"])
        self.assertEqual("references/beta-cohort-plan.schema.json", payload["beta_program"]["cohort_plan_schema"])
        self.assertEqual(".skill-beta/cohort-plan.json", payload["beta_program"]["cohort_plan_path"])
        self.assertEqual("assets/beta-ramp-plan-template.json", payload["beta_program"]["ramp_plan_template"])
        self.assertEqual("references/beta-ramp-plan.schema.json", payload["beta_program"]["ramp_plan_schema"])
        self.assertEqual(".skill-beta/ramp-plan.json", payload["beta_program"]["ramp_plan_path"])
        self.assertEqual("assets/simulated-user-profile-template.json", payload["beta_program"]["simulation_profile_template"])
        self.assertEqual(".skill-beta/personas", payload["beta_program"]["simulation_profile_dir"])
        self.assertEqual("references/simulation-persona-library.json", payload["beta_program"]["simulation_persona_library"])
        self.assertEqual("references/simulation-cohort-fixtures.json", payload["beta_program"]["simulation_cohort_fixtures"])
        self.assertEqual("assets/beta-simulation-config-template.json", payload["beta_program"]["simulation_config_template"])
        self.assertEqual(".skill-beta/simulation-configs", payload["beta_program"]["simulation_config_dir"])
        self.assertEqual("references/simulation-scenario-packs.json", payload["beta_program"]["simulation_scenario_packs"])
        self.assertEqual("references/simulation-trace-catalog.json", payload["beta_program"]["simulation_trace_catalog"])
        self.assertEqual(".skill-beta/fixture-previews", payload["beta_program"]["simulation_preview_dir"])
        self.assertEqual(".skill-beta/fixture-diffs", payload["beta_program"]["simulation_diff_dir"])
        self.assertEqual(".skill-beta/simulation-runs", payload["beta_program"]["simulation_run_dir"])
        self.assertIn("python scripts/init_beta_simulation.py", payload["beta_program"]["simulation_init_command_template"])
        self.assertIn("python scripts/preview_beta_simulation_fixture.py", payload["beta_program"]["simulation_preview_command_template"])
        self.assertIn("python scripts/compare_beta_simulation_manifests.py", payload["beta_program"]["simulation_diff_command_template"])
        self.assertIn("python scripts/run_beta_simulation.py", payload["beta_program"]["simulation_run_command_template"])
        self.assertIn("python scripts/summarize_beta_simulation.py", payload["beta_program"]["simulation_summary_command_template"])
        self.assertEqual("assets/beta-round-report-template.json", payload["beta_program"]["report_template"])
        self.assertEqual(".skill-beta/reports", payload["beta_program"]["report_dir"])
        self.assertEqual(".skill-beta/round-decisions", payload["beta_program"]["decision_dir"])
        self.assertIn("python scripts/evaluate_beta_round.py", payload["beta_program"]["gate_command_template"])
        self.assertEqual(3, len(payload["beta_program"]["rounds"]))

    def test_generate_response_pack_payload_includes_auto_run_section(self) -> None:
        result = route_request.route_request(
            "/auto resume background safe fix this repeated regression until stable and keep benchmark evidence",
            load_config(),
            repo_path=REPO_ROOT,
        )

        payload = response_pack.build_response_pack_payload(result)

        self.assertIn("auto_run", payload)
        self.assertTrue(payload["auto_run"]["enabled"])
        self.assertEqual("setup", payload["auto_run"]["requested_phase"])
        self.assertEqual("auto-setup", payload["auto_run"]["execution_mode"])
        self.assertEqual("background", payload["auto_run"]["run_style"])
        self.assertEqual("safe", payload["auto_run"]["safety_level"])
        self.assertTrue(payload["auto_run"]["resume_requested"])
        self.assertTrue(payload["auto_run"]["detached_ready"])
        self.assertTrue(payload["auto_run"]["workflow_supported"])
        self.assertIn("root-cause-remediate", payload["auto_run"]["eligible_workflows"])
        self.assertEqual(".skill-auto/state", payload["auto_run"]["state_dir"])
        self.assertEqual("references/automation-state.schema.json", payload["auto_run"]["automation_state_schema"])
        self.assertIn("python scripts/run_auto_workflow.py", payload["auto_run"]["setup_command"])

    def test_generate_response_pack_payload_includes_automation_resume_section(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto background safe fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )
            result = route_request.route_request(
                "/auto resume background safe fix this repeated regression until stable and keep benchmark evidence",
                load_config(),
                repo_path=root,
            )

            payload = response_pack.build_response_pack_payload(result)

            self.assertIn("automation_resume", payload)
            self.assertTrue(payload["automation_resume"]["enabled"])
            self.assertTrue(payload["automation_resume"]["state_resume_available"])
            self.assertEqual("resume-explicit-go", payload["automation_resume"]["decision_id"])
            self.assertIn(
                "resume_from_automation_state.py",
                payload["automation_resume"]["dry_run_command"],
            )

    def test_generate_response_pack_cli_writes_json_sidecar_by_default(self) -> None:
        with make_tempdir() as tmp:
            output = Path(tmp) / "response-pack.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(GENERATE_RESPONSE_PACK_SCRIPT),
                    "--text",
                    "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
                    "--repo",
                    str(REPO_ROOT),
                    "--output",
                    str(output),
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                encoding="utf-8",
            )

            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertTrue(output.exists())
            sidecar = output.with_suffix(".json")
            written = json.loads(sidecar.read_text(encoding="utf-8"))
            response_contract.validate_response_pack_payload(written)
            self.assertEqual(response_contract.SIDECAR_SCHEMA_VERSION, written["schema_version"])
            self.assertEqual("planning", written["template"])
            self.assertEqual("docs/progress/MASTER.md", written["resume"]["progress_anchor"])

    def test_generate_response_pack_renders_bundle_and_anchor(self) -> None:
        result = route_request.route_request(
            "Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## Team Dispatch", markdown)
        self.assertIn("Workflow bundle: plan-first-build", markdown)
        self.assertIn("Bundle confidence: 0.96 (process-skill)", markdown)
        self.assertIn("Workflow source explanation: This bundle is activated by an explicit process skill, so it should be treated as the primary execution journey.", markdown)
        self.assertIn("## Evidence", markdown)
        self.assertIn("## Next Action", markdown)
        self.assertIn("## Resume", markdown)
        self.assertIn("Smallest executable action: lock transformation scope, target, and constraints", markdown)
        self.assertIn("Progress anchor: docs/progress/MASTER.md", markdown)
        self.assertIn("## Planning Pack", markdown)

    def test_generate_response_pack_renders_product_bundle_bootstrap(self) -> None:
        result = route_request.route_request(
            "Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## Bundle Bootstrap", markdown)
        self.assertIn("python scripts/init_product_delivery.py --root . --pretty", markdown)
        self.assertIn(".skill-product/current-slice.md", markdown)

    def test_generate_response_pack_renders_beta_program(self) -> None:
        result = route_request.route_request(
            "这个产品开发前后都要做内测，分三轮递增用户，并模拟不同类型的内测用户来收集反馈。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## 内测计划", markdown)
        self.assertIn("round-0 | pre-build concept smoke | 样本 5", markdown)
        self.assertIn(".skill-beta/cohort-matrix.md", markdown)
        self.assertIn(".skill-beta/feedback-ledger.md", markdown)
        self.assertIn("assets/beta-cohort-plan-template.json", markdown)
        self.assertIn("references/beta-cohort-plan.schema.json", markdown)
        self.assertIn(".skill-beta/cohort-plan.json", markdown)
        self.assertIn("assets/beta-ramp-plan-template.json", markdown)
        self.assertIn("references/beta-ramp-plan.schema.json", markdown)
        self.assertIn(".skill-beta/ramp-plan.json", markdown)
        self.assertIn("assets/simulated-user-profile-template.json", markdown)
        self.assertIn(".skill-beta/personas", markdown)
        self.assertIn("references/simulation-persona-library.json", markdown)
        self.assertIn("references/simulation-cohort-fixtures.json", markdown)
        self.assertIn("assets/beta-simulation-config-template.json", markdown)
        self.assertIn(".skill-beta/simulation-configs", markdown)
        self.assertIn("references/simulation-scenario-packs.json", markdown)
        self.assertIn("references/simulation-trace-catalog.json", markdown)
        self.assertIn(".skill-beta/fixture-previews", markdown)
        self.assertIn(".skill-beta/fixture-diffs", markdown)
        self.assertIn("python scripts/init_beta_simulation.py", markdown)
        self.assertIn("python scripts/preview_beta_simulation_fixture.py", markdown)
        self.assertIn("python scripts/compare_beta_simulation_manifests.py", markdown)
        self.assertIn("python scripts/run_beta_simulation.py", markdown)
        self.assertIn("python scripts/summarize_beta_simulation.py", markdown)
        self.assertIn("assets/beta-round-report-template.json", markdown)
        self.assertIn("python scripts/evaluate_beta_round.py --report .skill-beta/reports/<round-id>.json --pretty", markdown)

    def test_generate_response_pack_renders_automation_resume_section(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            auto_workflow.build_setup_plan(
                text="/auto background safe fix this repeated regression until stable and keep benchmark evidence",
                repo_root=root,
                config=load_config(),
            )
            result = route_request.route_request(
                "/auto resume background safe fix this repeated regression until stable and keep benchmark evidence",
                load_config(),
                repo_path=root,
            )

            markdown = response_pack.build_response_pack(result)

            self.assertIn("## Automation Resume", markdown)
            self.assertIn("resume-explicit-go", markdown)
            self.assertIn("resume_from_automation_state.py", markdown)

    def test_generate_response_pack_auto_uses_chinese_scaffold(self) -> None:
        result = route_request.route_request(
            "这个核心模块要大规模迁移，先调研再执行，先规划再开发。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## 团队派工", markdown)
        self.assertIn("主责智能体：Sentinel Architect (NB)", markdown)
        self.assertIn("bundle 置信度：0.96（来源：process-skill）", markdown)
        self.assertIn("路由原因：当前请求属于重写、迁移或先规划后开发，应先产出 planning pack 和持久化进度锚点。", markdown)
        self.assertIn("工作流来源解释：这条 bundle 由显式 process skill 激活，应视为当前任务的主执行旅程。", markdown)
        self.assertIn("## 证据与约束", markdown)
        self.assertIn("## 下一动作", markdown)
        self.assertIn("## 恢复信息", markdown)
        self.assertIn("最小可执行动作：先锁定改造范围、目标和约束", markdown)
        self.assertIn("## 规划包", markdown)

    def test_generate_response_pack_release_template(self) -> None:
        result = route_request.route_request(
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result, template="release")

        self.assertIn("run the formal release gate", markdown)
        self.assertIn("## Governance", markdown)

    def test_generate_response_pack_review_template(self) -> None:
        result = route_request.route_request(
            "This is a PR. Please do a security review and give refactor advice.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result, template="review")

        self.assertIn("review-first path", markdown)
        self.assertIn("Workflow bundle: audit-fix-deliver", markdown)
        self.assertIn("Workflow source explanation: This bundle is activated by both the selected lead and matching request keywords, so the journey is strongly anchored in task semantics.", markdown)

    def test_generate_response_pack_auto_uses_english_release_scaffold(self) -> None:
        result = route_request.route_request(
            "Is this version ready to ship? Do not answer from benchmark alone. Run the formal release gate.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## Team Dispatch", markdown)
        self.assertIn("Workflow bundle: ship-hold-remediate", markdown)
        self.assertIn("Why this route: Formal release readiness or acceptance is central, so release gate drives the journey.", markdown)
        self.assertIn("Workflow source explanation: This bundle is activated by an explicit process skill, so it should be treated as the primary execution journey.", markdown)
        self.assertIn("## Evidence", markdown)
        self.assertIn("Key conclusion: run the formal release gate before making a ship decision.", markdown)
        self.assertIn("Smallest executable action: run the release gate first", markdown)

    def test_generate_response_pack_auto_uses_english_iteration_scaffold(self) -> None:
        result = route_request.route_request(
            "Run another iteration, benchmark it against the baseline, and stop if the result regresses.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## Team Dispatch", markdown)
        self.assertIn("Workflow bundle: root-cause-remediate", markdown)
        self.assertIn("Workflow source explanation: This bundle is activated by an explicit process skill, so it should be treated as the primary execution journey.", markdown)
        self.assertIn("## Resume", markdown)
        self.assertIn("Key conclusion: stay inside the bounded loop and change only one variable per round.", markdown)
        self.assertIn("Smallest executable action: freeze guesswork and summarize what is already known", markdown)
        self.assertIn("## Optimization Loop", markdown)

    def test_generate_response_pack_auto_uses_chinese_review_scaffold(self) -> None:
        result = route_request.route_request(
            "请 review 这个 Java GC 问题并给出建议",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## 团队派工", markdown)
        self.assertIn("主责智能体：Code Audit Council", markdown)
        self.assertIn("协作智能体：Java Virtuoso", markdown)
        self.assertIn("路由原因：当前请求以审计或 review 为主，应先给出 findings，再决定修复与交付。", markdown)
        self.assertIn("工作流来源解释：这条 bundle 同时由主责和请求关键词触发，因此和任务语义强绑定。", markdown)
        self.assertIn("最小可执行动作：先给出 findings", markdown)

    def test_generate_response_pack_renders_auto_run_section(self) -> None:
        result = route_request.route_request(
            "/auto background The release is already live; absorb telemetry and support signals.",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## Auto Run", markdown)
        self.assertIn("Current bundle: post-release-close-loop", markdown)
        self.assertIn("Run style: background / safety level: standard", markdown)
        self.assertIn("Eligible workflows:", markdown)
        self.assertIn("State schema: references/automation-state.schema.json", markdown)
        self.assertIn("python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty", markdown)

    def test_generate_response_pack_auto_uses_chinese_release_scaffold(self) -> None:
        result = route_request.route_request(
            "这版现在能不能提交/发版？不要只看 benchmark，通过正式 release gate 做提交前验收。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## 团队派工", markdown)
        self.assertIn("工作流 bundle：ship-hold-remediate", markdown)
        self.assertIn("路由原因：当前请求明确以正式发布判断或验收为中心，应先走 release gate。", markdown)
        self.assertIn("工作流来源解释：这条 bundle 由显式 process skill 激活，应视为当前任务的主执行旅程。", markdown)
        self.assertIn("关键结论：先跑正式 release gate，再决定 ship 还是 hold。", markdown)
        self.assertIn("最小可执行动作：先运行正式 release gate", markdown)

    def test_generate_response_pack_auto_uses_chinese_iteration_scaffold(self) -> None:
        result = route_request.route_request(
            "继续优化这个 React dashboard UX，跑 benchmark，对比上一轮，直到稳定。",
            load_config(),
            repo_path=REPO_ROOT,
        )

        markdown = response_pack.build_response_pack(result)

        self.assertIn("## 团队派工", markdown)
        self.assertIn("主责智能体：World-Class Product Architect", markdown)
        self.assertIn("工作流 bundle：root-cause-remediate", markdown)
        self.assertIn("路由原因：当前请求需要基于证据做诊断或有边界迭代，应保留验证证据与回滚决策。", markdown)
        self.assertIn("工作流来源解释：这条 bundle 由显式 process skill 激活，应视为当前任务的主执行旅程。", markdown)
        self.assertIn("最小可执行动作：先冻结猜测并总结当前已知信息", markdown)
        self.assertIn("## 优化闭环", markdown)

    def test_verify_action_workflow_bundle_includes_source_explanation(self) -> None:
        result = verify_action.verify_action(
            text="Rewrite this project in Rust, but plan before coding and keep a progress tracker for later sessions.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="workflow-bundle",
        )

        self.assertTrue(result["allowed"])
        self.assertEqual("process-skill", result["details"]["workflow_bundle_source"])
        self.assertIn("primary execution journey", result["details"]["workflow_bundle_source_explanation"])
        self.assertEqual("process-skill", result["router_snapshot"]["workflow_bundle_source"])

    def test_verify_action_workflow_bundle_exposes_product_bootstrap(self) -> None:
        result = verify_action.verify_action(
            text="Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="workflow-bundle",
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["details"]["bundle_bootstrap"]["required"])
        self.assertIn(
            "python scripts/init_product_delivery.py --root . --pretty",
            result["details"]["bundle_bootstrap"]["commands"],
        )
        self.assertIn(
            "python scripts/init_product_delivery.py --root . --pretty",
            result["explanation_card"]["bundle_bootstrap_commands"],
        )
        self.assertEqual(
            ".skill-product/current-slice.md",
            result["router_snapshot"]["workflow_bundle_bootstrap"]["resume_anchor"],
        )

    def test_verify_action_bundle_bootstrap_requires_product_init_contract(self) -> None:
        result = verify_action.verify_action(
            text="Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="bundle-bootstrap",
        )

        self.assertTrue(result["allowed"])
        self.assertTrue(result["details"]["bootstrap_required"])
        self.assertTrue(result["details"]["progress_anchor_matches_resume_anchor"])
        self.assertEqual([], result["details"]["missing_contract_fields"])
        self.assertTrue(result["details"]["resume_anchor_in_artifacts"])
        self.assertTrue(result["details"]["resume_anchor_in_resume_artifacts"])
        self.assertEqual("missing", result["details"]["workspace_state"])
        self.assertFalse(result["details"]["workspace_ready"])
        self.assertTrue(result["details"]["bootstrap_command_required_now"])
        self.assertIn(
            ".skill-product/current-slice.md",
            result["details"]["missing_artifacts_on_disk"],
        )
        self.assertFalse(result["details"]["resume_anchor_exists"])
        self.assertEqual(
            ".skill-product/current-slice.md",
            result["details"]["bootstrap"]["resume_anchor"],
        )

    def test_verify_action_assistant_delta_contract(self) -> None:
        result = verify_action.verify_action(
            text="Define the onboarding user flow, acceptance criteria, and backend contract for this signup revamp.",
            config=load_config(),
            repo_path=REPO_ROOT,
            check="assistant-delta-contract",
        )

        self.assertTrue(result["allowed"])
        details = result["details"]["assistant_delta_contract"]
        self.assertTrue(details["enabled"])
        self.assertIn("Technical Trinity", details["assistants"])
        self.assertIn("claim", details["required_fields"])
        self.assertIn("Technical Trinity", details["by_agent"])
        self.assertEqual([], result["details"]["special_field_failures"])


if __name__ == "__main__":
    unittest.main()
