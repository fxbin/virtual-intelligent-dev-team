#!/usr/bin/env python3
"""Run the release acceptance gate for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
BENCHMARK_SCRIPT = SCRIPT_DIR / "run_benchmarks.py"
BASELINE_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"
ITERATION_LOOP_SCRIPT = SCRIPT_DIR / "run_iteration_loop.py"
SYNC_PATTERNS_SCRIPT = SCRIPT_DIR / "sync_distilled_patterns.py"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
AUTOMATION_STATE_SCRIPT = SCRIPT_DIR / "automation_state.py"
EVALUATE_BETA_ROUND_SCRIPT = SCRIPT_DIR / "evaluate_beta_round.py"
INIT_POST_RELEASE_FEEDBACK_SCRIPT = SCRIPT_DIR / "init_post_release_feedback.py"
SKILL_SNAPSHOT_SCRIPT = SCRIPT_DIR / "skill_snapshot.py"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "evals" / "release-gate"
DEFAULT_ITERATION_WORKSPACE = SKILL_DIR / ".skill-iterations"
LABEL_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
BETA_GATE_RESULT_FILENAME = "beta-round-gate-result.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


benchmark_runner = load_module("virtual_team_release_gate_benchmark", BENCHMARK_SCRIPT)
baseline_registry = load_module("virtual_team_release_gate_baseline_registry", BASELINE_SCRIPT)
iteration_loop = load_module("virtual_team_release_gate_iteration_loop", ITERATION_LOOP_SCRIPT)
pattern_sync = load_module("virtual_team_release_gate_pattern_sync", SYNC_PATTERNS_SCRIPT)
response_contract = load_module("virtual_team_release_gate_response_contract", RESPONSE_CONTRACT_SCRIPT)
automation_state = load_module("virtual_team_release_gate_automation_state", AUTOMATION_STATE_SCRIPT)
beta_round_evaluator = load_module(
    "virtual_team_release_gate_beta_round_evaluator",
    EVALUATE_BETA_ROUND_SCRIPT,
)
post_release_feedback_init = load_module(
    "virtual_team_release_gate_post_release_feedback_init",
    INIT_POST_RELEASE_FEEDBACK_SCRIPT,
)
skill_snapshot = load_module("virtual_team_release_gate_skill_snapshot", SKILL_SNAPSHOT_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_benchmark_fixture(path: Path) -> dict[str, object]:
    payload = load_json(path)
    required_fields = ("summary", "json_report", "markdown_report")
    for key in required_fields:
        if key not in payload:
            raise RuntimeError(f"benchmark fixture missing required key: {key}")
    json_report = Path(str(payload["json_report"])).resolve()
    markdown_report = Path(str(payload["markdown_report"])).resolve()
    if not json_report.exists():
        raise RuntimeError(f"benchmark fixture json_report does not exist: {json_report}")
    if not markdown_report.exists():
        raise RuntimeError(f"benchmark fixture markdown_report does not exist: {markdown_report}")
    response_contract.validate_benchmark_run_result(load_json(json_report))
    offline_drill_run = payload.get("offline_drill_run")
    if isinstance(offline_drill_run, dict):
        markdown = str(offline_drill_run.get("markdown_report", "")).strip()
        if markdown != "" and not Path(markdown).resolve().exists():
            raise RuntimeError(f"benchmark fixture offline drill report does not exist: {markdown}")
    return payload


def load_beta_gate_result(path: Path) -> dict[str, object]:
    payload = load_json(path)
    response_contract.validate_beta_round_gate_result(payload)
    return payload


def load_beta_remediation_brief(path: Path) -> dict[str, object]:
    payload = load_json(path)
    response_contract.validate_beta_remediation_brief(payload)
    return payload


def find_latest_file(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda item: (item.stat().st_mtime, str(item)))


def resolve_beta_gate(
    *,
    beta_gate_result: Path | None,
    beta_decision_dir: Path | None,
    beta_report_dir: Path | None,
) -> dict[str, object] | None:
    if beta_gate_result is not None:
        resolved = beta_gate_result.resolve()
        if not resolved.exists():
            raise RuntimeError(f"beta gate result does not exist: {resolved}")
        payload = load_beta_gate_result(resolved)
        return {
            "source": "beta-gate-result",
            "result": payload,
        }

    if beta_decision_dir is not None:
        resolved_dir = beta_decision_dir.resolve()
        if not resolved_dir.exists():
            raise RuntimeError(f"beta decision directory does not exist: {resolved_dir}")
        latest_result = find_latest_file(list(resolved_dir.rglob(BETA_GATE_RESULT_FILENAME)))
        if latest_result is None:
            raise RuntimeError(f"no beta gate results found under: {resolved_dir}")
        payload = load_beta_gate_result(latest_result)
        return {
            "source": "beta-decision-dir",
            "result": payload,
        }

    if beta_report_dir is not None:
        resolved_dir = beta_report_dir.resolve()
        if not resolved_dir.exists():
            raise RuntimeError(f"beta report directory does not exist: {resolved_dir}")

        latest_report: Path | None = None
        for candidate in resolved_dir.rglob("*.json"):
            if candidate.name == BETA_GATE_RESULT_FILENAME:
                continue
            try:
                payload = load_json(candidate)
                response_contract.validate_beta_round_report(payload)
            except Exception:
                continue
            latest_report = candidate if latest_report is None else find_latest_file([latest_report, candidate])
        if latest_report is None:
            raise RuntimeError(f"no beta round reports found under: {resolved_dir}")

        payload = beta_round_evaluator.evaluate_beta_round(report_path=latest_report.resolve())
        return {
            "source": "beta-report-dir",
            "result": payload,
        }

    return None


def build_beta_gate_summary(beta_gate: dict[str, object] | None) -> dict[str, object]:
    if beta_gate is None:
        return {
            "beta_gate_enabled": False,
            "beta_gate_passed": None,
            "beta_gate_decision": None,
            "beta_gate_round_id": None,
        }

    result = beta_gate.get("result", {})
    if not isinstance(result, dict):
        result = {}
    return {
        "beta_gate_enabled": True,
        "beta_gate_passed": bool(result.get("ok")),
        "beta_gate_decision": str(result.get("decision", "")).strip() or None,
        "beta_gate_round_id": str(result.get("round_id", "")).strip() or None,
    }


def beta_gate_snapshot(beta_gate: dict[str, object] | None) -> dict[str, object] | None:
    if beta_gate is None:
        return None
    result = beta_gate.get("result", {})
    if not isinstance(result, dict):
        result = {}
    follow_up = result.get("follow_up", {})
    if not isinstance(follow_up, dict):
        follow_up = {}
    snapshot = {
        "enabled": True,
        "source": str(beta_gate.get("source", "beta-gate-result")),
        "generated_at": result.get("generated_at"),
        "ok": bool(result.get("ok")),
        "decision": result.get("decision"),
        "round_id": result.get("round_id"),
        "reason": result.get("reason"),
        "report_path": result.get("report_path"),
        "json_report": result.get("json_report"),
        "markdown_report": result.get("markdown_report"),
        "release_governance_recommended": bool(follow_up.get("release_governance_recommended")),
    }
    remediation_brief_json = str(follow_up.get("brief_json", "")).strip()
    remediation_brief_markdown = str(follow_up.get("brief_markdown", "")).strip()
    if remediation_brief_json != "":
        snapshot["remediation_brief_json"] = remediation_brief_json
    if remediation_brief_markdown != "":
        snapshot["remediation_brief_markdown"] = remediation_brief_markdown
    resume_artifacts = follow_up.get("resume_artifacts", [])
    if isinstance(resume_artifacts, list) and resume_artifacts:
        snapshot["resume_artifacts"] = [str(item) for item in resume_artifacts if str(item).strip()]
    blockers = follow_up.get("blockers", [])
    if isinstance(blockers, list) and blockers:
        snapshot["blockers"] = [str(item) for item in blockers if str(item).strip()]
    if remediation_brief_json != "":
        try:
            remediation_brief = load_beta_remediation_brief(Path(remediation_brief_json).resolve())
            snapshot["remediation_brief"] = remediation_brief
        except Exception:
            pass
    blocker_breakdown = result.get("blocker_breakdown")
    if isinstance(blocker_breakdown, dict):
        snapshot["blocker_breakdown"] = blocker_breakdown
    return snapshot


def benchmark_checks_passed(summary: dict[str, object]) -> bool:
    return bool(summary.get("tests_passed")) and bool(summary.get("validator_passed")) and bool(
        summary.get("evals_passed")
    ) and (not bool(summary.get("offline_drill_enabled")) or bool(summary.get("offline_drill_passed")))


def derive_release_gate_reason(
    *,
    summary: dict[str, object],
    beta_gate: dict[str, object] | None,
) -> str:
    beta_snapshot = beta_gate_snapshot(beta_gate)
    benchmark_ok = benchmark_checks_passed(summary)
    if beta_snapshot is not None and not bool(beta_snapshot.get("ok")) and benchmark_ok:
        return (
            f"latest beta round gate is `{beta_snapshot.get('decision')}`"
            f" for `{beta_snapshot.get('round_id')}`"
        )
    if not summary.get("tests_passed"):
        return "unit tests failed"
    if not summary.get("validator_passed"):
        return "semantic regression validator failed"
    if not summary.get("evals_passed"):
        return "eval prompts regressed"
    if summary.get("offline_drill_enabled") and not summary.get("offline_drill_passed"):
        return "offline loop drill failed"
    if beta_snapshot is not None and not bool(beta_snapshot.get("ok")):
        return (
            f"latest beta round gate is `{beta_snapshot.get('decision')}`"
            f" for `{beta_snapshot.get('round_id')}`"
        )
    return "all benchmark, offline drill, and beta gates passed"


def blocker_specs(summary: dict[str, object], beta_gate: dict[str, object] | None = None) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    if not bool(summary.get("tests_passed")):
        specs.append(
            {
                "id": "unit-tests",
                "label": "unit tests failed",
                "objective_hint": "先修复单元测试失败，再恢复发布就绪状态",
                "evidence_required": "python -m unittest virtual-intelligent-dev-team/tests/test_routing_and_guardrails.py",
            }
        )
    if not bool(summary.get("validator_passed")):
        specs.append(
            {
                "id": "semantic-regression",
                "label": "semantic regression validator failed",
                "objective_hint": "修复语义回归后，再验证路由与流程闭环",
                "evidence_required": "python scripts/validate_virtual_team.py --pretty",
            }
        )
    if not bool(summary.get("evals_passed")):
        specs.append(
            {
                "id": "eval-suite",
                "label": "eval prompts regressed",
                "objective_hint": "修复 eval 断言回归，恢复评测稳定性",
                "evidence_required": "python scripts/run_benchmarks.py --output-dir evals/benchmark-results --pretty",
            }
        )
    if summary.get("offline_drill_enabled") and not bool(summary.get("offline_drill_passed")):
        specs.append(
            {
                "id": "offline-loop-drill",
                "label": "offline loop drill failed",
                "objective_hint": "修复 rollback / pivot / resume 闭环问题，再重新验收",
                "evidence_required": "python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty",
            }
        )
    beta_snapshot = beta_gate_snapshot(beta_gate)
    if beta_snapshot is not None and not bool(beta_snapshot.get("ok")):
        decision = str(beta_snapshot.get("decision", "hold")).strip() or "hold"
        round_id = str(beta_snapshot.get("round_id", "latest-round")).strip() or "latest-round"
        if decision == "escalate":
            label = f"beta round {round_id} escalated"
            objective_hint = "冻结发布扩张，进入技术治理处理 critical issue，直到 beta gate 回到 advance 再重新验收"
        else:
            label = f"beta round {round_id} is still on hold"
            objective_hint = "修复 beta blocker 主题并重跑当前轮次，拿到 advance 后再进入 release gate"
        specs.append(
            {
                "id": "beta-round-gate",
                "label": label,
                "objective_hint": objective_hint,
                "evidence_required": f"python scripts/evaluate_beta_round.py --report .skill-beta/reports/{round_id}.json --pretty",
            }
        )
        remediation_brief = beta_snapshot.get("remediation_brief")
        if isinstance(remediation_brief, dict):
            beta_blockers = remediation_brief.get("blockers", [])
            if isinstance(beta_blockers, list):
                for item in beta_blockers:
                    if not isinstance(item, dict):
                        continue
                    blocker_id = str(item.get("id", "")).strip()
                    label = str(item.get("label", "")).strip()
                    objective_hint = str(item.get("objective_hint", "")).strip()
                    evidence_required = str(item.get("evidence_required", "")).strip()
                    if label == "":
                        continue
                    specs.append(
                        {
                            "id": f"beta-{blocker_id or 'remediation'}",
                            "label": f"beta remediation: {label}",
                            "objective_hint": objective_hint or "follow the beta remediation brief and rerun the blocked round",
                            "evidence_required": evidence_required or f"python scripts/evaluate_beta_round.py --report .skill-beta/reports/{round_id}.json --pretty",
                        }
                    )
    return specs


def normalize_label(label: str, default: str) -> str:
    normalized = LABEL_SAFE_CHARS.sub("-", label.strip()).strip("-")
    return normalized or default


def compact_text(value: object, limit: int = 180) -> str:
    text = " ".join(str(value).split())
    if limit <= 0 or len(text) <= limit:
        return text
    return text[: max(limit - 1, 1)].rstrip() + "…"


def unique_compact_values(values: list[object], *, limit: int = 180) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for raw in values:
        text = compact_text(raw, limit=limit).strip()
        if text == "" or text in seen:
            continue
        seen.add(text)
        items.append(text)
    return items


def output_excerpt(run_payload: object, max_lines: int = 6) -> list[str]:
    if not isinstance(run_payload, dict):
        return []
    lines: list[str] = []
    for key in ("stdout", "stderr"):
        content = str(run_payload.get(key, "")).strip()
        if content == "":
            continue
        for raw in content.splitlines():
            line = compact_text(raw, limit=220).strip()
            if line == "":
                continue
            lines.append(line)
            if len(lines) >= max_lines:
                return lines
    return lines


def build_benchmark_context(benchmark_result: dict[str, object]) -> dict[str, object]:
    test_run = benchmark_result.get("test_run", {})
    validator_run = benchmark_result.get("validator_run", {})
    eval_run = benchmark_result.get("eval_run", {})
    offline_drill_run = benchmark_result.get("offline_drill_run", {})

    failed_cases: list[dict[str, object]] = []
    raw_cases = eval_run.get("cases", []) if isinstance(eval_run, dict) else []
    if isinstance(raw_cases, list):
        for item in raw_cases:
            if not isinstance(item, dict) or bool(item.get("passed", False)):
                continue
            raw_tags = item.get("tags", [])
            raw_failures = item.get("failures", [])
            failed_cases.append(
                {
                    "id": item.get("id"),
                    "prompt": compact_text(item.get("prompt", ""), limit=160),
                    "tags": unique_compact_values(
                        raw_tags if isinstance(raw_tags, list) else [],
                        limit=48,
                    ),
                    "failures": unique_compact_values(
                        raw_failures if isinstance(raw_failures, list) else [],
                        limit=180,
                    )[:3],
                }
            )

    eval_passed = None
    if isinstance(eval_run, dict):
        eval_passed = int(eval_run.get("passed", 0)) == int(eval_run.get("total", 0))

    return {
        "unit_tests": {
            "passed": bool(test_run.get("passed")) if isinstance(test_run, dict) else None,
            "command": "python -m unittest virtual-intelligent-dev-team/tests/test_routing_and_guardrails.py",
            "output_excerpt": output_excerpt(test_run),
        },
        "semantic_regression": {
            "passed": bool(validator_run.get("passed")) if isinstance(validator_run, dict) else None,
            "command": "python scripts/validate_virtual_team.py --pretty",
            "output_excerpt": output_excerpt(validator_run),
        },
        "eval_suite": {
            "passed": eval_passed,
            "command": "python scripts/run_benchmarks.py --output-dir evals/benchmark-results --pretty",
            "failed_cases": failed_cases[:5],
        },
        "offline_loop_drill": {
            "enabled": "offline_drill_run" in benchmark_result,
            "passed": bool(offline_drill_run.get("ok")) if isinstance(offline_drill_run, dict) else None,
            "command": "python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty",
            "markdown_report": (
                str(offline_drill_run.get("markdown_report", "")).strip()
                if isinstance(offline_drill_run, dict)
                else ""
            )
            or None,
        },
    }


def blocker_profile(blocker_id: str) -> dict[str, object]:
    profiles: dict[str, dict[str, object]] = {
        "unit-tests": {
            "focus": "repair deterministic unit-test regressions in release gate and iteration bootstrap flow",
            "target_files": [
                "tests/test_routing_and_guardrails.py",
                "scripts/run_release_gate.py",
                "references/release-gate-playbook.md",
                "SKILL.md",
            ],
            "preferred_mutation_ops": ["replace_text", "insert_after", "write_file"],
            "acceptance_commands": [
                "python -m unittest virtual-intelligent-dev-team/tests/test_routing_and_guardrails.py",
                "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
            ],
        },
        "semantic-regression": {
            "focus": "repair routing semantics and validator expectations so the release gate contract becomes valid again",
            "target_files": [
                "scripts/route_request.py",
                "references/routing-rules.json",
                "references/regression-cases.json",
                "scripts/validate_virtual_team.py",
                "tests/test_routing_and_guardrails.py",
            ],
            "preferred_mutation_ops": ["json_set", "json_merge", "json_append_unique", "replace_text"],
            "acceptance_commands": [
                "python scripts/validate_virtual_team.py --pretty",
                "python scripts/run_benchmarks.py --output-dir evals/benchmark-results --pretty",
            ],
        },
        "eval-suite": {
            "focus": "repair failing eval prompts, routing expectations, and regression coverage without creating benchmark drift",
            "target_files": [
                "evals/evals.json",
                "references/regression-cases.json",
                "references/routing-rules.json",
                "scripts/route_request.py",
                "tests/test_routing_and_guardrails.py",
            ],
            "preferred_mutation_ops": ["json_append_unique", "json_set", "json_merge", "replace_text"],
            "acceptance_commands": [
                "python scripts/run_benchmarks.py --output-dir evals/benchmark-results --pretty",
                "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
            ],
        },
        "offline-loop-drill": {
            "focus": "repair rollback, pivot, resume, and state-sync behavior in the offline bounded iteration drill",
            "target_files": [
                "scripts/run_offline_loop_drill.py",
                "scripts/run_iteration_loop.py",
                "scripts/run_iteration_cycle.py",
                "references/offline-loop-drill-playbook.md",
                "references/rollback-and-stop-rules.md",
                "tests/test_routing_and_guardrails.py",
            ],
            "preferred_mutation_ops": ["replace_text", "insert_after", "json_set", "write_file"],
            "acceptance_commands": [
                "python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty",
                "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
            ],
        },
        "beta-round-gate": {
            "focus": "repair staged beta blockers and round evidence so release expansion can resume only after the latest beta round advances",
            "target_files": [
                "references/beta-validation-playbook.md",
                "references/release-gate-playbook.md",
                "scripts/init_beta_round_report.py",
                "scripts/evaluate_beta_round.py",
                "tests/test_routing_and_guardrails.py",
            ],
            "preferred_mutation_ops": ["write_file", "replace_text", "json_set"],
            "acceptance_commands": [
                "python scripts/evaluate_beta_round.py --report .skill-beta/reports/<round-id>.json --pretty",
                "python scripts/run_release_gate.py --output-dir evals/release-gate --beta-decision-dir .skill-beta/round-decisions --pretty",
            ],
        },
    }
    return profiles.get(
        blocker_id,
        {
            "focus": "capture blocker-aware release gate remediation context",
            "target_files": [
                "scripts/run_release_gate.py",
                "references/release-gate-playbook.md",
                "SKILL.md",
            ],
            "preferred_mutation_ops": ["write_file"],
            "acceptance_commands": [
                "python scripts/run_release_gate.py --output-dir evals/release-gate --pretty",
            ],
        },
    )


def blocker_target_files(blockers: list[dict[str, object]]) -> list[str]:
    targets: list[str] = []

    def add(*paths: str) -> None:
        for path in paths:
            if path not in targets:
                targets.append(path)

    add("scripts/run_release_gate.py", "references/release-gate-playbook.md", "SKILL.md")
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = str(item.get("id", "")).strip()
        profile = blocker_profile(blocker_id)
        add(*[str(path) for path in profile.get("target_files", [])])
    return targets


def blocker_focus(blocker: dict[str, object], brief: dict[str, object]) -> str:
    blocker_id = str(blocker.get("id", "")).strip()
    profile = blocker_profile(blocker_id)
    hint = str(blocker.get("objective_hint", "")).strip()
    label = str(blocker.get("label", "")).strip()
    reason = str(brief.get("reason", "")).strip()
    for candidate in [hint, str(profile.get("focus", "")).strip(), label, reason]:
        if candidate != "":
            return candidate
    return "capture blocker-aware release gate remediation context"


def blocker_acceptance_commands(blocker: dict[str, object]) -> list[str]:
    blocker_id = str(blocker.get("id", "")).strip()
    profile = blocker_profile(blocker_id)
    raw_commands: list[object] = []
    evidence_required = str(blocker.get("evidence_required", "")).strip()
    if evidence_required != "":
        raw_commands.append(evidence_required)
    acceptance_commands = profile.get("acceptance_commands", [])
    if isinstance(acceptance_commands, list):
        raw_commands.extend(acceptance_commands)
    return unique_compact_values(raw_commands, limit=200)


def blocker_preferred_mutation_ops(blocker: dict[str, object]) -> list[str]:
    blocker_id = str(blocker.get("id", "")).strip()
    profile = blocker_profile(blocker_id)
    raw_ops = profile.get("preferred_mutation_ops", [])
    return unique_compact_values(raw_ops if isinstance(raw_ops, list) else [], limit=64)


def blocker_evidence_snapshot(blocker: dict[str, object], brief: dict[str, object]) -> dict[str, object]:
    benchmark_context = brief.get("benchmark_context", {})
    if not isinstance(benchmark_context, dict):
        benchmark_context = {}
    blocker_id = str(blocker.get("id", "")).strip()

    if blocker_id == "unit-tests":
        payload = benchmark_context.get("unit_tests", {})
        return payload if isinstance(payload, dict) else {}
    if blocker_id == "semantic-regression":
        payload = benchmark_context.get("semantic_regression", {})
        return payload if isinstance(payload, dict) else {}
    if blocker_id == "eval-suite":
        payload = benchmark_context.get("eval_suite", {})
        return payload if isinstance(payload, dict) else {}
    if blocker_id == "offline-loop-drill":
        payload = benchmark_context.get("offline_loop_drill", {})
        return payload if isinstance(payload, dict) else {}
    if blocker_id == "beta-round-gate":
        payload = brief.get("beta_gate_context", {})
        return payload if isinstance(payload, dict) else {}
    return {}


def blocker_catalog_keywords(blocker: dict[str, object], brief: dict[str, object]) -> list[str]:
    profile = blocker_profile(str(blocker.get("id", "")).strip())
    evidence = blocker_evidence_snapshot(blocker, brief)
    raw_keywords: list[object] = [
        blocker.get("id", ""),
        blocker.get("label", ""),
        blocker.get("objective_hint", ""),
        blocker.get("evidence_required", ""),
        profile.get("focus", ""),
        "release gate",
        "hold",
        "ship",
        "发布",
        "发版",
    ]
    if isinstance(evidence, dict):
        blocker_breakdown = evidence.get("blocker_breakdown", {})
        if isinstance(blocker_breakdown, dict):
            for key in ("by_persona", "by_scenario"):
                items = blocker_breakdown.get(key, [])
                if not isinstance(items, list):
                    continue
                for item in items[:4]:
                    if not isinstance(item, dict):
                        continue
                    raw_keywords.append(item.get("label", ""))
                    themes = item.get("top_feedback_themes", [])
                    if isinstance(themes, list):
                        raw_keywords.extend(themes[:3])
        output_excerpt_payload = evidence.get("output_excerpt", [])
        if isinstance(output_excerpt_payload, list):
            raw_keywords.extend(output_excerpt_payload[:3])
        failed_cases = evidence.get("failed_cases", [])
        if isinstance(failed_cases, list):
            for item in failed_cases[:4]:
                if not isinstance(item, dict):
                    continue
                raw_keywords.extend(
                    [
                        item.get("id", ""),
                        item.get("prompt", ""),
                    ]
                )
                tags = item.get("tags", [])
                failures = item.get("failures", [])
                if isinstance(tags, list):
                    raw_keywords.extend(tags[:4])
                if isinstance(failures, list):
                    raw_keywords.extend(failures[:2])
    return unique_compact_values(raw_keywords, limit=120)


def beta_breakdown_lines(beta_context: dict[str, object]) -> list[str]:
    blocker_breakdown = beta_context.get("blocker_breakdown", {})
    if not isinstance(blocker_breakdown, dict):
        return []

    lines: list[str] = []
    by_persona = blocker_breakdown.get("by_persona", [])
    if isinstance(by_persona, list) and by_persona:
        lines.extend(["", "## Beta Blocker Breakdown By Persona", ""])
        for item in by_persona[:5]:
            if not isinstance(item, dict):
                continue
            themes = item.get("top_feedback_themes", [])
            theme_text = ", ".join(str(value) for value in themes[:3]) if isinstance(themes, list) else ""
            lines.append(
                f"- {item.get('label')}: sessions={item.get('session_count')}, blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, high={item.get('high_severity_issue_count')}, themes={theme_text}"
            )

    by_scenario = blocker_breakdown.get("by_scenario", [])
    if isinstance(by_scenario, list) and by_scenario:
        lines.extend(["", "## Beta Blocker Breakdown By Scenario", ""])
        for item in by_scenario[:5]:
            if not isinstance(item, dict):
                continue
            themes = item.get("top_feedback_themes", [])
            theme_text = ", ".join(str(value) for value in themes[:3]) if isinstance(themes, list) else ""
            lines.append(
                f"- {item.get('label')}: sessions={item.get('session_count')}, blockers={item.get('blocker_issue_count')}, critical={item.get('critical_issue_count')}, high={item.get('high_severity_issue_count')}, themes={theme_text}"
            )
    return lines


def render_hold_benchmark_signals(brief: dict[str, object]) -> list[str]:
    benchmark_context = brief.get("benchmark_context", {})
    beta_context = brief.get("beta_gate_context", {})
    if not isinstance(beta_context, dict):
        beta_context = {}
    if (not isinstance(benchmark_context, dict) or len(benchmark_context) == 0) and len(beta_context) == 0:
        return []

    lines = [
        "## Benchmark Signals",
        "",
    ]

    unit_tests = benchmark_context.get("unit_tests", {})
    if isinstance(unit_tests, dict):
        lines.append(f"- Unit tests passed: `{unit_tests.get('passed')}`")
        excerpts = unit_tests.get("output_excerpt", [])
        if isinstance(excerpts, list):
            lines.extend([f"  - {item}" for item in excerpts[:3]])

    semantic_regression = benchmark_context.get("semantic_regression", {})
    if isinstance(semantic_regression, dict):
        lines.append(f"- Semantic regression passed: `{semantic_regression.get('passed')}`")
        excerpts = semantic_regression.get("output_excerpt", [])
        if isinstance(excerpts, list):
            lines.extend([f"  - {item}" for item in excerpts[:3]])

    eval_suite = benchmark_context.get("eval_suite", {})
    if isinstance(eval_suite, dict):
        lines.append(f"- Eval suite passed: `{eval_suite.get('passed')}`")
        failed_cases = eval_suite.get("failed_cases", [])
        if isinstance(failed_cases, list):
            for item in failed_cases[:3]:
                if not isinstance(item, dict):
                    continue
                lines.append(f"  - eval#{item.get('id')}: {item.get('prompt')}")

    offline_loop_drill = benchmark_context.get("offline_loop_drill", {})
    if isinstance(offline_loop_drill, dict) and offline_loop_drill.get("enabled") is not None:
        lines.append(f"- Offline loop drill passed: `{offline_loop_drill.get('passed')}`")
        report = str(offline_loop_drill.get("markdown_report", "")).strip()
        if report != "":
            lines.append(f"  - report: `{report}`")

    if beta_context:
        lines.append(f"- Beta gate decision: `{beta_context.get('decision')}`")
        lines.append(f"  - round: `{beta_context.get('round_id')}`")
        lines.append(f"  - source: `{beta_context.get('source')}`")
        report = str(beta_context.get("json_report", "")).strip()
        if report != "":
            lines.append(f"  - report: `{report}`")
        blocker_breakdown = beta_context.get("blocker_breakdown", {})
        if isinstance(blocker_breakdown, dict):
            by_persona = blocker_breakdown.get("by_persona", [])
            by_scenario = blocker_breakdown.get("by_scenario", [])
            if isinstance(by_persona, list) and by_persona and isinstance(by_persona[0], dict):
                lines.append(
                    f"  - top persona slice: `{by_persona[0].get('label')}` blockers={by_persona[0].get('blocker_issue_count')}"
                )
            if isinstance(by_scenario, list) and by_scenario and isinstance(by_scenario[0], dict):
                lines.append(
                    f"  - top scenario slice: `{by_scenario[0].get('label')}` blockers={by_scenario[0].get('blocker_issue_count')}"
                )

    lines.append("")
    return lines


def render_hold_diagnosis_content(brief: dict[str, object]) -> str:
    blockers = brief.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    lines = [
        "# Release Gate Hold Diagnosis",
        "",
        f"- Objective: {brief.get('objective', '')}",
        f"- Reason: {brief.get('reason', '')}",
        f"- Owner: {brief.get('owner', '')}",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for item in blockers:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {item.get('label', 'unclassified blocker')}")
            hint = str(item.get("objective_hint", "")).strip()
            evidence = str(item.get("evidence_required", "")).strip()
            if hint:
                lines.append(f"  - Objective hint: {hint}")
            if evidence:
                lines.append(f"  - Evidence required: `{evidence}`")
    else:
        lines.append(f"- {brief.get('reason', 'release gate hold')}")
    beta_context = brief.get("beta_gate_context", {})
    if isinstance(beta_context, dict):
        lines.extend(beta_breakdown_lines(beta_context))
    lines.extend(render_hold_benchmark_signals(brief))
    lines.extend(
        [
            "",
            "## Current Focus",
            "",
            "- {focus}",
            "",
            "## Generation Context",
            "",
            "- Round: {round_id}",
            "- Hypothesis key: {hypothesis_key}",
            "- Generation reason: {generation_reason}",
            "",
        ]
    )
    return "\n".join(lines)


def render_hold_targets_content(brief: dict[str, object]) -> str:
    blockers = brief.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    preferred_ops = unique_compact_values(
        [
            op
            for item in blockers
            if isinstance(item, dict)
            for op in blocker_preferred_mutation_ops(item)
        ],
        limit=64,
    )
    payload = {
        "source_gate": "release-gate",
        "objective": brief.get("objective", ""),
        "reason": brief.get("reason", ""),
        "recommended_focus": "{focus}",
        "round_id": "{round_id}",
        "hypothesis_key": "{hypothesis_key}",
        "generation_reason": "{generation_reason}",
        "blocker_ids": [
            str(item.get("id", "")).strip()
            for item in blockers
            if isinstance(item, dict) and str(item.get("id", "")).strip() != ""
        ],
        "primary_blocker": (
            str(blockers[0].get("id", "")).strip()
            if blockers and isinstance(blockers[0], dict)
            else None
        ),
        "target_files": blocker_target_files(blockers),
        "preferred_mutation_ops": preferred_ops,
        "required_evidence": unique_compact_values(
            brief.get("required_evidence", []) if isinstance(brief.get("required_evidence"), list) else [],
            limit=200,
        ),
        "beta_gate_context": brief.get("beta_gate_context", {}) if isinstance(brief.get("beta_gate_context"), dict) else {},
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_blocker_remediation_content(brief: dict[str, object], blocker: dict[str, object]) -> str:
    label = str(blocker.get("label", "unclassified blocker")).strip() or "unclassified blocker"
    blocker_id = str(blocker.get("id", "")).strip() or "release-gate-hold"
    focus = blocker_focus(blocker, brief)
    target_files = blocker_target_files([blocker])
    acceptance_commands = blocker_acceptance_commands(blocker)
    preferred_ops = blocker_preferred_mutation_ops(blocker)
    evidence = blocker_evidence_snapshot(blocker, brief)

    lines = [
        f"# Release Gate Hold Remediation — {label}",
        "",
        f"- Blocker ID: `{blocker_id}`",
        f"- Objective: {brief.get('objective', '')}",
        f"- Focus: {focus}",
        "",
        "## Target Files",
        "",
    ]
    lines.extend([f"- `{path}`" for path in target_files] or ["- None captured."])
    lines.extend(["", "## Preferred Mutation Ops", ""])
    lines.extend([f"- `{item}`" for item in preferred_ops] or ["- `write_file`"])
    lines.extend(["", "## Acceptance Commands", ""])
    lines.extend([f"- `{item}`" for item in acceptance_commands] or ["- None recorded."])
    lines.extend(["", "## Evidence Snapshot", ""])

    output_excerpt_payload = evidence.get("output_excerpt", []) if isinstance(evidence, dict) else []
    if isinstance(output_excerpt_payload, list) and output_excerpt_payload:
        lines.extend([f"- {item}" for item in output_excerpt_payload[:5]])

    failed_cases = evidence.get("failed_cases", []) if isinstance(evidence, dict) else []
    if isinstance(failed_cases, list) and failed_cases:
        for item in failed_cases[:4]:
            if not isinstance(item, dict):
                continue
            lines.append(f"- eval#{item.get('id')}: {item.get('prompt')}")
            tags = item.get("tags", [])
            failures = item.get("failures", [])
            if isinstance(tags, list) and tags:
                lines.append(f"  - tags: {', '.join(str(tag) for tag in tags)}")
            if isinstance(failures, list):
                lines.extend([f"  - failure: {detail}" for detail in failures[:2]])

    if (
        not isinstance(output_excerpt_payload, list) or len(output_excerpt_payload) == 0
    ) and (not isinstance(failed_cases, list) or len(failed_cases) == 0):
        blocker_breakdown = evidence.get("blocker_breakdown", {}) if isinstance(evidence, dict) else {}
        if isinstance(blocker_breakdown, dict):
            lines.extend(beta_breakdown_lines({"blocker_breakdown": blocker_breakdown}))
        report = evidence.get("markdown_report") if isinstance(evidence, dict) else None
        if report:
            lines.append(f"- markdown report: `{report}`")
        else:
            lines.append("- No benchmark evidence excerpt captured.")

    lines.extend(
        [
            "",
            "## Generation Context",
            "",
            "- Round: {round_id}",
            "- Hypothesis key: {hypothesis_key}",
            "- Generation reason: {generation_reason}",
            "",
        ]
    )
    return "\n".join(lines)


def render_blocker_targets_content(brief: dict[str, object], blocker: dict[str, object]) -> str:
    blocker_id = str(blocker.get("id", "")).strip() or "release-gate-hold"
    payload = {
        "source_gate": "release-gate",
        "objective": brief.get("objective", ""),
        "reason": brief.get("reason", ""),
        "blocker_id": blocker_id,
        "blocker_label": str(blocker.get("label", "")).strip(),
        "recommended_focus": blocker_focus(blocker, brief),
        "round_id": "{round_id}",
        "hypothesis_key": "{hypothesis_key}",
        "generation_reason": "{generation_reason}",
        "target_files": blocker_target_files([blocker]),
        "preferred_mutation_ops": blocker_preferred_mutation_ops(blocker),
        "acceptance_commands": blocker_acceptance_commands(blocker),
        "evidence_snapshot": blocker_evidence_snapshot(blocker, brief),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def build_blocker_mutation_plan(
    brief: dict[str, object],
    blocker: dict[str, object],
    *,
    include_global: bool,
) -> dict[str, object]:
    blocker_slug = normalize_label(
        str(blocker.get("id", "")).strip() or str(blocker.get("label", "")).strip(),
        "release-gate-hold",
    )
    operations: list[dict[str, object]] = []
    if include_global:
        operations.extend(
            [
                {
                    "op": "write_file",
                    "path": "artifacts/release-gate-hold/{round_id}-diagnosis.md",
                    "content": render_hold_diagnosis_content(brief),
                },
                {
                    "op": "write_file",
                    "path": "artifacts/release-gate-hold/{round_id}-targets.json",
                    "content": render_hold_targets_content(brief),
                },
            ]
        )
    operations.extend(
        [
            {
                "op": "write_file",
                "path": f"artifacts/release-gate-hold/{{round_id}}-{blocker_slug}-remediation.md",
                "content": render_blocker_remediation_content(brief, blocker),
            },
            {
                "op": "write_file",
                "path": f"artifacts/release-gate-hold/{{round_id}}-{blocker_slug}-targets.json",
                "content": render_blocker_targets_content(brief, blocker),
            },
        ]
    )
    return {
        "mode": "patch",
        "operations": operations,
    }


def build_hold_seed_candidate(brief: dict[str, object]) -> dict[str, object]:
    blockers = brief.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    primary_blocker = blockers[0] if blockers and isinstance(blockers[0], dict) else None
    first_label = str(primary_blocker.get("label", "")).strip() if primary_blocker else ""
    first_id = str(primary_blocker.get("id", "")).strip() if primary_blocker else ""
    focus = blocker_focus(primary_blocker, brief) if primary_blocker else "capture blocker-aware release gate remediation context"
    candidate_text = (
        f"bootstrap a blocker-specific remediation candidate for {first_label}"
        if first_label
        else "capture a blocker-aware remediation scaffold for the current release gate hold"
    )
    return {
        "round_id": "round-01",
        "owner": str(brief.get("owner", "Technical Trinity")).strip() or "Technical Trinity",
        "candidate": candidate_text,
        "hypothesis_key": normalize_label(first_id or first_label or "release-gate-hold", "release-gate-hold"),
        "mutation_focus": focus,
        "mutation_plan_source": f"release-gate:{first_id or 'hold'}",
        "mutation_plan": (
            build_blocker_mutation_plan(brief, primary_blocker, include_global=True)
            if primary_blocker is not None
            else {
                "mode": "patch",
                "operations": [
                    {
                        "op": "write_file",
                        "path": "artifacts/release-gate-hold/{round_id}-diagnosis.md",
                        "content": render_hold_diagnosis_content(brief),
                    },
                    {
                        "op": "write_file",
                        "path": "artifacts/release-gate-hold/{round_id}-targets.json",
                        "content": render_hold_targets_content(brief),
                    },
                ],
            }
        ),
        "promote_label": "accepted-round-01",
    }


def build_hold_mutation_catalog(brief: dict[str, object]) -> list[dict[str, object]]:
    blockers = brief.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    catalog: list[dict[str, object]] = []
    for index, item in enumerate(blockers):
        if not isinstance(item, dict):
            continue
        blocker_id = str(item.get("id", "")).strip()
        if blocker_id == "":
            continue
        catalog.append(
            {
                "id": f"release-gate-{blocker_id}-remediation",
                "priority": max(40 - index * 5, 15),
                "when_any_keywords": blocker_catalog_keywords(item, brief),
                "mutation_plan": build_blocker_mutation_plan(brief, item, include_global=True),
            }
        )

    blocker_keywords = unique_compact_values(
        [
            str(item.get("label", "")).lower()
            for item in blockers
            if isinstance(item, dict) and str(item.get("label", "")).strip() != ""
        ]
        + [
            str(item.get("id", "")).lower()
            for item in blockers
            if isinstance(item, dict) and str(item.get("id", "")).strip() != ""
        ]
        + ["release gate", "ship", "hold", "发布", "发版"],
        limit=120,
    )
    catalog.append(
        {
            "id": "release-gate-hold-diagnosis-refresh",
            "priority": 10,
            "when_any_keywords": blocker_keywords,
            "mutation_plan": {
                "mode": "patch",
                "operations": [
                    {
                        "op": "write_file",
                        "path": "artifacts/release-gate-hold/{round_id}-diagnosis.md",
                        "content": render_hold_diagnosis_content(brief),
                    },
                    {
                        "op": "write_file",
                        "path": "artifacts/release-gate-hold/{round_id}-targets.json",
                        "content": render_hold_targets_content(brief),
                    },
                ],
            },
        }
    )
    return catalog


def copy_skill_snapshot(candidate_repo: Path) -> Path:
    return skill_snapshot.copy_skill_snapshot(candidate_repo, source_root=SKILL_DIR)


def render_hold_open_loops(brief: dict[str, object]) -> str:
    blockers = brief.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    objective_hints = brief.get("objective_hints", [])
    if not isinstance(objective_hints, list):
        objective_hints = []
    lines = [
        "# Open Loops",
        "",
        "## Active",
        "",
    ]
    if blockers:
        for item in blockers:
            if not isinstance(item, dict):
                continue
            lines.append(f"- [release-gate] {item.get('label', 'unclassified blocker')}")
            hint = str(item.get("objective_hint", "")).strip()
            if hint:
                lines.append(f"  - hint: {hint}")
    else:
        lines.append(f"- [release-gate] {brief.get('reason', 'release gate hold')}")
    if objective_hints:
        lines.extend(["", "## Objective Hints", ""])
        lines.extend([f"- {str(item)}" for item in objective_hints if str(item).strip() != ""])
    lines.extend(["", "## Recently Resolved", "", "- None yet.", ""])
    return "\n".join(lines)


def render_hold_context_chain(brief: dict[str, object], brief_json_path: Path) -> str:
    blockers = brief.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    objective_hints = brief.get("objective_hints", [])
    if not isinstance(objective_hints, list):
        objective_hints = []
    lines = [
        "# Iteration Context Chain",
        "",
        "Use this compact history to choose the next round candidate.",
        "",
        "## Release Gate Hold",
        "",
        f"- Objective: {brief.get('objective', '')}",
        f"- Reason: {brief.get('reason', '')}",
        f"- Brief JSON: `{brief_json_path}`",
        "",
        "### Blockers",
        "",
    ]
    if blockers:
        for item in blockers:
            if isinstance(item, dict):
                lines.append(f"- {item.get('label', 'unclassified blocker')}")
    else:
        lines.append(f"- {brief.get('reason', 'release gate hold')}")
    if objective_hints:
        lines.extend(["", "### Objective Hints", ""])
        lines.extend([f"- {str(item)}" for item in objective_hints if str(item).strip() != ""])
    lines.append("")
    return "\n".join(lines)


def build_hold_iteration_plan(
    *,
    workspace: Path,
    brief: dict[str, object],
    baseline_label: str,
    max_rounds: int,
    benchmark_command_template: str | None = None,
) -> dict[str, object]:
    return {
        "owner": str(brief.get("owner", "Technical Trinity")).strip() or "Technical Trinity",
        "objective": str(brief.get("objective", "recover release readiness")).strip()
        or "recover release readiness",
        "baseline_label": baseline_label,
        "autonomous_candidate_generation": True,
        "candidate_repo_template": "./repo-copy",
        "candidate_patch_template": "./patches/{round_id}.patch",
        "candidate_brief_template": "./candidate-briefs/{round_id}.json",
        "candidate_output_dir_template": "./runs/{round_id}",
        "auto_apply_rollback": True,
        "loop_policy": {
            "max_rounds": max(max_rounds, 1),
            "max_same_hypothesis_retries": 2,
            "max_consecutive_non_keep_rounds": 2,
            "auto_pivot_on_stagnation": True,
            "advance_baseline_on_keep": True,
            "halt_on_decisions": ["stop"],
            "sync_patterns_at_end": True,
        },
        "benchmark_command_template": benchmark_command_template
        or "python scripts/run_benchmarks.py --output-dir {output_dir} --pretty",
        "mutation_catalog": build_hold_mutation_catalog(brief),
        "candidates": [build_hold_seed_candidate(brief)],
        "generated_from_release_gate": {
            "source": "release-gate",
            "workspace": str(workspace),
            "reason": str(brief.get("reason", "")),
        },
    }


def bootstrap_hold_iteration_workspace(
    *,
    output_dir: Path,
    iteration_workspace: Path,
    brief: dict[str, object],
    benchmark_json: Path,
    auto_run_next_iteration_on_hold: bool,
    hold_loop_max_rounds: int,
) -> dict[str, object]:
    iteration_workspace.mkdir(parents=True, exist_ok=True)
    baseline_label = str(brief.get("baseline_label_suggestion", "stable")).strip() or "stable"
    candidate_repo = copy_skill_snapshot(iteration_workspace / "repo-copy")
    baseline_result = baseline_registry.register_baseline(
        workspace=iteration_workspace,
        label=baseline_label,
        report_path=benchmark_json,
        notes="release gate hold: bootstrap baseline for the next bounded iteration",
    )
    plan_path = iteration_workspace / "iteration-plan.release-gate.json"
    plan_payload = build_hold_iteration_plan(
        workspace=iteration_workspace,
        brief=brief,
        baseline_label=baseline_label,
        max_rounds=hold_loop_max_rounds,
        benchmark_command_template=(
            str(brief.get("hold_benchmark_command_template", "")).strip() or None
        ),
    )
    write_json(plan_path, plan_payload)
    brief_json_path = output_dir / "next-iteration-brief.json"
    open_loops_path = iteration_workspace / "open-loops.md"
    context_chain_path = iteration_workspace / "iteration-context-chain.md"
    write_text(open_loops_path, render_hold_open_loops(brief))
    write_text(context_chain_path, render_hold_context_chain(brief, brief_json_path=brief_json_path))
    sync_result = pattern_sync.sync_patterns(iteration_workspace)

    result: dict[str, object] = {
        "workspace": str(iteration_workspace),
        "candidate_repo": str(candidate_repo),
        "plan_json": str(plan_path),
        "open_loops": str(open_loops_path),
        "iteration_context_chain": str(context_chain_path),
        "baseline_registration": baseline_result,
        "distilled_pattern_sync": sync_result,
        "recommended_command": f"python scripts/run_iteration_loop.py --workspace {iteration_workspace} --plan {plan_path} --pretty",
    }
    if auto_run_next_iteration_on_hold:
        try:
            auto_result = iteration_loop.run_loop(
                workspace=iteration_workspace,
                plan_path=plan_path,
            )
            result["auto_iteration"] = {
                "status": "completed",
                "result": auto_result,
            }
        except Exception as exc:
            result["auto_iteration"] = {
                "status": "failed",
                "error": str(exc),
            }
    return result


def build_hold_follow_up(
    *,
    output_dir: Path,
    benchmark_result: dict[str, object],
    summary: dict[str, object],
    reason: str,
    benchmark_json: str,
    benchmark_markdown: str,
    offline_drill_report: str | None,
    beta_gate: dict[str, object] | None,
    iteration_workspace: Path | None,
    auto_run_next_iteration_on_hold: bool,
    hold_loop_max_rounds: int,
) -> dict[str, object]:
    blockers = blocker_specs(summary, beta_gate)
    workspace = iteration_workspace or DEFAULT_ITERATION_WORKSPACE
    beta_snapshot = beta_gate_snapshot(beta_gate)
    blocker_labels = [str(item["label"]) for item in blockers]
    objective_hints = [str(item["objective_hint"]) for item in blockers]
    evidence_required = [str(item["evidence_required"]) for item in blockers]
    beta_resume_artifacts: list[str] = []
    beta_required_evidence: list[str] = []
    beta_recommended_commands: list[str] = []
    if isinstance(beta_snapshot, dict):
        raw_resume_artifacts = beta_snapshot.get("resume_artifacts", [])
        if isinstance(raw_resume_artifacts, list):
            beta_resume_artifacts = [str(item) for item in raw_resume_artifacts if str(item).strip()]
        remediation_brief = beta_snapshot.get("remediation_brief")
        if isinstance(remediation_brief, dict):
            raw_required = remediation_brief.get("required_evidence", [])
            if isinstance(raw_required, list):
                beta_required_evidence = [str(item) for item in raw_required if str(item).strip()]
            raw_commands = remediation_brief.get("recommended_commands", [])
            if isinstance(raw_commands, list):
                beta_recommended_commands = [str(item) for item in raw_commands if str(item).strip()]
    objective = (
        "恢复 release gate 就绪状态，清除以下阻塞："
        + ("；".join(blocker_labels) if blocker_labels else reason)
    )
    brief = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_gate": "release-gate",
        "decision": "hold",
        "reason": reason,
        "loop_state": "reopened",
        "owner": "Technical Trinity",
        "objective": objective,
        "objective_hints": objective_hints or ["按失败门禁逐项修复后再重新验收"],
        "blockers": blockers,
        "benchmark_context": build_benchmark_context(benchmark_result),
        "beta_gate_context": beta_gate_snapshot(beta_gate),
        "hold_benchmark_command_template": (
            str(benchmark_result.get("hold_benchmark_command_template", "")).strip() or None
        ),
        "baseline_report": benchmark_json,
        "baseline_markdown": benchmark_markdown,
        "offline_drill_report": offline_drill_report,
        "iteration_workspace": str(workspace),
        "baseline_label_suggestion": "stable",
        "recommended_commands": [
            f"python scripts/init_iteration_round.py --workspace {workspace} --round-id round-01 --objective \"{objective}\" --baseline stable --pretty",
            f"python scripts/run_iteration_loop.py --workspace {workspace} --plan {workspace / 'iteration-plan.json'} --pretty",
            f"python scripts/run_release_gate.py --output-dir {output_dir} --iteration-workspace {workspace} --pretty",
        ],
        "required_evidence": evidence_required
        + beta_required_evidence
        + ["重新运行 formal release gate，并得到 ship 决策"],
    }
    if beta_snapshot is not None:
        brief["recommended_commands"][-1] = (
            f"python scripts/run_release_gate.py --output-dir {output_dir} "
            f"--iteration-workspace {workspace} --beta-decision-dir .skill-beta/round-decisions --pretty"
        )
    if beta_recommended_commands:
        brief["recommended_commands"] = beta_recommended_commands + brief["recommended_commands"]
    if beta_resume_artifacts:
        brief["resume_artifacts"] = beta_resume_artifacts
    json_path = output_dir / "next-iteration-brief.json"
    markdown_path = output_dir / "next-iteration-brief.md"
    write_json(json_path, brief)
    markdown_lines = [
        "# Next Iteration Brief",
        "",
        f"- Generated: `{brief['generated_at']}`",
        f"- Gate decision: `{brief['decision']}`",
        f"- Reason: {brief['reason']}",
        f"- Loop state: `{brief['loop_state']}`",
        f"- Owner: `{brief['owner']}`",
        f"- Objective: {brief['objective']}",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for item in blockers:
            markdown_lines.extend(
                [
                    f"- `{item['id']}`: {item['label']}",
                    f"  - Objective hint: {item['objective_hint']}",
                    f"  - Evidence required: `{item['evidence_required']}`",
                ]
            )
    else:
        markdown_lines.append(f"- {reason}")
    markdown_lines.extend(
        [
            "",
            "## Recommended Commands",
            "",
        ]
    )
    markdown_lines.extend([f"- `{command}`" for command in brief["recommended_commands"]])
    if beta_resume_artifacts:
        markdown_lines.extend(["", "## Beta Resume Artifacts", ""])
        markdown_lines.extend([f"- `{item}`" for item in beta_resume_artifacts])
    markdown_lines.extend(
        [
            "",
            "## Baseline Context",
            "",
            f"- Benchmark JSON: `{benchmark_json}`",
            f"- Benchmark Markdown: `{benchmark_markdown}`",
            f"- Offline drill report: `{offline_drill_report}`",
            f"- Beta gate JSON: `{beta_snapshot.get('json_report') if beta_snapshot else None}`",
            f"- Beta remediation brief JSON: `{beta_snapshot.get('remediation_brief_json') if isinstance(beta_snapshot, dict) else None}`",
            "",
        ]
    )
    markdown_path.write_text("\n".join(markdown_lines), encoding="utf-8")
    result = {
        "loop_state": "reopened",
        "next_action": "bounded-iteration",
        "blockers": blocker_labels,
        "brief_json": str(json_path),
        "brief_markdown": str(markdown_path),
        "iteration_workspace": str(workspace),
    }
    if iteration_workspace is not None:
        result["bootstrap"] = bootstrap_hold_iteration_workspace(
            output_dir=output_dir,
            iteration_workspace=iteration_workspace,
            brief=brief,
            benchmark_json=Path(benchmark_json).resolve(),
            auto_run_next_iteration_on_hold=auto_run_next_iteration_on_hold,
            hold_loop_max_rounds=hold_loop_max_rounds,
        )
    return result


def infer_repo_root(*, output_dir: Path, iteration_workspace: Path | None) -> Path:
    if iteration_workspace is not None:
        return iteration_workspace.parent
    if output_dir.parent.name == "evals":
        return output_dir.parent.parent
    return output_dir.parent


def build_post_release_bootstrap(*, repo_root: Path) -> dict[str, object]:
    bootstrap = post_release_feedback_init.init_post_release_feedback(root=repo_root, overwrite=False)
    signal_report = repo_root / ".skill-post-release" / "current-signals.json"
    triage_summary = repo_root / ".skill-post-release" / "triage-summary.md"
    return {
        "root": str(repo_root),
        "resume_anchor": str(triage_summary),
        "signal_report": str(signal_report),
        "artifacts": [str(item) for item in bootstrap.get("artifacts", []) if str(item).strip()],
        "actions": bootstrap.get("actions", []),
        "recommended_command": str(bootstrap.get("evaluation_command", "")).strip()
        or "python scripts/evaluate_post_release_feedback.py --report .skill-post-release/current-signals.json --pretty",
    }


def build_ship_follow_up(
    *,
    output_dir: Path,
    benchmark_json: Path,
    benchmark_markdown: str,
    beta_gate: dict[str, object] | None,
    release_label: str,
    iteration_workspace: Path | None,
) -> dict[str, object]:
    beta_snapshot = beta_gate_snapshot(beta_gate)
    repo_root = infer_repo_root(output_dir=output_dir, iteration_workspace=iteration_workspace)
    post_release_bootstrap = build_post_release_bootstrap(repo_root=repo_root)
    closure: dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_gate": "release-gate",
        "decision": "ship",
        "loop_state": "closed",
        "next_action": "archive-and-promote",
        "release_label": release_label,
        "benchmark_report": str(benchmark_json),
        "benchmark_markdown": benchmark_markdown,
        "beta_gate_report": beta_snapshot["json_report"] if beta_snapshot else None,
        "post_release_bootstrap": post_release_bootstrap,
    }
    if iteration_workspace is not None:
        iteration_workspace.mkdir(parents=True, exist_ok=True)
        baseline_result = baseline_registry.register_baseline(
            workspace=iteration_workspace,
            label=release_label,
            report_path=benchmark_json,
            notes="release gate ship: archived as reusable release-ready baseline",
        )
        sync_result = pattern_sync.sync_patterns(iteration_workspace)
        closure["iteration_workspace"] = str(iteration_workspace)
        closure["baseline_registration"] = baseline_result
        closure["distilled_pattern_sync"] = sync_result
    else:
        closure["iteration_workspace"] = None
        closure["baseline_registration"] = {
            "status": "skipped",
            "reason": "iteration workspace not provided",
        }
        closure["distilled_pattern_sync"] = {
            "status": "skipped",
            "reason": "iteration workspace not provided",
        }

    json_path = output_dir / "release-closure.json"
    markdown_path = output_dir / "release-closure.md"
    write_json(json_path, closure)
    markdown_lines = [
        "# Release Closure",
        "",
        f"- Generated: `{closure['generated_at']}`",
        f"- Decision: `{closure['decision']}`",
        f"- Loop state: `{closure['loop_state']}`",
        f"- Next action: `{closure['next_action']}`",
        f"- Release label: `{closure['release_label']}`",
        f"- Benchmark JSON: `{closure['benchmark_report']}`",
        f"- Benchmark Markdown: `{closure['benchmark_markdown']}`",
        f"- Beta gate JSON: `{closure.get('beta_gate_report')}`",
        "",
        "## Archive Actions",
        "",
    ]
    baseline_result = closure["baseline_registration"]
    if isinstance(baseline_result, dict) and baseline_result.get("status") == "skipped":
        markdown_lines.append(f"- Baseline registration skipped: {baseline_result['reason']}")
    else:
        markdown_lines.extend(
            [
                f"- Baseline registered: `{baseline_result['label']}`",
                f"- Stored report: `{baseline_result['stored_report']}`",
            ]
        )
    sync_result = closure["distilled_pattern_sync"]
    if isinstance(sync_result, dict) and sync_result.get("status") == "skipped":
        markdown_lines.append(f"- Distilled pattern sync skipped: {sync_result['reason']}")
    else:
        markdown_lines.extend(
            [
                f"- Distilled patterns: `{sync_result['distilled_patterns']}`",
                f"- Kept rounds captured: `{sync_result['kept_rounds']}`",
            ]
        )
    markdown_lines.extend(
        [
            "",
            "## Post-Release Feedback Loop",
            "",
            f"- Resume anchor: `{post_release_bootstrap['resume_anchor']}`",
            f"- Signal report: `{post_release_bootstrap['signal_report']}`",
            f"- Recommended command: `{post_release_bootstrap['recommended_command']}`",
        ]
    )
    for item in post_release_bootstrap["artifacts"]:
        markdown_lines.append(f"- Artifact: `{item}`")
    markdown_lines.append("")
    markdown_path.write_text("\n".join(markdown_lines), encoding="utf-8")
    return {
        "loop_state": "closed",
        "next_action": "archive-and-promote",
        "release_label": release_label,
        "closure_json": str(json_path),
        "closure_markdown": str(markdown_path),
        "baseline_registration": closure["baseline_registration"],
        "distilled_pattern_sync": closure["distilled_pattern_sync"],
        "post_release_bootstrap": post_release_bootstrap,
    }


def render_markdown(result: dict[str, object]) -> str:
    explanation_card = result.get("explanation_card", {})
    if not isinstance(explanation_card, dict):
        explanation_card = {}
    lines = [
        "# Release Gate Report",
        "",
        f"- Generated: `{result['generated_at']}`",
        f"- Gate: `{'PASS' if result['ok'] else 'FAIL'}`",
        f"- Unit tests: `{'PASS' if result['summary'].get('tests_passed') else 'FAIL'}`",
        f"- Semantic regression: `{'PASS' if result['summary'].get('validator_passed') else 'FAIL'}`",
        f"- Eval prompts: `{'PASS' if result['summary'].get('evals_passed') else 'FAIL'}`",
        f"- Offline loop drill: `{'PASS' if result['summary'].get('offline_drill_passed') else 'FAIL'}`",
        f"- Beta gate: `{'PASS' if result['summary'].get('beta_gate_passed') else 'SKIP' if result['summary'].get('beta_gate_passed') is None else 'FAIL'}`",
        "",
        "## Artifacts",
        "",
        f"- Benchmark JSON: `{result['benchmark_json']}`",
        f"- Benchmark Markdown: `{result['benchmark_markdown']}`",
        f"- Offline drill report: `{result.get('offline_drill_report')}`",
        f"- Beta gate JSON: `{result.get('beta_gate', {}).get('json_report') if isinstance(result.get('beta_gate'), dict) else None}`",
        f"- Beta gate Markdown: `{result.get('beta_gate', {}).get('markdown_report') if isinstance(result.get('beta_gate'), dict) else None}`",
        "",
        "## Decision",
        "",
        f"- Decision: `{result['decision']}`",
        f"- Reason: {result['reason']}",
        "",
    ]
    lines.extend(
        [
            "## Evidence",
            "",
            f"- Route evidence: {explanation_card.get('route_evidence', result['reason'])}",
            f"- Workflow source explanation: {explanation_card.get('workflow_source_explanation', 'Release gate is the active acceptance lane for this decision.')}",
            f"- Gate status summary: tests=`{'PASS' if result['summary'].get('tests_passed') else 'FAIL'}`, validator=`{'PASS' if result['summary'].get('validator_passed') else 'FAIL'}`, evals=`{'PASS' if result['summary'].get('evals_passed') else 'FAIL'}`, offline-drill=`{'PASS' if result['summary'].get('offline_drill_passed') else 'FAIL'}`, beta=`{'PASS' if result['summary'].get('beta_gate_passed') else 'SKIP' if result['summary'].get('beta_gate_passed') is None else 'FAIL'}`",
            "",
            "## Next Action",
            "",
            f"- Smallest executable action: {explanation_card.get('next_action', result['follow_up'].get('next_action') if isinstance(result.get('follow_up'), dict) else 'n/a')}",
            f"- Current owner: {explanation_card.get('current_owner', 'Technical Trinity')}",
            "",
            "## Resume",
            "",
            f"- Progress anchor: {explanation_card.get('progress_anchor', 'not required')}",
            "- Resume artifacts:",
        ]
    )
    resume_artifacts = explanation_card.get("resume_artifacts", [])
    if isinstance(resume_artifacts, list) and resume_artifacts:
        lines.extend([f"- `{item}`" for item in resume_artifacts])
    else:
        lines.append("- none")
    lines.append("")
    follow_up = result.get("follow_up", {})
    if isinstance(follow_up, dict):
        lines.extend(
            [
                "## Closed Loop Follow-up",
                "",
                f"- Loop state: `{follow_up.get('loop_state')}`",
                f"- Next action: `{follow_up.get('next_action')}`",
            ]
        )
        if "brief_json" in follow_up:
            lines.append(f"- Next iteration brief JSON: `{follow_up['brief_json']}`")
            lines.append(f"- Next iteration brief Markdown: `{follow_up['brief_markdown']}`")
        bootstrap = follow_up.get("bootstrap")
        if isinstance(bootstrap, dict):
            lines.append(f"- Hold bootstrap plan: `{bootstrap.get('plan_json')}`")
            lines.append(f"- Hold bootstrap workspace: `{bootstrap.get('workspace')}`")
        if "closure_json" in follow_up:
            lines.append(f"- Release closure JSON: `{follow_up['closure_json']}`")
            lines.append(f"- Release closure Markdown: `{follow_up['closure_markdown']}`")
        post_release_bootstrap = follow_up.get("post_release_bootstrap")
        if isinstance(post_release_bootstrap, dict):
            lines.append(f"- Post-release resume anchor: `{post_release_bootstrap.get('resume_anchor')}`")
            lines.append(f"- Post-release signal report: `{post_release_bootstrap.get('signal_report')}`")
        lines.append("")
    return "\n".join(lines)


def run_release_gate(
    *,
    output_dir: Path,
    previous_output: Path | None = None,
    offline_drill_workspace: Path | None = None,
    iteration_workspace: Path | None = None,
    release_label: str = "",
    auto_run_next_iteration_on_hold: bool = False,
    hold_loop_max_rounds: int = 3,
    benchmark_fixture: Path | None = None,
    beta_gate_result: Path | None = None,
    beta_decision_dir: Path | None = None,
    beta_report_dir: Path | None = None,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_iteration_workspace = iteration_workspace.resolve() if iteration_workspace else None
    repo_root = infer_repo_root(
        output_dir=output_dir.resolve(),
        iteration_workspace=resolved_iteration_workspace,
    ).resolve()
    benchmark_result = (
        load_benchmark_fixture(benchmark_fixture.resolve())
        if benchmark_fixture is not None
        else benchmark_runner.run_benchmark_suite(
            output_dir=output_dir,
            previous_output=previous_output,
            include_offline_drill=True,
            offline_drill_workspace=offline_drill_workspace,
        )
    )
    summary = dict(benchmark_result["summary"])
    beta_gate = resolve_beta_gate(
        beta_gate_result=beta_gate_result,
        beta_decision_dir=beta_decision_dir,
        beta_report_dir=beta_report_dir,
    )
    summary.update(build_beta_gate_summary(beta_gate))
    summary["overall_passed"] = bool(summary.get("overall_passed")) and (
        summary.get("beta_gate_passed") is not False
    )
    ok = bool(summary.get("overall_passed"))
    decision = "ship" if ok else "hold"
    reason = derive_release_gate_reason(summary=summary, beta_gate=beta_gate)
    resolved_release_label = normalize_label(release_label, "release-ready")
    follow_up = (
        build_ship_follow_up(
            output_dir=output_dir,
            benchmark_json=Path(benchmark_result["json_report"]).resolve(),
            benchmark_markdown=benchmark_result["markdown_report"],
            beta_gate=beta_gate,
            release_label=resolved_release_label,
            iteration_workspace=resolved_iteration_workspace,
        )
        if ok
        else build_hold_follow_up(
            output_dir=output_dir,
            benchmark_result=benchmark_result,
            summary=summary,
            reason=reason,
            benchmark_json=benchmark_result["json_report"],
            benchmark_markdown=benchmark_result["markdown_report"],
            offline_drill_report=benchmark_result.get("offline_drill_run", {}).get("markdown_report"),
            beta_gate=beta_gate,
            iteration_workspace=resolved_iteration_workspace,
            auto_run_next_iteration_on_hold=auto_run_next_iteration_on_hold,
            hold_loop_max_rounds=hold_loop_max_rounds,
        )
    )

    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "skill_name": "virtual-intelligent-dev-team",
        "ok": ok,
        "decision": decision,
        "reason": reason,
        "summary": summary,
        "release_label": resolved_release_label,
        "follow_up": follow_up,
        "benchmark_json": benchmark_result["json_report"],
        "benchmark_markdown": benchmark_result["markdown_report"],
        "offline_drill_report": benchmark_result.get("offline_drill_run", {}).get("markdown_report"),
        "beta_gate": beta_gate_snapshot(beta_gate),
    }
    result["explanation_card"] = response_contract.build_release_gate_explanation_card(
        decision=decision,
        reason=reason,
        summary=summary,
        follow_up=follow_up if isinstance(follow_up, dict) else {},
        beta_gate=result["beta_gate"] if isinstance(result.get("beta_gate"), dict) else None,
    )
    json_path = output_dir / "release-gate-results.json"
    markdown_path = output_dir / "release-gate-report.md"
    result["json_report"] = str(json_path)
    result["markdown_report"] = str(markdown_path)
    follow_up_resume_artifacts = follow_up.get("resume_artifacts", []) if isinstance(follow_up, dict) else []
    result["automation_state"] = automation_state.write_automation_state(
        repo_root=repo_root,
        source_workflow="ship-hold-remediate",
        state_kind="release-gate-result",
        mode="manual",
        phase="release-gate",
        status="completed",
        decision=decision,
        execution_mode="release-gate",
        resume_anchor=str(
            follow_up.get("resume_anchor", result["markdown_report"]) if isinstance(follow_up, dict) else result["markdown_report"]
        ),
        resume_artifacts=[str(item) for item in follow_up_resume_artifacts if str(item).strip()],
        recommended_next_step=str(
            follow_up.get("next_action", "inspect the release gate follow-up") if isinstance(follow_up, dict) else "inspect the release gate follow-up"
        ),
        handoff_target=str(
            follow_up.get("next_action", "release-decision") if isinstance(follow_up, dict) else "release-decision"
        ),
        primary_path=str(output_dir / "automation-state.json"),
        related_paths=[
            str(json_path),
            str(markdown_path),
            str(benchmark_result["json_report"]),
            str(benchmark_result["markdown_report"]),
        ],
        upstream_dependencies=[
            str(item)
            for item in [
                benchmark_result.get("json_report"),
                benchmark_result.get("markdown_report"),
                benchmark_result.get("offline_drill_run", {}).get("markdown_report"),
                (result.get("beta_gate") or {}).get("json_report") if isinstance(result.get("beta_gate"), dict) else None,
            ]
            if str(item).strip()
        ],
        metadata={
            "ok": ok,
            "auto_run_next_iteration_on_hold": auto_run_next_iteration_on_hold,
            "hold_loop_max_rounds": hold_loop_max_rounds,
        },
    )
    response_contract.validate_release_gate_result(result)
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    with markdown_path.open("w", encoding="utf-8") as file:
        file.write(render_markdown(result))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the release acceptance gate for virtual-intelligent-dev-team")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for release gate artifacts")
    parser.add_argument("--previous-output", help="Previous benchmark JSON report for diff comparison")
    parser.add_argument("--offline-drill-workspace", help="Workspace root for offline drill artifacts")
    parser.add_argument("--iteration-workspace", help="Iteration workspace for follow-up closure artifacts")
    parser.add_argument("--release-label", default="", help="Release-ready baseline label when ship")
    parser.add_argument(
        "--auto-run-next-iteration-on-hold",
        action="store_true",
        help="When hold and iteration workspace is provided, bootstrap and execute the next bounded iteration loop",
    )
    parser.add_argument(
        "--hold-loop-max-rounds",
        type=int,
        default=3,
        help="Max rounds for hold bootstrap iteration plan",
    )
    parser.add_argument(
        "--benchmark-fixture",
        help="Use a precomputed benchmark result JSON instead of running the benchmark suite (for drills/tests)",
    )
    parser.add_argument("--beta-gate-result", help="Path to a beta round gate result JSON to enforce before ship.")
    parser.add_argument(
        "--beta-decision-dir",
        help="Directory containing beta round gate results; the latest result by mtime is enforced before ship.",
    )
    parser.add_argument(
        "--beta-report-dir",
        help="Directory containing beta round reports; the latest valid report is evaluated and enforced before ship.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON summary to stdout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_release_gate(
        output_dir=Path(args.output_dir).resolve(),
        previous_output=Path(args.previous_output).resolve() if args.previous_output else None,
        offline_drill_workspace=Path(args.offline_drill_workspace).resolve() if args.offline_drill_workspace else None,
        iteration_workspace=Path(args.iteration_workspace).resolve() if args.iteration_workspace else None,
        release_label=args.release_label,
        auto_run_next_iteration_on_hold=args.auto_run_next_iteration_on_hold,
        hold_loop_max_rounds=args.hold_loop_max_rounds,
        benchmark_fixture=Path(args.benchmark_fixture).resolve() if args.benchmark_fixture else None,
        beta_gate_result=Path(args.beta_gate_result).resolve() if args.beta_gate_result else None,
        beta_decision_dir=Path(args.beta_decision_dir).resolve() if args.beta_decision_dir else None,
        beta_report_dir=Path(args.beta_report_dir).resolve() if args.beta_report_dir else None,
    )
    stdout_payload = {
        "ok": result["ok"],
        "decision": result["decision"],
        "reason": result["reason"],
        "release_label": result["release_label"],
        "follow_up": result["follow_up"],
        "json_report": result["json_report"],
        "markdown_report": result["markdown_report"],
        "benchmark_json": result["benchmark_json"],
        "benchmark_markdown": result["benchmark_markdown"],
        "offline_drill_report": result["offline_drill_report"],
        "beta_gate": result["beta_gate"],
    }
    if args.pretty:
        print(json.dumps(stdout_payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(stdout_payload, ensure_ascii=False))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
