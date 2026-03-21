#!/usr/bin/env python3
"""Run the release acceptance gate for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
BENCHMARK_SCRIPT = SCRIPT_DIR / "run_benchmarks.py"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "evals" / "release-gate"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


benchmark_runner = load_module("virtual_team_release_gate_benchmark", BENCHMARK_SCRIPT)


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
    return "\n".join(lines)


def run_release_gate(
    *,
    output_dir: Path,
    previous_output: Path | None = None,
    offline_drill_workspace: Path | None = None,
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

    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "skill_name": "virtual-intelligent-dev-team",
        "ok": ok,
        "decision": decision,
        "reason": reason,
        "summary": summary,
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
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON summary to stdout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_release_gate(
        output_dir=Path(args.output_dir).resolve(),
        previous_output=Path(args.previous_output).resolve() if args.previous_output else None,
        offline_drill_workspace=Path(args.offline_drill_workspace).resolve() if args.offline_drill_workspace else None,
    )
    stdout_payload = {
        "ok": result["ok"],
        "decision": result["decision"],
        "reason": result["reason"],
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
