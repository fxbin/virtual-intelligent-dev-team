#!/usr/bin/env python3
"""Semantic regression validation for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib.util
import json
import subprocess
from pathlib import Path
from uuid import uuid4


SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent
TMP_ROOT = REPO_ROOT / ".tmp-validation"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
CASES_PATH = SKILL_DIR / "references" / "regression-cases.json"
ROUTE_SCRIPT = SKILL_DIR / "scripts" / "route_request.py"
GUARDRAIL_SCRIPT = SKILL_DIR / "scripts" / "git_workflow_guardrail.py"
VERIFY_ACTION_SCRIPT = SKILL_DIR / "scripts" / "verify_action.py"
CONTRACT_LINT_SCRIPT = SKILL_DIR / "scripts" / "lint_virtual_team_contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_route_request_validator", ROUTE_SCRIPT)
guardrail = load_module("virtual_team_guardrail_validator", GUARDRAIL_SCRIPT)
verify_action = load_module("virtual_team_verify_action_validator", VERIFY_ACTION_SCRIPT)
contract_lint = load_module("virtual_team_contract_lint_validator", CONTRACT_LINT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def load_config() -> dict[str, object]:
    config = load_json(CONFIG_PATH)
    governance = config.setdefault("governance", {})
    if not isinstance(governance, dict):
        raise RuntimeError("routing-rules.json governance must be an object")
    fast_track = governance.setdefault("fast_track_control", {})
    if not isinstance(fast_track, dict):
        raise RuntimeError("routing-rules.json governance.fast_track_control must be an object")
    fast_track["write_event_log"] = False
    return config


def run_git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    return (proc.stdout or "").strip()


def configure_repo(repo: Path) -> None:
    run_git("config", "user.name", "Codex Validator", cwd=repo)
    run_git("config", "user.email", "codex-validator@example.com", cwd=repo)


@contextmanager
def make_tempdir():
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"tmp-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    yield str(path)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_routing_cases(config: dict[str, object], cases: list[dict[str, object]]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for case in cases:
        name = str(case.get("name", "unnamed"))
        text = str(case.get("text", ""))
        expect = case.get("expect", {})
        if not isinstance(expect, dict):
            raise AssertionError(f"routing case {name} missing expect object")

        result = route_request.route_request(text=text, config=config, repo_path=REPO_ROOT)
        check(result["lead_agent"] == expect.get("lead_agent"), f"{name}: unexpected lead_agent")

        if "assistant_agents" in expect:
            check(result["assistant_agents"] == expect["assistant_agents"], f"{name}: unexpected assistants")
        if "assistant_agents_contains" in expect:
            expected_agents = expect["assistant_agents_contains"]
            check(isinstance(expected_agents, list), f"{name}: assistant_agents_contains must be a list")
            for agent in expected_agents:
                check(agent in result["assistant_agents"], f"{name}: missing assistant {agent}")
        if "needs_git_workflow" in expect:
            check(result["needs_git_workflow"] == expect["needs_git_workflow"], f"{name}: unexpected needs_git_workflow")
        if "needs_release_gate" in expect:
            check(result["needs_release_gate"] == expect["needs_release_gate"], f"{name}: unexpected needs_release_gate")
        if "process_skills" in expect:
            check(result["process_skills"] == expect["process_skills"], f"{name}: unexpected process_skills")
        if "workflow_bundle" in expect:
            check(result["workflow_bundle"] == expect["workflow_bundle"], f"{name}: unexpected workflow_bundle")
        if "bundle_confidence" in expect:
            check(result["bundle_confidence"] == expect["bundle_confidence"], f"{name}: unexpected bundle_confidence")
        if "progress_anchor_recommended" in expect:
            check(
                result["progress_anchor_recommended"] == expect["progress_anchor_recommended"],
                f"{name}: unexpected progress_anchor_recommended",
            )
        if "resume_artifacts_contains" in expect:
            expected_artifacts = expect["resume_artifacts_contains"]
            check(isinstance(expected_artifacts, list), f"{name}: resume_artifacts_contains must be a list")
            for artifact in expected_artifacts:
                check(
                    artifact in result.get("resume_artifacts", []),
                    f"{name}: missing resume artifact {artifact}",
                )
        if "bundle_bootstrap_commands_contains" in expect:
            expected_commands = expect["bundle_bootstrap_commands_contains"]
            commands = (result.get("workflow_bundle_bootstrap") or {}).get("commands", [])
            check(isinstance(expected_commands, list), f"{name}: bundle_bootstrap_commands_contains must be a list")
            check(isinstance(commands, list), f"{name}: workflow_bundle_bootstrap.commands must be a list")
            for command in expected_commands:
                check(command in commands, f"{name}: missing bootstrap command {command}")
        if "bundle_bootstrap_artifacts_contains" in expect:
            expected_artifacts = expect["bundle_bootstrap_artifacts_contains"]
            artifacts = (result.get("workflow_bundle_bootstrap") or {}).get("artifacts", [])
            check(isinstance(expected_artifacts, list), f"{name}: bundle_bootstrap_artifacts_contains must be a list")
            check(isinstance(artifacts, list), f"{name}: workflow_bundle_bootstrap.artifacts must be a list")
            for artifact in expected_artifacts:
                check(artifact in artifacts, f"{name}: missing bootstrap artifact {artifact}")

        priority_agent = (result["reason"]["priority_routing"] or {}).get("agent")
        check(priority_agent == expect.get("priority_agent"), f"{name}: unexpected priority routing agent")
        results.append({"name": name, "status": "passed"})
    return results


def validate_process_plan_cases(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for case in cases:
        name = str(case.get("name", "unnamed"))
        repo_strategy = case.get("repo_strategy", {})
        expect = case.get("expect", {})
        if not isinstance(repo_strategy, dict) or not isinstance(expect, dict):
            raise AssertionError(f"process plan case {name} is malformed")

        plan = route_request.build_process_plan(
            needs_pre_development_planning=bool(
                case.get("needs_pre_development_planning", False)
            ),
            needs_iteration=bool(case.get("needs_iteration", False)),
            needs_worktree=bool(case.get("needs_worktree", False)),
            needs_release_gate=bool(case.get("needs_release_gate", False)),
            needs_git_workflow=bool(case.get("needs_git_workflow", False)),
            repo_strategy=repo_strategy,
        )
        check(len(plan) > 0, f"{name}: empty process plan")
        commands = plan[0].get("commands", [])
        artifacts = plan[0].get("artifacts", [])
        check(isinstance(commands, list), f"{name}: commands must be a list")
        check(isinstance(artifacts, list), f"{name}: artifacts must be a list")

        for command in expect.get("commands_contains", []):
            check(command in commands, f"{name}: missing command {command}")
        for artifact in expect.get("artifacts_contains", []):
            check(artifact in artifacts, f"{name}: missing artifact {artifact}")
        for first, second in expect.get("ordered_pairs", []):
            check(first in commands and second in commands, f"{name}: missing ordered pair commands")
            check(commands.index(first) < commands.index(second), f"{name}: invalid command order")
        results.append({"name": name, "status": "passed"})
    return results


def scenario_g0_staged_should_fail() -> None:
    with make_tempdir() as tmp:
        repo = Path(tmp)
        run_git("init", cwd=repo)
        configure_repo(repo)
        (repo / "demo.txt").write_text("base\n", encoding="utf-8")
        run_git("add", "demo.txt", cwd=repo)
        run_git("commit", "-m", "chore: init repo", cwd=repo)
        (repo / "demo.txt").write_text("base\nchange\n", encoding="utf-8")
        run_git("add", "demo.txt", cwd=repo)

        try:
            guardrail.validate_stage(repo=repo, stage="G0", commit_message=None, max_staged_files=20)
        except RuntimeError as exc:
            check("pre-existing staged changes" in str(exc), "g0 staged case: unexpected error message")
            return
        raise AssertionError("g0 staged case: expected failure did not occur")


def scenario_g3_behind_should_report_sync() -> None:
    with make_tempdir() as tmp:
        repo = Path(tmp)
        run_git("init", cwd=repo)
        configure_repo(repo)
        run_git("checkout", "-b", "main", cwd=repo)
        (repo / "demo.txt").write_text("v1\n", encoding="utf-8")
        run_git("add", "demo.txt", cwd=repo)
        run_git("commit", "-m", "feat: add demo file", cwd=repo)
        base_sha = run_git("rev-parse", "HEAD", cwd=repo)

        run_git("branch", "upstream-main", cwd=repo)
        run_git("checkout", "upstream-main", cwd=repo)
        (repo / "demo.txt").write_text("v1\nv2\n", encoding="utf-8")
        run_git("add", "demo.txt", cwd=repo)
        run_git("commit", "-m", "fix: update demo file", cwd=repo)

        run_git("checkout", "main", cwd=repo)
        run_git("reset", "--hard", base_sha, cwd=repo)
        run_git("branch", "--set-upstream-to=upstream-main", "main", cwd=repo)

        result = guardrail.validate_stage(repo=repo, stage="G3", commit_message=None, max_staged_files=20)
        details = result.get("details", {})
        check(result.get("passed") is True, "g3 behind case: expected pass")
        check(int(details.get("behind", 0)) == 1, "g3 behind case: expected behind=1")
        check(bool(details.get("requires_sync")) is True, "g3 behind case: expected requires_sync=true")


def validate_guardrail_cases(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for case in cases:
        name = str(case.get("name", "unnamed"))
        case_type = str(case.get("type", ""))
        if case_type == "command_policy":
            expect = case.get("expect", {})
            if not isinstance(expect, dict):
                raise AssertionError(f"{name}: expect must be an object")
            commands = case.get("commands", [])
            check(isinstance(commands, list), f"{name}: commands must be a list")
            policy = guardrail.analyze_command_policy(commands)
            check(policy["max_risk"] == expect.get("max_risk"), f"{name}: unexpected max_risk")
            decisions = expect.get("decisions", {})
            check(isinstance(decisions, dict), f"{name}: decisions must be an object")
            policy_map = {item["command"]: item["risk"] for item in policy["decisions"]}
            for command, risk in decisions.items():
                check(policy_map.get(command) == risk, f"{name}: unexpected risk for {command}")
        elif case_type == "g0_staged_should_fail":
            scenario_g0_staged_should_fail()
        elif case_type == "g3_behind_should_report_sync":
            scenario_g3_behind_should_report_sync()
        else:
            raise AssertionError(f"{name}: unknown guardrail case type {case_type}")
        results.append({"name": name, "status": "passed"})
    return results


def validate_verify_action_cases(
    config: dict[str, object], cases: list[dict[str, object]]
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for case in cases:
        name = str(case.get("name", "unnamed"))
        text = str(case.get("text", ""))
        check_name = str(case.get("check", ""))
        expect = case.get("expect", {})
        if not isinstance(expect, dict):
            raise AssertionError(f"{name}: expect must be an object")

        result = verify_action.verify_action(
            text=text,
            config=config,
            repo_path=REPO_ROOT,
            check=check_name,
            process_skill=str(case.get("process_skill", "")) or None,
            lead_agent=str(case.get("lead_agent", "")) or None,
            assistant_agents=[
                str(item)
                for item in case.get("assistant_agents", [])
                if isinstance(item, str)
            ],
        )

        if "allowed" in expect:
            check(result["allowed"] == expect["allowed"], f"{name}: unexpected allowed decision")
        if "summary_contains" in expect:
            needle = str(expect["summary_contains"])
            check(needle in str(result.get("summary", "")), f"{name}: summary missing {needle!r}")
        if "recommended_next_step_contains" in expect:
            needle = str(expect["recommended_next_step_contains"])
            check(
                needle in str(result.get("recommended_next_step", "")),
                f"{name}: recommended_next_step missing {needle!r}",
            )
        if "detail_equals" in expect:
            detail_equals = expect["detail_equals"]
            check(isinstance(detail_equals, dict), f"{name}: detail_equals must be an object")
            details = result.get("details", {})
            check(isinstance(details, dict), f"{name}: result details must be an object")
            for key, value in detail_equals.items():
                check(details.get(key) == value, f"{name}: unexpected details[{key!r}]")
        results.append({"name": name, "status": "passed"})
    return results


def validate_contract_lint() -> list[dict[str, object]]:
    result = contract_lint.lint_contract(SKILL_DIR)
    errors = result.get("errors", [])
    if not bool(result.get("ok")):
        raise AssertionError(f"contract lint failed: {' | '.join(str(item) for item in errors)}")
    return [{"name": "mechanical_contract_lint", "status": "passed"}]


def validate() -> dict[str, object]:
    config = load_config()
    cases = load_json(CASES_PATH)

    routing_cases = cases.get("routing_cases", [])
    process_plan_cases = cases.get("process_plan_cases", [])
    guardrail_cases = cases.get("guardrail_cases", [])
    verify_action_cases = cases.get("verify_action_cases", [])
    check(isinstance(routing_cases, list), "routing_cases must be a list")
    check(isinstance(process_plan_cases, list), "process_plan_cases must be a list")
    check(isinstance(guardrail_cases, list), "guardrail_cases must be a list")
    check(isinstance(verify_action_cases, list), "verify_action_cases must be a list")

    sections = {
        "contract_lint": validate_contract_lint(),
        "routing_cases": validate_routing_cases(config, routing_cases),
        "process_plan_cases": validate_process_plan_cases(process_plan_cases),
        "guardrail_cases": validate_guardrail_cases(guardrail_cases),
        "verify_action_cases": validate_verify_action_cases(config, verify_action_cases),
    }
    total_passed = sum(len(items) for items in sections.values())
    return {
        "ok": True,
        "config_version": str(config.get("meta", {}).get("version", "unknown")),
        "cases_file": str(CASES_PATH),
        "passed": total_passed,
        "sections": sections,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate semantic regressions for virtual-intelligent-dev-team")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = validate()
        exit_code = 0
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
        exit_code = 2

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
