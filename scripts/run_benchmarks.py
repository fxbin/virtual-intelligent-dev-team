#!/usr/bin/env python3
"""Run benchmark suite and generate machine/human-readable reports."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import re


SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent
TEST_SCRIPT = SKILL_DIR / "tests" / "test_routing_and_guardrails.py"
VALIDATOR_SCRIPT = SKILL_DIR / "scripts" / "validate_virtual_team.py"
ROUTE_SCRIPT = SKILL_DIR / "scripts" / "route_request.py"
OFFLINE_DRILL_SCRIPT = SKILL_DIR / "scripts" / "run_offline_loop_drill.py"
RESPONSE_PACK_SCRIPT = SKILL_DIR / "scripts" / "generate_response_pack.py"
RESPONSE_CONTRACT_SCRIPT = SKILL_DIR / "scripts" / "response_contract.py"
VERIFY_ACTION_SCRIPT = SKILL_DIR / "scripts" / "verify_action.py"
RELEASE_GATE_SCRIPT = SKILL_DIR / "scripts" / "run_release_gate.py"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
EVALS_PATH = SKILL_DIR / "evals" / "evals.json"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "evals" / "benchmark-results"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_route_request_benchmark", ROUTE_SCRIPT)
offline_loop_drill = load_module("virtual_team_offline_loop_drill_benchmark", OFFLINE_DRILL_SCRIPT)
response_pack = load_module("virtual_team_response_pack_benchmark", RESPONSE_PACK_SCRIPT)
response_contract = load_module("virtual_team_response_contract_benchmark", RESPONSE_CONTRACT_SCRIPT)
verify_action = load_module("virtual_team_verify_action_benchmark", VERIFY_ACTION_SCRIPT)
MISSING = object()
INTEGER_RE = re.compile(r"^-?\d+$")
FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def load_config() -> dict[str, object]:
    config = load_json(CONFIG_PATH)
    governance = config.setdefault("governance", {})
    if isinstance(governance, dict):
        fast_track = governance.setdefault("fast_track_control", {})
        if isinstance(fast_track, dict):
            fast_track["write_event_log"] = False
    return config


def classify_prompt(text: str) -> list[str]:
    lowered = text.lower()
    tags: list[str] = []

    if any(route_request.keyword_matches(lowered, token) for token in ["react", "next.js", "tailwind", "shadcn", "ui", "ux", "dashboard", "frontend", "front-end", "framer motion"]):
        tags.append("frontend")
    if any(route_request.keyword_matches(lowered, token) for token in ["python", "django", "flask", "fastapi", "celery", "go", "gin", "node", "nestjs", "java", "spring", "rust"]):
        tags.append("backend-stack")
    if any(
        route_request.keyword_matches(lowered, token)
        for token in [
            "rewrite",
            "migrate",
            "overhaul",
            "transform",
            "plan before coding",
            "planning before coding",
            "large-scale refactor",
            "大规模迁移",
            "大规模重构",
            "先规划再开发",
        ]
    ):
        tags.append("planning")
    if any(route_request.keyword_matches(lowered, token) for token in ["commit", "push", "worktree", "branch", "git", "rebase", "merge"]):
        tags.append("git-workflow")
    if any(route_request.keyword_matches(lowered, token) for token in ["review", "audit", "security review", "ux review", "code review"]):
        tags.append("review")
    if any(
        route_request.keyword_matches(lowered, token)
        for token in [
            "product brief",
            "prd",
            "acceptance criteria",
            "user flow",
            "onboarding",
            "mvp",
            "需求拆解",
            "验收标准",
        ]
    ):
        tags.append("product-delivery")
    if any(
        route_request.keyword_matches(lowered, token)
        for token in [
            "release gate",
            "rollback",
            "branch policy",
            "review bar",
            "治理",
            "回滚",
            "发布门禁",
            "分支策略",
        ]
    ):
        tags.append("technical-governance")
    if any(route_request.keyword_matches(lowered, token) for token in ["backend", "api contract", "auth", "implementation", "technical plan", "tech plan"]):
        tags.append("cross-domain")
    if any(
        route_request.keyword_matches(lowered, token)
        for token in [
            "iterate",
            "iteration",
            "benchmark",
            "optimize",
            "regression",
            "another round",
            "迭代",
            "优化",
            "基准",
            "回归",
            "再来一轮",
        ]
    ):
        tags.append("iteration")
    if any(
        route_request.keyword_matches(lowered, token)
        for token in [
            "release gate",
            "formal gate",
            "ready to ship",
            "ready to release",
            "release candidate",
            "发版前",
            "提交前验收",
            "正式验收",
            "能不能发版",
        ]
    ):
        tags.append("release-gate")
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        tags.append("chinese")
    if any(ch.isascii() and ch.isalpha() for ch in text) and any("\u4e00" <= ch <= "\u9fff" for ch in text):
        tags.append("mixed-language")
    if len(text.strip()) <= 24:
        tags.append("short-prompt")
    if len(tags) == 0:
        tags.append("general")
    return tags


def run_command(command: list[str], cwd: Path) -> dict[str, object]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "passed": proc.returncode == 0,
    }


def read_nested(data: object, path: str, default: object = MISSING) -> object:
    aliases = {
        "priority_routing agent": "reason.priority_routing.agent",
    }
    path = aliases.get(path, path)
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def parse_scalar_literal(raw: str) -> object:
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "null":
        return None
    if INTEGER_RE.match(raw):
        return int(raw)
    if FLOAT_RE.match(raw):
        return float(raw)
    return raw


def as_numeric(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def parse_field_expectation(
    expectation: str,
    data: object,
    *,
    context_label: str,
) -> tuple[bool, str]:
    if expectation.endswith(" does not exist"):
        field = expectation.removesuffix(" does not exist").strip()
        value = read_nested(data, field, default=MISSING)
        return value is MISSING, f"{context_label}.{field}={value!r}"

    if expectation.endswith(" exists"):
        field = expectation.removesuffix(" exists").strip()
        value = read_nested(data, field, default=MISSING)
        return value is not MISSING, f"{context_label}.{field}={value!r}"

    if expectation.endswith(" is null"):
        field = expectation.removesuffix(" is null").strip()
        value = read_nested(data, field, default=MISSING)
        return value is None, f"{context_label}.{field}={value!r}"

    if expectation.endswith(" is not null"):
        field = expectation.removesuffix(" is not null").strip()
        value = read_nested(data, field, default=MISSING)
        return value is not MISSING and value is not None, f"{context_label}.{field}={value!r}"

    if " length is not " in expectation:
        field, expected = expectation.split(" length is not ", 1)
        value = read_nested(data, field.strip(), default=MISSING)
        if value is MISSING or not hasattr(value, "__len__"):
            return False, f"{context_label}.{field.strip()}={value!r}"
        return len(value) != int(expected), f"{context_label}.{field.strip()}={value!r}"

    if " length is " in expectation:
        field, expected = expectation.split(" length is ", 1)
        value = read_nested(data, field.strip(), default=MISSING)
        if value is MISSING or not hasattr(value, "__len__"):
            return False, f"{context_label}.{field.strip()}={value!r}"
        return len(value) == int(expected), f"{context_label}.{field.strip()}={value!r}"

    for operator in (" >= ", " <= ", " > ", " < "):
        if operator in expectation:
            field, expected = expectation.split(operator, 1)
            value = read_nested(data, field.strip(), default=MISSING)
            numeric_value = as_numeric(value)
            expected_value = as_numeric(parse_scalar_literal(expected))
            if value is MISSING or numeric_value is None or expected_value is None:
                return False, f"{context_label}.{field.strip()}={value!r}"
            if operator == " >= ":
                return numeric_value >= expected_value, f"{context_label}.{field.strip()}={value!r}"
            if operator == " <= ":
                return numeric_value <= expected_value, f"{context_label}.{field.strip()}={value!r}"
            if operator == " > ":
                return numeric_value > expected_value, f"{context_label}.{field.strip()}={value!r}"
            return numeric_value < expected_value, f"{context_label}.{field.strip()}={value!r}"

    if " contains " in expectation:
        field, expected = expectation.split(" contains ", 1)
        value = read_nested(data, field.strip(), default=MISSING)
        if isinstance(value, list):
            return expected in value, f"{context_label}.{field.strip()}={value!r}"
        if isinstance(value, str):
            return expected in value, f"{context_label}.{field.strip()}={value!r}"
        return False, f"{context_label}.{field.strip()}={value!r}"

    if " is not " in expectation:
        field, expected = expectation.split(" is not ", 1)
        value = read_nested(data, field.strip(), default=MISSING)
        expected_value = parse_scalar_literal(expected)
        if expected_value is None:
            return value is not None and value is not MISSING, f"{context_label}.{field.strip()}={value!r}"
        if isinstance(expected_value, bool):
            return value is not expected_value, f"{context_label}.{field.strip()}={value!r}"
        if isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool):
            numeric_value = as_numeric(value)
            return numeric_value is not None and numeric_value != float(expected_value), f"{context_label}.{field.strip()}={value!r}"
        return str(value) != str(expected_value), f"{context_label}.{field.strip()}={value!r}"

    if " is " in expectation:
        field, expected = expectation.split(" is ", 1)
        value = read_nested(data, field.strip(), default=MISSING)
        expected_value = parse_scalar_literal(expected)
        if expected_value is None:
            return value is None, f"{context_label}.{field.strip()}={value!r}"
        if isinstance(expected_value, bool):
            return value is expected_value, f"{context_label}.{field.strip()}={value!r}"
        if isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool):
            numeric_value = as_numeric(value)
            return numeric_value is not None and numeric_value == float(expected_value), f"{context_label}.{field.strip()}={value!r}"
        return str(value) == str(expected_value), f"{context_label}.{field.strip()}={value!r}"

    return False, f"unsupported expectation for {context_label}"


def parse_expectation(
    expectation: str,
    result: dict[str, object],
    response_pack_markdown: str,
    response_pack_payload: dict[str, object],
    extra_payloads: dict[str, object] | None = None,
) -> tuple[bool, str]:
    if extra_payloads is None:
        extra_payloads = {}
    if expectation.startswith("response_pack contains "):
        expected = expectation.removeprefix("response_pack contains ")
        return expected in response_pack_markdown, f"response_pack={response_pack_markdown!r}"
    if expectation.startswith("response_pack_json "):
        inner_expectation = expectation.removeprefix("response_pack_json ")
        return parse_field_expectation(
            inner_expectation,
            response_pack_payload,
            context_label="response_pack_json",
        )
    if expectation.startswith("verify_action_json "):
        inner_expectation = expectation.removeprefix("verify_action_json ")
        verify_payload = extra_payloads.get("verify_action_json", {})
        return parse_field_expectation(inner_expectation, verify_payload, context_label="verify_action_json")
    if expectation.startswith("release_gate_json "):
        inner_expectation = expectation.removeprefix("release_gate_json ")
        release_payload = extra_payloads.get("release_gate_json", {})
        return parse_field_expectation(inner_expectation, release_payload, context_label="release_gate_json")
    if expectation == "assistant_agents is empty":
        value = result.get("assistant_agents")
        return value == [], f"assistant_agents={value!r}"
    if expectation == "process_skills is empty":
        value = result.get("process_skills")
        return value == [], f"process_skills={value!r}"
    if expectation == "clarifying_question is not null":
        value = result.get("clarifying_question")
        return value is not None, f"clarifying_question={value!r}"
    if expectation == "mode is not single-agent execution":
        value = str(result.get("mode"))
        return "模式 A" not in value and "single-agent" not in value.lower(), f"mode={value!r}"
    if expectation.startswith("process_plan first commands contain "):
        expected = expectation.removeprefix("process_plan first commands contain ")
        plans = result.get("process_plan")
        if not isinstance(plans, list) or len(plans) == 0:
            return False, f"process_plan={plans!r}"
        commands = plans[0].get("commands") if isinstance(plans[0], dict) else None
        if not isinstance(commands, list):
            return False, f"process_plan[0].commands={commands!r}"
        return expected in commands, f"process_plan[0].commands={commands!r}"

    return parse_field_expectation(expectation, result, context_label="result")


def evaluate_evals(config: dict[str, object]) -> dict[str, object]:
    payload = load_json(EVALS_PATH)
    response_contract.validate_benchmark_evals_payload(payload)
    evals = payload.get("evals", [])
    if not isinstance(evals, list):
        raise RuntimeError("evals.json evals must be a list")

    cases: list[dict[str, object]] = []
    category_totals: Counter[str] = Counter()
    category_passed: Counter[str] = Counter()

    for item in evals:
        if not isinstance(item, dict):
            continue
        prompt = str(item.get("prompt", ""))
        expectations = item.get("expectations", [])
        if not isinstance(expectations, list):
            expectations = []
        runner = str(item.get("runner", "route")).strip() or "route"
        response_pack_markdown = ""
        response_pack_payload: dict[str, object] = {}
        extra_payloads: dict[str, object] = {}

        if runner == "route":
            result = route_request.route_request(prompt, config, repo_path=REPO_ROOT)
            response_pack_markdown = response_pack.build_response_pack(result)
            response_pack_payload = response_pack.build_response_pack_payload(result)
        elif runner == "verify_action":
            check = str(item.get("check", "")).strip()
            assistant_agents = item.get("assistant_agents", [])
            if not isinstance(assistant_agents, list):
                assistant_agents = []
            result = verify_action.verify_action(
                text=prompt,
                config=config,
                repo_path=REPO_ROOT,
                check=check,
                process_skill=str(item.get("process_skill", "")).strip() or None,
                lead_agent=str(item.get("lead_agent", "")).strip() or None,
                assistant_agents=[str(agent) for agent in assistant_agents if str(agent).strip() != ""],
            )
            extra_payloads["verify_action_json"] = result
        elif runner == "release_gate":
            summary = item.get("release_gate_summary", {})
            if not isinstance(summary, dict):
                raise RuntimeError(f"release_gate eval {item.get('id')} must provide release_gate_summary object")
            beta_gate_config = item.get("release_gate_beta")
            if beta_gate_config is not None and not isinstance(beta_gate_config, dict):
                raise RuntimeError(f"release_gate eval {item.get('id')} must provide release_gate_beta object when present")
            release_gate_module = load_module(
                f"virtual_team_release_gate_benchmark_eval_{item.get('id')}",
                RELEASE_GATE_SCRIPT,
            )
            with tempfile.TemporaryDirectory(prefix="virtual-team-release-gate-eval-") as tmp:
                temp_root = Path(tmp)
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
                fixture_payload: dict[str, object] = {
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
                beta_gate_result = None
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
                result = release_gate_module.run_release_gate(
                    output_dir=temp_root / "release-gate-output",
                    benchmark_fixture=fixture_path,
                    beta_gate_result=beta_gate_result,
                )
            extra_payloads["release_gate_json"] = result
        else:
            raise RuntimeError(f"Unsupported eval runner: {runner}")
        failures: list[str] = []
        for raw in expectations:
            ok, detail = parse_expectation(
                str(raw),
                result,
                response_pack_markdown,
                response_pack_payload,
                extra_payloads,
            )
            if not ok:
                failures.append(f"{raw} [{detail}]")
        raw_categories = item.get("categories")
        if isinstance(raw_categories, list) and all(isinstance(category, str) for category in raw_categories):
            tags = [str(category) for category in raw_categories]
        else:
            tags = classify_prompt(prompt)
        passed = len(failures) == 0
        for tag in tags:
            category_totals[tag] += 1
            if passed:
                category_passed[tag] += 1
        cases.append(
            {
                "id": item.get("id"),
                "prompt": prompt,
                "tags": tags,
                "runner": runner,
                "lead_agent": result.get("lead_agent"),
                "assistant_agents": result.get("assistant_agents") if isinstance(result.get("assistant_agents"), list) else [],
                "response_pack_preview": response_pack_markdown[:400],
                "passed": passed,
                "failures": failures,
            }
        )

    return {
        "passed": sum(1 for case in cases if case["passed"]),
        "total": len(cases),
        "cases": cases,
        "category_breakdown": [
            {
                "category": category,
                "passed": category_passed[category],
                "total": category_totals[category],
                "pass_rate": round(category_passed[category] / max(category_totals[category], 1), 3),
            }
            for category in sorted(category_totals)
        ],
    }


def build_summary(
    test_run: dict[str, object],
    validator_run: dict[str, object],
    eval_run: dict[str, object],
    offline_drill_run: dict[str, object] | None = None,
) -> dict[str, object]:
    lead_counter = Counter()
    assistant_counter = Counter()
    failures: list[dict[str, object]] = []

    for case in eval_run["cases"]:
        lead_counter[str(case["lead_agent"])] += 1
        for assistant in case["assistant_agents"]:
            assistant_counter[str(assistant)] += 1
        if not case["passed"]:
            failures.append(
                {
                    "id": case["id"],
                    "prompt": case["prompt"],
                    "failures": case["failures"],
                }
            )

    tests_passed = bool(test_run["passed"])
    validator_passed = bool(validator_run["passed"])
    evals_passed = int(eval_run["passed"]) == int(eval_run["total"])
    offline_drill_enabled = offline_drill_run is not None
    offline_drill_passed = bool(offline_drill_run.get("ok")) if offline_drill_enabled else None
    overall_passed = tests_passed and validator_passed and evals_passed
    if offline_drill_enabled:
        overall_passed = overall_passed and bool(offline_drill_passed)

    return {
        "tests_passed": tests_passed,
        "validator_passed": validator_passed,
        "evals_passed": evals_passed,
        "offline_drill_enabled": offline_drill_enabled,
        "offline_drill_passed": offline_drill_passed,
        "overall_passed": overall_passed,
        "lead_distribution": dict(lead_counter.most_common()),
        "assistant_distribution": dict(assistant_counter.most_common()),
        "eval_failures": failures,
    }


def render_markdown(result: dict[str, object]) -> str:
    lines: list[str] = []
    summary = result["summary"]
    tests = result["test_run"]
    validator = result["validator_run"]
    evals = result["eval_run"]
    diff = result.get("diff")

    lines.append("# Benchmark Report")
    lines.append("")
    lines.append(f"- Generated: `{result['generated_at']}`")
    lines.append(f"- Overall: `{'PASS' if summary['overall_passed'] else 'FAIL'}`")
    lines.append(f"- Unit tests: `{'PASS' if summary['tests_passed'] else 'FAIL'}`")
    lines.append(f"- Semantic regression: `{'PASS' if summary['validator_passed'] else 'FAIL'}`")
    lines.append(f"- Eval prompts: `{evals['passed']}/{evals['total']}`")
    if summary.get("offline_drill_enabled"):
        lines.append(f"- Offline loop drill: `{'PASS' if summary.get('offline_drill_passed') else 'FAIL'}`")
    lines.append("")
    lines.append("## Breakdown")
    lines.append("")
    for item in evals["category_breakdown"]:
        lines.append(f"- `{item['category']}`: `{item['passed']}/{item['total']}`")
    if isinstance(diff, dict):
        lines.append("")
        lines.append("## Diff Vs Previous")
        lines.append("")
        previous = diff.get("previous_summary", {})
        if isinstance(previous, dict):
            lines.append(
                f"- Previous evals: `{previous.get('evals_passed', 0)}/{previous.get('evals_total', 0)}`"
            )
            lines.append(
                f"- Current evals: `{evals['passed']}/{evals['total']}`"
            )
        new_failures = diff.get("new_failures", [])
        resolved_failures = diff.get("resolved_failures", [])
        category_changes = diff.get("category_changes", [])
        lines.append(f"- New failures: `{len(new_failures)}`")
        lines.append(f"- Resolved failures: `{len(resolved_failures)}`")
        if category_changes:
            lines.append("")
            lines.append("### Category Changes")
            lines.append("")
            for item in category_changes:
                lines.append(
                    f"- `{item['category']}`: `{item['previous_passed']}/{item['previous_total']}` -> `{item['current_passed']}/{item['current_total']}`"
                )
    lines.append("")
    lines.append("## Lead Distribution")
    lines.append("")
    for lead, count in summary["lead_distribution"].items():
        lines.append(f"- `{lead}`: `{count}`")
    lines.append("")
    lines.append("## Assistant Distribution")
    lines.append("")
    if summary["assistant_distribution"]:
        for assistant, count in summary["assistant_distribution"].items():
            lines.append(f"- `{assistant}`: `{count}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append(f"- Tests: `{' '.join(tests['command'])}` -> return code `{tests['returncode']}`")
    lines.append(f"- Validator: `{' '.join(validator['command'])}` -> return code `{validator['returncode']}`")
    offline_drill_run = result.get("offline_drill_run")
    if isinstance(offline_drill_run, dict):
        lines.append(f"- Offline drill workspace: `{offline_drill_run.get('workspace')}`")
        lines.append(f"- Offline drill report: `{offline_drill_run.get('markdown_report')}`")
    lines.append("")
    lines.append("## Eval Failures")
    lines.append("")
    if summary["eval_failures"]:
        for item in summary["eval_failures"]:
            lines.append(f"- `#{item['id']}` {item['prompt']}")
            for failure in item["failures"]:
                lines.append(f"  - {failure}")
    else:
        lines.append("- None")
    if isinstance(diff, dict):
        new_failures = diff.get("new_failures", [])
        resolved_failures = diff.get("resolved_failures", [])
        lines.append("")
        lines.append("## Failure Delta")
        lines.append("")
        if new_failures:
            lines.append("### New Failures")
            lines.append("")
            for item in new_failures:
                lines.append(f"- `#{item['id']}` {item['prompt']}")
        else:
            lines.append("- New failures: None")
        lines.append("")
        if resolved_failures:
            lines.append("### Resolved Failures")
            lines.append("")
            for item in resolved_failures:
                lines.append(f"- `#{item['id']}` {item['prompt']}")
        else:
            lines.append("- Resolved failures: None")
    return "\n".join(lines) + "\n"


def load_previous_result(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    data = load_json(path)
    response_contract.validate_benchmark_run_result(data)
    if "eval_run" not in data or "summary" not in data:
        return None
    return data


def build_diff(current: dict[str, object], previous: dict[str, object]) -> dict[str, object]:
    current_cases = {
        str(case.get("id")): case for case in current["eval_run"]["cases"] if isinstance(case, dict)
    }
    previous_cases = {
        str(case.get("id")): case for case in previous["eval_run"]["cases"] if isinstance(case, dict)
    }
    new_failures: list[dict[str, object]] = []
    resolved_failures: list[dict[str, object]] = []
    for case_id, case in current_cases.items():
        prev = previous_cases.get(case_id)
        if prev is None:
            continue
        if bool(prev.get("passed")) and not bool(case.get("passed")):
            new_failures.append({"id": case.get("id"), "prompt": case.get("prompt")})
        if not bool(prev.get("passed")) and bool(case.get("passed")):
            resolved_failures.append({"id": case.get("id"), "prompt": case.get("prompt")})

    prev_categories = {
        item["category"]: item
        for item in previous["eval_run"].get("category_breakdown", [])
        if isinstance(item, dict) and "category" in item
    }
    curr_categories = {
        item["category"]: item
        for item in current["eval_run"].get("category_breakdown", [])
        if isinstance(item, dict) and "category" in item
    }
    all_categories = sorted(set(prev_categories) | set(curr_categories))
    category_changes: list[dict[str, object]] = []
    for category in all_categories:
        prev = prev_categories.get(category, {"passed": 0, "total": 0})
        curr = curr_categories.get(category, {"passed": 0, "total": 0})
        if prev.get("passed") != curr.get("passed") or prev.get("total") != curr.get("total"):
            category_changes.append(
                {
                    "category": category,
                    "previous_passed": prev.get("passed", 0),
                    "previous_total": prev.get("total", 0),
                    "current_passed": curr.get("passed", 0),
                    "current_total": curr.get("total", 0),
                }
            )

    prev_summary = previous.get("summary", {})
    return {
        "previous_summary": {
            "evals_passed": previous["eval_run"].get("passed", 0),
            "evals_total": previous["eval_run"].get("total", 0),
            "overall_passed": prev_summary.get("overall_passed"),
        },
        "new_failures": new_failures,
        "resolved_failures": resolved_failures,
        "category_changes": category_changes,
    }


def run_benchmark_suite(
    *,
    output_dir: Path,
    previous_output: Path | None = None,
    include_offline_drill: bool = False,
    offline_drill_workspace: Path | None = None,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_config()
    test_run = run_command([sys.executable, str(TEST_SCRIPT)], cwd=SKILL_DIR)
    validator_run = run_command([sys.executable, str(VALIDATOR_SCRIPT), "--pretty"], cwd=SKILL_DIR)
    eval_run = evaluate_evals(config)
    offline_drill_run: dict[str, object] | None = None
    if include_offline_drill:
        drill_workspace = (
            offline_drill_workspace.resolve()
            if offline_drill_workspace is not None
            else (output_dir / "offline-loop-drill").resolve()
        )
        offline_drill_run = offline_loop_drill.run_drill(workspace=drill_workspace)

    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "skill_name": "virtual-intelligent-dev-team",
        "test_run": test_run,
        "validator_run": validator_run,
        "eval_run": eval_run,
    }
    if offline_drill_run is not None:
        result["offline_drill_run"] = offline_drill_run
    result["summary"] = build_summary(
        test_run,
        validator_run,
        eval_run,
        offline_drill_run=offline_drill_run,
    )
    if previous_output is not None:
        previous = load_previous_result(previous_output.resolve())
        if previous is not None:
            result["diff"] = build_diff(result, previous)

    response_contract.validate_benchmark_run_result(result)

    json_path = output_dir / "benchmark-results.json"
    md_path = output_dir / "benchmark-report.md"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    with md_path.open("w", encoding="utf-8") as file:
        file.write(render_markdown(result))
    result["json_report"] = str(json_path)
    result["markdown_report"] = str(md_path)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run benchmark suite for virtual-intelligent-dev-team")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for benchmark artifacts")
    parser.add_argument("--previous-output", help="Previous benchmark JSON report for diff comparison")
    parser.add_argument("--include-offline-drill", action="store_true", help="Run the real offline loop drill as part of the benchmark gate")
    parser.add_argument("--offline-drill-workspace", help="Workspace root for offline drill artifacts")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON summary to stdout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_benchmark_suite(
        output_dir=Path(args.output_dir).resolve(),
        previous_output=Path(args.previous_output).resolve() if args.previous_output else None,
        include_offline_drill=bool(args.include_offline_drill),
        offline_drill_workspace=Path(args.offline_drill_workspace).resolve() if args.offline_drill_workspace else None,
    )

    stdout_payload = {
        "ok": result["summary"]["overall_passed"],
        "json_report": result["json_report"],
        "markdown_report": result["markdown_report"],
        "evals_passed": result["eval_run"]["passed"],
        "evals_total": result["eval_run"]["total"],
        "tests_passed": result["test_run"]["passed"],
        "validator_passed": result["validator_run"]["passed"],
    }
    if result["summary"].get("offline_drill_enabled"):
        stdout_payload["offline_drill_passed"] = result["summary"].get("offline_drill_passed")
        stdout_payload["offline_drill_report"] = result.get("offline_drill_run", {}).get("markdown_report")
    if "diff" in result:
        stdout_payload["new_failures"] = len(result["diff"].get("new_failures", []))
        stdout_payload["resolved_failures"] = len(result["diff"].get("resolved_failures", []))
    if args.pretty:
        print(json.dumps(stdout_payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(stdout_payload, ensure_ascii=False))
    raise SystemExit(0 if result["summary"]["overall_passed"] else 2)


if __name__ == "__main__":
    main()
