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
    fixture_path = output_dir / "beta-round-gate-result.json"
    fixture_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "beta-round-gate-report.md").write_text("# Beta Gate\n", encoding="utf-8")
    response_contract.validate_beta_round_gate_result(payload)
    return fixture_path


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

            self.assertTrue(master_path.exists())
            self.assertTrue(overview_path.exists())
            self.assertTrue(phase_path.exists())
            self.assertIn("Rust Rewrite", master_path.read_text(encoding="utf-8"))
            self.assertIn("Rewrite the monolith into a Rust service stack.", overview_path.read_text(encoding="utf-8"))
            self.assertIn("Phase 1: Foundation", phase_path.read_text(encoding="utf-8"))

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
            ledger_markdown = Path(summary_result["feedback_ledger_out"]).read_text(encoding="utf-8")
            self.assertIn("## Generated Entries", ledger_markdown)
            self.assertIn("| round-1 |", ledger_markdown)

    def test_evaluate_beta_round_emits_advance_decision(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            diff_dir = root / ".skill-beta" / "fixture-diffs" / "round-0-to-round-1"
            diff_dir.mkdir(parents=True, exist_ok=True)
            diff_payload = {
                "schema_version": "beta-simulation-diff/v1",
                "generated_at": "2026-04-08T12:00:00Z",
                "skill_name": "virtual-intelligent-dev-team",
                "previous_round_id": "round-0",
                "current_round_id": "round-1",
                "previous_manifest_path": str(root / ".skill-beta" / "fixture-previews" / "round-0" / "beta-simulation-manifest.json"),
                "current_manifest_path": str(root / ".skill-beta" / "fixture-previews" / "round-1" / "beta-simulation-manifest.json"),
                "previous_session_count": 3,
                "current_session_count": 5,
                "session_count_delta": 2,
                "added_personas": [],
                "removed_personas": [],
                "added_scenarios": [],
                "removed_scenarios": [],
                "added_traces": [],
                "removed_traces": [],
                "new_session_matrix": [],
                "coverage_shift_summary": {
                    "previous_persona_count": 3,
                    "current_persona_count": 4,
                    "previous_scenario_count": 3,
                    "current_scenario_count": 4,
                    "previous_trace_count": 3,
                    "current_trace_count": 4,
                    "new_session_matrix_count": 0,
                    "expansion_mode": "expanded",
                },
                "risk_notes": ["Coverage expanded while preserving the previous baseline."],
                "expansion_ok": True,
                "review_required": False,
                "json_report": str(diff_dir / "beta-simulation-diff.json"),
                "markdown_report": str(diff_dir / "beta-simulation-diff.md"),
            }
            response_contract.validate_beta_simulation_diff(diff_payload)
            (diff_dir / "beta-simulation-diff.json").write_text(
                json.dumps(diff_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (diff_dir / "beta-simulation-diff.md").write_text("# Diff\n", encoding="utf-8")
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
                    "fixture_manifest_json": str(root / ".skill-beta" / "fixture-previews" / "round-1" / "beta-simulation-manifest.json"),
                    "fixture_manifest_markdown": str(root / ".skill-beta" / "fixture-previews" / "round-1" / "beta-simulation-manifest.md"),
                    "fixture_diff_json": str(diff_dir / "beta-simulation-diff.json"),
                    "fixture_diff_markdown": str(diff_dir / "beta-simulation-diff.md"),
                },
                "notes": "",
            }
            report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = beta_round_evaluator.evaluate_beta_round(report_path=report)

            self.assertTrue(result["ok"])
            self.assertEqual("advance", result["decision"])
            self.assertEqual("round-2", result["follow_up"]["next_round_recommended"])
            self.assertEqual("passed", result["diff_gate"]["status"])
            self.assertTrue(Path(result["json_report"]).exists())
            self.assertTrue(Path(result["markdown_report"]).exists())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_emits_escalate_for_critical_issues(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
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
            self.assertEqual("missing", result["diff_gate"]["status"])
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_holds_when_fixture_diff_is_missing(self) -> None:
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
            self.assertEqual("missing", result["diff_gate"]["status"])
            self.assertIn("fixture diff", result["reason"].lower())
            response_contract.validate_beta_round_gate_result(result)

    def test_evaluate_beta_round_preserves_blocker_breakdown(self) -> None:
        with make_tempdir() as tmp:
            root = Path(tmp)
            report = root / ".skill-beta" / "reports" / "round-1.json"
            report.parent.mkdir(parents=True, exist_ok=True)
            diff_dir = root / ".skill-beta" / "fixture-diffs" / "round-0-to-round-1"
            diff_dir.mkdir(parents=True, exist_ok=True)
            diff_payload = {
                "schema_version": "beta-simulation-diff/v1",
                "generated_at": "2026-04-08T12:00:00Z",
                "skill_name": "virtual-intelligent-dev-team",
                "previous_round_id": "round-0",
                "current_round_id": "round-1",
                "previous_manifest_path": str(root / ".skill-beta" / "fixture-previews" / "round-0" / "beta-simulation-manifest.json"),
                "current_manifest_path": str(root / ".skill-beta" / "fixture-previews" / "round-1" / "beta-simulation-manifest.json"),
                "previous_session_count": 4,
                "current_session_count": 6,
                "session_count_delta": 2,
                "added_personas": [],
                "removed_personas": [],
                "added_scenarios": [],
                "removed_scenarios": [],
                "added_traces": [],
                "removed_traces": [],
                "new_session_matrix": [],
                "coverage_shift_summary": {
                    "previous_persona_count": 3,
                    "current_persona_count": 4,
                    "previous_scenario_count": 3,
                    "current_scenario_count": 4,
                    "previous_trace_count": 3,
                    "current_trace_count": 4,
                    "new_session_matrix_count": 0,
                    "expansion_mode": "expanded",
                },
                "risk_notes": ["Coverage expanded while preserving the previous baseline."],
                "expansion_ok": True,
                "review_required": False,
                "json_report": str(diff_dir / "beta-simulation-diff.json"),
                "markdown_report": str(diff_dir / "beta-simulation-diff.md"),
            }
            (diff_dir / "beta-simulation-diff.json").write_text(
                json.dumps(diff_payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (diff_dir / "beta-simulation-diff.md").write_text("# Diff\n", encoding="utf-8")
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
                    "fixture_manifest_json": str(root / ".skill-beta" / "fixture-previews" / "round-1" / "beta-simulation-manifest.json"),
                    "fixture_manifest_markdown": str(root / ".skill-beta" / "fixture-previews" / "round-1" / "beta-simulation-manifest.md"),
                    "fixture_diff_json": str(diff_dir / "beta-simulation-diff.json"),
                    "fixture_diff_markdown": str(diff_dir / "beta-simulation-diff.md")
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
            self.assertEqual("passed", result["diff_gate"]["status"])
            self.assertEqual("Edge-Case Breaker", result["blocker_breakdown"]["by_persona"][0]["label"])
            markdown = Path(result["markdown_report"]).read_text(encoding="utf-8")
            self.assertIn("## Fixture Diff Gate", markdown)
            self.assertIn("## Blocker Breakdown By Persona", markdown)
            self.assertIn("## Blocker Breakdown By Scenario", markdown)

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
