#!/usr/bin/env python3
"""Run the release acceptance gate for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path
import re


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
BENCHMARK_SCRIPT = SCRIPT_DIR / "run_benchmarks.py"
BASELINE_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"
SYNC_PATTERNS_SCRIPT = SCRIPT_DIR / "sync_distilled_patterns.py"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "evals" / "release-gate"
DEFAULT_ITERATION_WORKSPACE = SKILL_DIR / ".skill-iterations"
LABEL_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


benchmark_runner = load_module("virtual_team_release_gate_benchmark", BENCHMARK_SCRIPT)
baseline_registry = load_module("virtual_team_release_gate_baseline_registry", BASELINE_SCRIPT)
pattern_sync = load_module("virtual_team_release_gate_pattern_sync", SYNC_PATTERNS_SCRIPT)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def blocker_specs(summary: dict[str, object]) -> list[dict[str, object]]:
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
    return specs


def normalize_label(label: str, default: str) -> str:
    normalized = LABEL_SAFE_CHARS.sub("-", label.strip()).strip("-")
    return normalized or default


def build_hold_follow_up(
    *,
    output_dir: Path,
    summary: dict[str, object],
    reason: str,
    benchmark_json: str,
    benchmark_markdown: str,
    offline_drill_report: str | None,
    iteration_workspace: Path | None,
) -> dict[str, object]:
    blockers = blocker_specs(summary)
    workspace = iteration_workspace or DEFAULT_ITERATION_WORKSPACE
    blocker_labels = [str(item["label"]) for item in blockers]
    objective_hints = [str(item["objective_hint"]) for item in blockers]
    evidence_required = [str(item["evidence_required"]) for item in blockers]
    objective = (
        "恢复 release gate 就绪状态，清除以下阻塞："
        + ("；".join(blocker_labels) if blocker_labels else reason)
    )
    brief = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_gate": "release-gate",
        "decision": "hold",
        "reason": reason,
        "loop_state": "reopened",
        "owner": "Technical Trinity",
        "objective": objective,
        "objective_hints": objective_hints or ["按失败门禁逐项修复后再重新验收"],
        "blockers": blockers,
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
        + ["重新运行 formal release gate，并得到 ship 决策"],
    }
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
    markdown_lines.extend(
        [
            "",
            "## Baseline Context",
            "",
            f"- Benchmark JSON: `{benchmark_json}`",
            f"- Benchmark Markdown: `{benchmark_markdown}`",
            f"- Offline drill report: `{offline_drill_report}`",
            "",
        ]
    )
    markdown_path.write_text("\n".join(markdown_lines), encoding="utf-8")
    return {
        "loop_state": "reopened",
        "next_action": "bounded-iteration",
        "blockers": blocker_labels,
        "brief_json": str(json_path),
        "brief_markdown": str(markdown_path),
        "iteration_workspace": str(workspace),
    }


def build_ship_follow_up(
    *,
    output_dir: Path,
    benchmark_json: Path,
    benchmark_markdown: str,
    release_label: str,
    iteration_workspace: Path | None,
) -> dict[str, object]:
    closure: dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_gate": "release-gate",
        "decision": "ship",
        "loop_state": "closed",
        "next_action": "archive-and-promote",
        "release_label": release_label,
        "benchmark_report": str(benchmark_json),
        "benchmark_markdown": benchmark_markdown,
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
    }


def render_markdown(result: dict[str, object]) -> str:
    lines = [
        "# Release Gate Report",
        "",
        f"- Generated: `{result['generated_at']}`",
        f"- Gate: `{'PASS' if result['ok'] else 'FAIL'}`",
        f"- Unit tests: `{'PASS' if result['summary'].get('tests_passed') else 'FAIL'}`",
        f"- Semantic regression: `{'PASS' if result['summary'].get('validator_passed') else 'FAIL'}`",
        f"- Eval prompts: `{'PASS' if result['summary'].get('evals_passed') else 'FAIL'}`",
        f"- Offline loop drill: `{'PASS' if result['summary'].get('offline_drill_passed') else 'FAIL'}`",
        "",
        "## Artifacts",
        "",
        f"- Benchmark JSON: `{result['benchmark_json']}`",
        f"- Benchmark Markdown: `{result['benchmark_markdown']}`",
        f"- Offline drill report: `{result.get('offline_drill_report')}`",
        "",
        "## Decision",
        "",
        f"- Decision: `{result['decision']}`",
        f"- Reason: {result['reason']}",
        "",
    ]
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
        if "closure_json" in follow_up:
            lines.append(f"- Release closure JSON: `{follow_up['closure_json']}`")
            lines.append(f"- Release closure Markdown: `{follow_up['closure_markdown']}`")
        lines.append("")
    return "\n".join(lines)


def run_release_gate(
    *,
    output_dir: Path,
    previous_output: Path | None = None,
    offline_drill_workspace: Path | None = None,
    iteration_workspace: Path | None = None,
    release_label: str = "",
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark_result = benchmark_runner.run_benchmark_suite(
        output_dir=output_dir,
        previous_output=previous_output,
        include_offline_drill=True,
        offline_drill_workspace=offline_drill_workspace,
    )
    summary = benchmark_result["summary"]
    ok = bool(summary.get("overall_passed"))
    decision = "ship" if ok else "hold"
    if not summary.get("tests_passed"):
        reason = "unit tests failed"
    elif not summary.get("validator_passed"):
        reason = "semantic regression validator failed"
    elif not summary.get("evals_passed"):
        reason = "eval prompts regressed"
    elif not summary.get("offline_drill_passed"):
        reason = "offline loop drill failed"
    else:
        reason = "all benchmark and offline drill gates passed"
    resolved_release_label = normalize_label(release_label, "release-ready")
    follow_up = (
        build_ship_follow_up(
            output_dir=output_dir,
            benchmark_json=Path(benchmark_result["json_report"]).resolve(),
            benchmark_markdown=benchmark_result["markdown_report"],
            release_label=resolved_release_label,
            iteration_workspace=iteration_workspace.resolve() if iteration_workspace else None,
        )
        if ok
        else build_hold_follow_up(
            output_dir=output_dir,
            summary=summary,
            reason=reason,
            benchmark_json=benchmark_result["json_report"],
            benchmark_markdown=benchmark_result["markdown_report"],
            offline_drill_report=benchmark_result.get("offline_drill_run", {}).get("markdown_report"),
            iteration_workspace=iteration_workspace.resolve() if iteration_workspace else None,
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
    }
    json_path = output_dir / "release-gate-results.json"
    markdown_path = output_dir / "release-gate-report.md"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    with markdown_path.open("w", encoding="utf-8") as file:
        file.write(render_markdown(result))
    result["json_report"] = str(json_path)
    result["markdown_report"] = str(markdown_path)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the release acceptance gate for virtual-intelligent-dev-team")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for release gate artifacts")
    parser.add_argument("--previous-output", help="Previous benchmark JSON report for diff comparison")
    parser.add_argument("--offline-drill-workspace", help="Workspace root for offline drill artifacts")
    parser.add_argument("--iteration-workspace", help="Iteration workspace for follow-up closure artifacts")
    parser.add_argument("--release-label", default="", help="Release-ready baseline label when ship")
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
    }
    if args.pretty:
        print(json.dumps(stdout_payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(stdout_payload, ensure_ascii=False))
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
