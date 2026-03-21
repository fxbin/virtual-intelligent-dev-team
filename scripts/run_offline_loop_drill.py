#!/usr/bin/env python3
"""Run real multi-round offline loop drills for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTER_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"
LOOP_SCRIPT = SCRIPT_DIR / "run_iteration_loop.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline_registry = load_module("virtual_team_drill_baseline_registry", REGISTER_SCRIPT)
iteration_loop = load_module("virtual_team_drill_iteration_loop", LOOP_SCRIPT)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def run_process(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )


def git(repo: Path, *args: str) -> str:
    return run_process(["git", *args], cwd=repo).stdout


def configure_repo(repo: Path) -> None:
    git(repo, "config", "user.name", "Codex Drill")
    git(repo, "config", "user.email", "codex-drill@example.com")


def benchmark_payload(
    *,
    overall_passed: bool,
    evals_passed: int,
    failure_ids: list[int],
    category_score: int,
) -> dict[str, object]:
    failing = set(failure_ids)
    return {
        "summary": {"overall_passed": overall_passed},
        "eval_run": {
            "passed": evals_passed,
            "total": 54,
            "cases": [
                {
                    "id": 1,
                    "prompt": "existing baseline coverage",
                    "passed": 1 not in failing,
                    "failures": [] if 1 not in failing else ["existing failure"],
                },
                {
                    "id": 2,
                    "prompt": "new regression coverage",
                    "passed": 2 not in failing,
                    "failures": [] if 2 not in failing else ["new failure"],
                },
            ],
            "category_breakdown": [
                {"category": "iteration", "passed": category_score, "total": 1},
                {"category": "optimization", "passed": category_score, "total": 1},
            ],
        },
    }


def create_candidate_repo_with_signal_benchmark(repo: Path) -> None:
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    write_json(repo / "signals.json", {"mode": "baseline", "focus": "baseline"})
    write_text(
        repo / "scripts" / "run_benchmarks.py",
        """#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
parser.add_argument("--pretty", action="store_true")
args = parser.parse_args()

output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
signals = json.loads(Path("signals.json").read_text(encoding="utf-8"))
mode = str(signals.get("mode", "baseline"))

if mode == "regress":
    payload = {
        "summary": {"overall_passed": False},
        "eval_run": {
            "passed": 52,
            "total": 54,
            "cases": [
                {"id": 1, "prompt": "existing baseline coverage", "passed": False, "failures": ["existing failure"]},
                {"id": 2, "prompt": "new regression coverage", "passed": False, "failures": ["new failure"]},
            ],
            "category_breakdown": [
                {"category": "iteration", "passed": 0, "total": 1},
                {"category": "optimization", "passed": 0, "total": 1},
            ],
        },
    }
elif mode == "improve":
    payload = {
        "summary": {"overall_passed": True},
        "eval_run": {
            "passed": 54,
            "total": 54,
            "cases": [
                {"id": 1, "prompt": "existing baseline coverage", "passed": True, "failures": []},
                {"id": 2, "prompt": "new regression coverage", "passed": True, "failures": []},
            ],
            "category_breakdown": [
                {"category": "iteration", "passed": 1, "total": 1},
                {"category": "optimization", "passed": 1, "total": 1},
            ],
        },
    }
else:
    payload = {
        "summary": {"overall_passed": False},
        "eval_run": {
            "passed": 53,
            "total": 54,
            "cases": [
                {"id": 1, "prompt": "existing baseline coverage", "passed": False, "failures": ["existing failure"]},
                {"id": 2, "prompt": "new regression coverage", "passed": True, "failures": []},
            ],
            "category_breakdown": [
                {"category": "iteration", "passed": 0, "total": 1},
                {"category": "optimization", "passed": 0, "total": 1},
            ],
        },
    }

(output_dir / "benchmark-results.json").write_text(
    json.dumps(payload, ensure_ascii=False),
    encoding="utf-8",
)
print(json.dumps({"ok": True, "mode": mode}, ensure_ascii=False))
""",
    )
    git(repo, "init")
    configure_repo(repo)
    git(repo, "add", "signals.json", "scripts/run_benchmarks.py")
    git(repo, "commit", "-m", "chore: init drill candidate repo")


def create_candidate_repo_with_resume_gate(repo: Path) -> None:
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    write_text(
        repo / "scripts" / "run_drill_benchmarks.py",
        """#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
parser.add_argument("--round-number", required=True, type=int)
args = parser.parse_args()

output_dir = Path(args.output_dir)
output_dir.mkdir(parents=True, exist_ok=True)
resume_flag = Path("../resume-allow.flag")

if args.round_number == 1:
    payload = {
        "summary": {"overall_passed": False},
        "eval_run": {
            "passed": 52,
            "total": 54,
            "cases": [
                {"id": 1, "prompt": "existing baseline coverage", "passed": False, "failures": ["existing failure"]},
                {"id": 2, "prompt": "new regression coverage", "passed": False, "failures": ["new failure"]},
            ],
            "category_breakdown": [
                {"category": "iteration", "passed": 0, "total": 1},
                {"category": "optimization", "passed": 0, "total": 1},
            ],
        },
    }
else:
    if not resume_flag.exists():
        sys.stderr.write("resume gate not open\\n")
        raise SystemExit(7)
    payload = {
        "summary": {"overall_passed": True},
        "eval_run": {
            "passed": 54,
            "total": 54,
            "cases": [
                {"id": 1, "prompt": "existing baseline coverage", "passed": True, "failures": []},
                {"id": 2, "prompt": "new regression coverage", "passed": True, "failures": []},
            ],
            "category_breakdown": [
                {"category": "iteration", "passed": 1, "total": 1},
                {"category": "optimization", "passed": 1, "total": 1},
            ],
        },
    }

(output_dir / "benchmark-results.json").write_text(
    json.dumps(payload, ensure_ascii=False),
    encoding="utf-8",
)
print(json.dumps({"ok": True, "round_number": args.round_number}, ensure_ascii=False))
""",
    )


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def scenario_rollback_then_keep(root: Path) -> dict[str, object]:
    scenario_dir = root / "rollback-then-keep"
    workspace = scenario_dir / "workspace"
    candidate_repo = scenario_dir / "candidate-repo"
    workspace.mkdir(parents=True, exist_ok=True)
    candidate_repo.mkdir(parents=True, exist_ok=True)

    create_candidate_repo_with_signal_benchmark(candidate_repo)
    baseline_report = scenario_dir / "baseline.json"
    write_json(
        baseline_report,
        benchmark_payload(
            overall_passed=False,
            evals_passed=53,
            failure_ids=[1],
            category_score=0,
        ),
    )
    baseline_registry.register_baseline(
        workspace=workspace,
        label="stable",
        report_path=baseline_report,
        notes="offline drill stable baseline",
    )

    plan = {
        "objective": "prove rollback then keep with real patch materialization and baseline promotion",
        "owner": "Technical Trinity",
        "baseline_label": "stable",
        "candidate_brief_template": "./briefs/{round_id}.json",
        "candidate_patch_template": "./patches/{round_id}.patch",
        "candidate_output_dir_template": "./runs/{round_id}",
        "loop_policy": {
            "max_rounds": 2,
            "advance_baseline_on_keep": True,
            "halt_on_decisions": ["keep", "stop"],
            "sync_patterns_at_end": True,
            "max_same_hypothesis_retries": 2,
        },
        "candidates": [
            {
                "round_id": "round-01",
                "candidate": "test a regressing routing mutation before rollback",
                "candidate_repo": str(candidate_repo),
                "auto_apply_rollback": True,
                "mutation_plan": {
                    "mode": "patch",
                    "operations": [
                        {
                            "op": "json_set",
                            "path": "signals.json",
                            "pointer": "/mode",
                            "value": "regress",
                        },
                        {
                            "op": "json_set",
                            "path": "signals.json",
                            "pointer": "/focus",
                            "value": "git-workflow",
                        },
                    ],
                },
            },
            {
                "round_id": "round-02",
                "candidate": "apply a safer routing improvement and keep it",
                "candidate_repo": str(candidate_repo),
                "auto_apply_rollback": True,
                "mutation_plan": {
                    "mode": "patch",
                    "operations": [
                        {
                            "op": "json_set",
                            "path": "signals.json",
                            "pointer": "/mode",
                            "value": "improve",
                        },
                        {
                            "op": "json_set",
                            "path": "signals.json",
                            "pointer": "/focus",
                            "value": "semantic-owner",
                        },
                    ],
                },
            },
        ],
    }
    plan_path = workspace / "iteration-plan.json"
    write_json(plan_path, plan)
    result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)

    decisions = [str(item.get("decision", "")) for item in result.get("rounds_run", [])]
    signals = load_json(candidate_repo / "signals.json")
    open_loops = (workspace / "open-loops.md").read_text(encoding="utf-8")
    patterns = (workspace / "distilled-patterns.md").read_text(encoding="utf-8")
    assert_true(decisions == ["rollback", "keep"], f"unexpected rollback/keep decisions: {decisions}")
    assert_true(str(result.get("final_baseline_label")) == "accepted-round-02", "baseline was not promoted after keep")
    assert_true(str(signals.get("mode")) == "improve", "kept candidate did not remain applied")
    assert_true("resolved-by round-02" in open_loops, "resolved open loop entry was not preserved")
    assert_true("round-02" in patterns, "kept round was not distilled into patterns")

    return {
        "scenario": "rollback-then-keep",
        "status": "passed",
        "workspace": str(workspace),
        "plan": str(plan_path),
        "summary": str(result.get("summary")),
        "round_count": result.get("round_count"),
        "decision_counts": result.get("decision_counts"),
        "final_baseline_label": result.get("final_baseline_label"),
        "signals": signals,
        "open_loops": str(workspace / "open-loops.md"),
        "distilled_patterns": str(workspace / "distilled-patterns.md"),
    }


def scenario_pivot_then_resume(root: Path) -> dict[str, object]:
    scenario_dir = root / "pivot-then-resume"
    workspace = scenario_dir / "workspace"
    candidate_repo = scenario_dir / "candidate-repo"
    resume_flag = scenario_dir / "resume-allow.flag"
    workspace.mkdir(parents=True, exist_ok=True)
    candidate_repo.mkdir(parents=True, exist_ok=True)

    create_candidate_repo_with_resume_gate(candidate_repo)
    baseline_report = scenario_dir / "baseline.json"
    write_json(
        baseline_report,
        benchmark_payload(
            overall_passed=False,
            evals_passed=53,
            failure_ids=[1],
            category_score=0,
        ),
    )
    baseline_registry.register_baseline(
        workspace=workspace,
        label="stable",
        report_path=baseline_report,
        notes="offline drill stable baseline",
    )
    write_text(
        workspace / "open-loops.md",
        "# Open Loops\n\n## Active\n\n- latency bottleneck\n- reliability bottleneck\n\n## Recently Resolved\n\n- None.\n",
    )
    write_text(
        workspace / "distilled-patterns.md",
        "# Distilled Patterns\n\n- Preserve the semantic owner while switching to the next bottleneck.\n",
    )
    write_text(
        workspace / "iteration-context-chain.md",
        "# Iteration Context Chain\n\n- latency bottleneck\n- reliability bottleneck\n",
    )

    plan = {
        "objective": "prove auto pivot and safe resume in a deep offline loop",
        "owner": "Technical Trinity",
        "baseline_label": "stable",
        "autonomous_candidate_generation": True,
        "candidate_repo_template": str(candidate_repo),
        "candidate_brief_template": "./briefs/{round_id}.json",
        "candidate_output_dir_template": "./runs/{round_id}",
        "benchmark_command_template": "python scripts/run_drill_benchmarks.py --output-dir {output_dir} --round-number {round_number}",
        "loop_policy": {
            "max_rounds": 2,
            "advance_baseline_on_keep": False,
            "halt_on_decisions": ["keep", "stop"],
            "sync_patterns_at_end": True,
            "max_same_hypothesis_retries": 1,
            "auto_pivot_on_stagnation": True,
        },
        "candidates": [
            {
                "round_id": "round-01",
                "candidate": "initial latency hypothesis",
                "hypothesis_key": "latency-bottleneck",
            }
        ],
    }
    plan_path = workspace / "iteration-plan.json"
    write_json(plan_path, plan)

    interruption = None
    try:
        iteration_loop.run_loop(workspace=workspace, plan_path=plan_path)
    except RuntimeError as exc:
        interruption = str(exc)

    assert_true(interruption is not None and "resume gate not open" in interruption, "expected resume-gated interruption did not occur")
    running_state = load_json(workspace / "loops" / "iteration-plan-state.json")
    assert_true(str(running_state.get("status")) == "running", "loop state should remain resumable after interruption")
    assert_true(int(running_state.get("round_count", 0)) == 1, "interrupted run should persist exactly one completed round")

    write_text(resume_flag, "resume is now allowed\n")
    result = iteration_loop.run_loop(workspace=workspace, plan_path=plan_path, resume=True)

    decisions = [str(item.get("decision", "")) for item in result.get("rounds_run", [])]
    latency_key = iteration_loop.normalize_hypothesis_key("latency-bottleneck")
    round_two = result["rounds_run"][1]
    round_two_brief = load_json(workspace / "briefs" / "round-02.json")
    assert_true(decisions == ["rollback", "keep"], f"unexpected pivot/resume decisions: {decisions}")
    assert_true(bool(result.get("resume_requested")), "resume flag was not recorded")
    assert_true(bool(result.get("resumed_from_existing")), "resume path was not recorded")
    assert_true(int(result.get("pivot_count", 0)) == 1, "pivot was not recorded")
    assert_true(latency_key in result.get("blocked_hypothesis_keys", []), "blocked hypothesis key missing after pivot")
    assert_true(str(round_two.get("candidate_source")) == "auto-generated", "pivoted round was not auto-generated")
    assert_true("same hypothesis retry budget exhausted" in str(round_two.get("generation_reason")), "pivot reason missing from resumed round")
    assert_true("reliability bottleneck" in json.dumps(round_two_brief, ensure_ascii=False), "resumed brief did not pivot to the next bottleneck")

    return {
        "scenario": "pivot-then-resume",
        "status": "passed",
        "workspace": str(workspace),
        "plan": str(plan_path),
        "summary": str(result.get("summary")),
        "round_count": result.get("round_count"),
        "decision_counts": result.get("decision_counts"),
        "pivot_count": result.get("pivot_count"),
        "blocked_hypothesis_keys": result.get("blocked_hypothesis_keys"),
        "resume_requested": result.get("resume_requested"),
        "resumed_from_existing": result.get("resumed_from_existing"),
        "brief_round_02": str(workspace / "briefs" / "round-02.json"),
    }


def render_markdown_report(root: Path, scenarios: list[dict[str, object]]) -> str:
    lines = [
        "# Offline Loop Drill Report",
        "",
        "This report captures the real multi-round drill scenarios for bounded self-optimization.",
        "",
    ]
    for item in scenarios:
        lines.extend(
            [
                f"## {item['scenario']}",
                "",
                f"- Status: `{item['status']}`",
                f"- Workspace: `{item['workspace']}`",
                f"- Plan: `{item['plan']}`",
                f"- Summary: `{item['summary']}`",
                f"- Round count: `{item['round_count']}`",
            ]
        )
        if "decision_counts" in item:
            lines.append(f"- Decision counts: `{json.dumps(item['decision_counts'], ensure_ascii=False)}`")
        if "final_baseline_label" in item:
            lines.append(f"- Final baseline label: `{item['final_baseline_label']}`")
        if "pivot_count" in item:
            lines.append(f"- Pivot count: `{item['pivot_count']}`")
        if "resume_requested" in item:
            lines.append(f"- Resume requested: `{item['resume_requested']}`")
            lines.append(f"- Resumed from existing: `{item['resumed_from_existing']}`")
        lines.append("")
    return "\n".join(lines)


def run_drill(workspace: Path) -> dict[str, object]:
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    scenarios = [
        scenario_rollback_then_keep(workspace),
        scenario_pivot_then_resume(workspace),
    ]
    markdown_report = workspace / "offline-loop-drill-report.md"
    write_text(markdown_report, render_markdown_report(workspace, scenarios))
    return {
        "ok": True,
        "workspace": str(workspace),
        "markdown_report": str(markdown_report),
        "scenarios": scenarios,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real offline loop drills for virtual-intelligent-dev-team.")
    parser.add_argument("--workspace", default=".tmp-offline-loop-drill", help="Workspace root for drill artifacts")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_drill(workspace=Path(args.workspace).resolve())
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
