#!/usr/bin/env python3
"""Run one bounded-iteration state-machine cycle and write local artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
BENCHMARK_SCRIPT = SCRIPT_DIR / "run_benchmarks.py"
REGISTER_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"
INIT_SCRIPT = SCRIPT_DIR / "init_iteration_round.py"
COMPARE_SCRIPT = SCRIPT_DIR / "compare_benchmark_results.py"
PROMOTE_SCRIPT = SCRIPT_DIR / "promote_iteration_baseline.py"
SYNC_SCRIPT = SCRIPT_DIR / "sync_distilled_patterns.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline_registry = load_module("virtual_team_baseline_registry", REGISTER_SCRIPT)
iteration_init = load_module("virtual_team_iteration_init", INIT_SCRIPT)
benchmark_compare = load_module("virtual_team_benchmark_compare", COMPARE_SCRIPT)
baseline_promotion = load_module("virtual_team_baseline_promotion", PROMOTE_SCRIPT)
pattern_sync = load_module("virtual_team_pattern_sync", SYNC_SCRIPT)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def round_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("round-")
    try:
        return (int(suffix), path.name)
    except ValueError:
        return (10**9, path.name)


def load_registry(workspace: Path) -> dict[str, object]:
    registry_path = workspace / "baselines" / "registry.json"
    if not registry_path.exists():
        raise RuntimeError("baseline registry not found; run register_benchmark_baseline.py first")
    return baseline_registry.load_json(registry_path)


def resolve_baseline_report(workspace: Path, label: str) -> Path:
    registry = load_registry(workspace)
    items = registry.get("baselines", [])
    if not isinstance(items, list):
        raise RuntimeError("baseline registry is malformed")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("label") != label:
            continue
        stored_report = item.get("stored_report")
        if not isinstance(stored_report, str) or stored_report.strip() == "":
            raise RuntimeError(f"baseline {label} has no stored report")
        return Path(stored_report).resolve()
    raise RuntimeError(f"baseline label not found: {label}")


def resolve_candidate_repo(candidate_repo: Path | None) -> Path:
    return candidate_repo.resolve() if candidate_repo is not None else SKILL_DIR


def resolve_benchmark_script(candidate_repo: Path | None) -> Path:
    benchmark_root = resolve_candidate_repo(candidate_repo)
    benchmark_script = benchmark_root / "scripts" / "run_benchmarks.py"
    if not benchmark_script.exists():
        raise RuntimeError(f"benchmark script not found in candidate repo: {benchmark_script}")
    return benchmark_script


def normalize_command(command: str, output_dir: Path) -> str:
    return command.replace("{output_dir}", str(output_dir))


def is_git_repo(path: Path) -> bool:
    probe = run_process(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
    return bool(probe["passed"]) and str(probe["stdout"]).strip() == "true"


def run_process(command: list[str], cwd: Path) -> dict[str, object]:
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


def run_checked_process(command: list[str], cwd: Path) -> dict[str, object]:
    result = run_process(command, cwd)
    if not result["passed"]:
        raise RuntimeError(str(result["stdout"]) + str(result["stderr"]))
    return result


def run_command(command: str, cwd: Path) -> dict[str, object]:
    proc = subprocess.run(
        ["/bin/zsh", "-lc", command],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    result = {
        "command": command,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "passed": proc.returncode == 0,
    }
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return result


def write_if_present(path: Path, content: str) -> str | None:
    if content == "":
        return None
    write_text(path, content)
    return str(path)


def capture_candidate_snapshot(round_dir: Path, candidate_root: Path, stage: str) -> dict[str, object]:
    snapshot_dir = round_dir / "workspace-snapshots" / stage
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "stage": stage,
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "candidate_root": str(candidate_root),
        "snapshot_dir": str(snapshot_dir),
    }

    git_repo = is_git_repo(candidate_root)
    payload["git_repo"] = git_repo
    if not git_repo:
        entries = sorted(path.name for path in candidate_root.iterdir()) if candidate_root.exists() else []
        payload["top_level_entries"] = entries[:50]
        snapshot_path = snapshot_dir / "snapshot.json"
        write_json(snapshot_path, payload)
        payload["snapshot"] = str(snapshot_path)
        return payload

    head = run_process(["git", "rev-parse", "--verify", "HEAD"], cwd=candidate_root)
    status = run_process(["git", "status", "--short", "--branch"], cwd=candidate_root)
    diff_stat = run_process(["git", "diff", "--stat"], cwd=candidate_root)
    staged_diff_stat = run_process(["git", "diff", "--cached", "--stat"], cwd=candidate_root)
    working_diff = run_process(["git", "diff", "--no-ext-diff", "--binary"], cwd=candidate_root)
    staged_diff = run_process(["git", "diff", "--cached", "--no-ext-diff", "--binary"], cwd=candidate_root)

    payload["head"] = str(head["stdout"]).strip() if head["passed"] else None
    payload["status"] = write_if_present(snapshot_dir / "status.txt", str(status["stdout"]))
    payload["diff_stat"] = write_if_present(snapshot_dir / "diff.stat.txt", str(diff_stat["stdout"]))
    payload["staged_diff_stat"] = write_if_present(
        snapshot_dir / "staged.diff.stat.txt",
        str(staged_diff_stat["stdout"]),
    )
    payload["working_diff"] = write_if_present(snapshot_dir / "working.diff", str(working_diff["stdout"]))
    payload["staged_diff"] = write_if_present(snapshot_dir / "staged.diff", str(staged_diff["stdout"]))
    payload["dirty"] = any(
        line.strip() != "" and not line.startswith("##")
        for line in str(status["stdout"]).splitlines()
    )
    snapshot_path = snapshot_dir / "snapshot.json"
    write_json(snapshot_path, payload)
    payload["snapshot"] = str(snapshot_path)
    return payload


def apply_patch_file(candidate_root: Path, patch_path: Path, patch_strip: int, reverse: bool = False) -> dict[str, object]:
    if not patch_path.exists():
        raise RuntimeError(f"candidate patch does not exist: {patch_path}")
    if is_git_repo(candidate_root):
        command = ["git", "apply", f"-p{patch_strip}"]
        if reverse:
            command.append("-R")
        command.append(str(patch_path))
    else:
        command = ["patch", f"-p{patch_strip}"]
        if reverse:
            command.append("-R")
        command.extend(["-i", str(patch_path)])
    return run_checked_process(command, cwd=candidate_root)


def run_benchmarks(
    output_dir: Path,
    candidate_repo: Path | None = None,
    benchmark_command: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark_root = resolve_candidate_repo(candidate_repo)
    if benchmark_command is not None:
        run_command(normalize_command(benchmark_command, output_dir), cwd=benchmark_root)
    else:
        benchmark_script = resolve_benchmark_script(candidate_repo)
        command = [
            sys.executable,
            str(benchmark_script),
            "--output-dir",
            str(output_dir),
            "--pretty",
        ]
        proc = subprocess.run(
            command,
            cwd=str(benchmark_root),
            text=True,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout + proc.stderr)
    report_path = output_dir / "benchmark-results.json"
    if not report_path.exists():
        raise RuntimeError("candidate benchmark report was not generated")
    return report_path


def render_ledger(
    round_id: str,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    candidate_repo: Path | None,
    baseline_report: Path,
    candidate_report: Path,
    comparison: dict[str, object],
) -> str:
    content = iteration_init.prepare_ledger(
        round_id=round_id,
        objective=objective,
        baseline=baseline_label,
        owner=owner,
    ).rstrip()
    reasons = comparison.get("decision_reason", [])
    if not isinstance(reasons, list):
        reasons = []
    lines = [
        content,
        "",
        "## Evidence Summary",
        "",
        f"- Baseline report: `{baseline_report}`",
        f"- Candidate report: `{candidate_report}`",
        f"- Candidate repo: `{candidate_repo.resolve()}`" if candidate_repo is not None else "- Candidate repo: controller workspace",
        f"- Candidate summary: `{comparison.get('candidate')}`",
        "",
        "## Decision",
        "",
        f"- Decision: `{comparison.get('decision', 'stop')}`",
        "- Decision reason:",
    ]
    lines.extend([f"  - {reason}" for reason in reasons] or ["  - no decision reason recorded"])
    return "\n".join(lines) + "\n"


def render_reflection(candidate: str, comparison: dict[str, object]) -> str:
    content = iteration_init.prepare_reflection(candidate=candidate).rstrip()
    reasons = comparison.get("decision_reason", [])
    if not isinstance(reasons, list):
        reasons = []
    lines = [
        content,
        "",
        "## Decision Outcome",
        "",
        f"- Decision: `{comparison.get('decision', 'stop')}`",
        "- Evidence-backed conclusion:",
    ]
    lines.extend([f"  - {reason}" for reason in reasons] or ["  - no evidence-backed conclusion recorded"])
    return "\n".join(lines) + "\n"


def summarize_deltas(comparison: dict[str, object]) -> str:
    new_failures = comparison.get("new_failures", [])
    resolved_failures = comparison.get("resolved_failures", [])
    category_improvements = comparison.get("category_improvements", [])
    category_regressions = comparison.get("category_regressions", [])
    return (
        f"resolved_failures={len(resolved_failures)}, "
        f"new_failures={len(new_failures)}, "
        f"category_improvements={len(category_improvements)}, "
        f"category_regressions={len(category_regressions)}"
    )


def suggested_next_move(decision: str) -> str:
    if decision == "keep":
        return "advance the accepted baseline and optimize the next bottleneck"
    if decision == "retry":
        return "change one execution variable and collect stronger evidence"
    if decision == "rollback":
        return "revert this direction and try a narrower or safer candidate"
    return "close the loop unless the objective or evidence source changes"


def next_evidence_focus(decision: str) -> str:
    if decision == "keep":
        return "verify the next candidate against the newly promoted baseline"
    if decision == "retry":
        return "improve the benchmark or test signal before changing direction"
    if decision == "rollback":
        return "re-run validator, benchmark, and targeted tests on the rollback candidate"
    return "capture the final accepted evidence and stop iterating"


def render_round_memory(
    round_id: str,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    comparison: dict[str, object],
) -> str:
    content = iteration_init.prepare_round_memory(
        round_id=round_id,
        objective=objective,
        baseline=baseline_label,
        owner=owner,
        candidate=candidate,
    )
    decision = str(comparison.get("decision", "stop"))
    reasons = comparison.get("decision_reason", [])
    if not isinstance(reasons, list):
        reasons = []
    content = iteration_init.replace_line(content, "- Overall result:", f"`{decision}`")
    content = iteration_init.replace_line(content, "- Key deltas:", summarize_deltas(comparison))
    content = iteration_init.replace_line(
        content,
        "- Main risk:",
        reasons[0] if reasons else "none recorded",
    )
    content = iteration_init.replace_line(
        content,
        "- Open loops:",
        "none" if decision in {"keep", "stop"} else "; ".join(reasons) or "needs another round",
    )
    content = iteration_init.replace_line(
        content,
        "- Suggested next move:",
        suggested_next_move(decision),
    )
    return content


def render_self_feedback(candidate: str, comparison: dict[str, object]) -> str:
    content = iteration_init.prepare_self_feedback(candidate=candidate)
    decision = str(comparison.get("decision", "stop"))
    reasons = comparison.get("decision_reason", [])
    if not isinstance(reasons, list):
        reasons = []
    category_improvements = comparison.get("category_improvements", [])
    category_regressions = comparison.get("category_regressions", [])

    helped = []
    hurt = []
    if decision == "keep":
        helped.append("the candidate improved evidence without violating hard constraints")
    if len(category_improvements) > 0:
        helped.append(f"{len(category_improvements)} benchmark categories improved")
    if decision == "rollback":
        hurt.append("the current candidate created a measurable regression")
    if len(category_regressions) > 0:
        hurt.append(f"{len(category_regressions)} benchmark categories regressed")
    if len(reasons) > 0:
        if decision in {"rollback", "retry", "stop"}:
            hurt.extend(str(reason) for reason in reasons)
        else:
            helped.extend(str(reason) for reason in reasons)

    content = iteration_init.replace_line(
        content,
        "- Signals worth keeping:",
        "; ".join(helped) if helped else "no durable positive signal recorded yet",
    )
    content = iteration_init.replace_line(
        content,
        "- Signals that regressed or blocked progress:",
        "; ".join(hurt) if hurt else "no hard regressions observed",
    )
    content = iteration_init.replace_line(
        content,
        "- One variable to change next:",
        suggested_next_move(decision),
    )
    content = iteration_init.replace_line(
        content,
        "- Evidence to collect next:",
        next_evidence_focus(decision),
    )
    return content


def render_context_chain(workspace: Path) -> str:
    lines = [
        "# Iteration Context Chain",
        "",
        "Use this compact history to choose the next round candidate.",
        "",
    ]
    round_dirs = sorted(
        (path for path in workspace.glob("round-*") if path.is_dir()),
        key=round_sort_key,
    )
    if not round_dirs:
        lines.extend(["- None yet.", ""])
        return "\n".join(lines)

    for round_dir in round_dirs:
        round_id = round_dir.name
        memory_path = round_dir / "round-memory.md"
        feedback_path = round_dir / "self-feedback.md"
        if not memory_path.exists() and not feedback_path.exists():
            continue
        lines.extend([f"## {round_id}", ""])
        if memory_path.exists():
            lines.extend(["### Round Memory", "", read_text(memory_path).strip(), ""])
        if feedback_path.exists():
            lines.extend(["### Self Feedback", "", read_text(feedback_path).strip(), ""])
    open_loops_path = workspace / "open-loops.md"
    if open_loops_path.exists():
        lines.extend(["## Current Open Loops", "", read_text(open_loops_path).strip(), ""])
    distilled_patterns_path = workspace / "distilled-patterns.md"
    if distilled_patterns_path.exists():
        lines.extend(["## Distilled Patterns", "", read_text(distilled_patterns_path).strip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def sync_context_chain(workspace: Path) -> Path:
    path = workspace / "iteration-context-chain.md"
    write_text(path, render_context_chain(workspace))
    return path


def build_state(
    round_id: str,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    candidate_repo: Path | None,
    candidate_patch: Path | None,
    patch_strip: int,
    hypothesis_key: str | None,
    benchmark_command: str | None,
    apply_command: str | None,
    rollback_command: str | None,
    auto_apply_rollback: bool,
    baseline_report: Path,
    candidate_report: Path,
    comparison: dict[str, object],
    round_memory_path: Path,
    self_feedback_path: Path,
    context_chain_path: Path,
    workspace_snapshots: dict[str, object],
    apply_result: dict[str, object] | None,
    rollback_result: dict[str, object] | None,
) -> dict[str, object]:
    decision = str(comparison.get("decision"))
    promotion_eligible = decision == "keep"
    if decision == "keep":
        next_action = "promote baseline and sync distilled patterns"
    elif decision in {"retry", "rollback"}:
        next_action = "run another bounded iteration round with revised candidate"
    else:
        next_action = "close the loop and preserve only distilled learnings"
    return {
        "round_id": round_id,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "completed",
        "objective": objective,
        "baseline_label": baseline_label,
        "owner": owner,
        "candidate": candidate,
        "candidate_repo": str(candidate_repo.resolve()) if candidate_repo is not None else None,
        "candidate_patch": str(candidate_patch.resolve()) if candidate_patch is not None else None,
        "patch_strip": patch_strip,
        "hypothesis_key": hypothesis_key,
        "benchmark_command": benchmark_command,
        "apply_command": apply_command,
        "rollback_command": rollback_command,
        "auto_apply_rollback": auto_apply_rollback,
        "baseline_report": str(baseline_report),
        "candidate_report": str(candidate_report),
        "round_memory": str(round_memory_path),
        "self_feedback": str(self_feedback_path),
        "memory_chain": str(context_chain_path),
        "workspace_snapshots": workspace_snapshots,
        "apply_result": apply_result,
        "rollback_result": rollback_result,
        "decision": decision,
        "decision_reason": comparison.get("decision_reason", []),
        "promotion_eligible": promotion_eligible,
        "next_action": next_action,
        "steps": [
            {"name": "initialized", "status": "completed"},
            {"name": "benchmarked", "status": "completed"},
            {"name": "evaluated", "status": "completed"},
            {"name": "closed", "status": "completed"},
        ],
        "comparison": comparison,
    }


def dedupe_lines(items: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = " ".join(str(item).split())
        if normalized == "" or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def parse_open_loops(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {"active": [], "resolved": []}

    active: list[str] = []
    resolved: list[str] = []
    current_section = "active"
    saw_section_header = False
    for raw in read_text(path).splitlines():
        line = raw.strip()
        if line.startswith("## "):
            saw_section_header = True
            lowered = line.lower()
            if lowered == "## active":
                current_section = "active"
            elif lowered in {"## resolved", "## recently resolved"}:
                current_section = "resolved"
            else:
                current_section = ""
            continue
        if not line.startswith("- "):
            continue
        value = line[2:].strip()
        if value.lower() == "none.":
            continue
        if current_section == "resolved":
            resolved.append(value)
        elif current_section == "active" or not saw_section_header:
            active.append(value)
    return {
        "active": dedupe_lines(active),
        "resolved": dedupe_lines(resolved),
    }


def render_open_loops(active: list[str], resolved: list[str]) -> str:
    active_items = dedupe_lines(active)
    resolved_items = dedupe_lines(resolved)
    lines = [
        "# Open Loops",
        "",
        "## Active",
        "",
    ]
    if active_items:
        lines.extend([f"- {item}" for item in active_items])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Recently Resolved",
            "",
        ]
    )
    if resolved_items:
        lines.extend([f"- {item}" for item in resolved_items])
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def resolve_open_loop_entry(entry: str, round_id: str) -> str:
    if "-> resolved-by " in entry:
        return entry
    return f"{entry} -> resolved-by {round_id}"


def update_open_loops(workspace: Path, round_id: str, comparison: dict[str, object]) -> Path:
    path = workspace / "open-loops.md"
    decision = str(comparison.get("decision", "stop"))
    reasons = comparison.get("decision_reason", [])
    if not isinstance(reasons, list):
        reasons = []
    previous = parse_open_loops(path)

    if decision in {"keep", "stop"}:
        active_items: list[str] = []
        resolved_items = dedupe_lines(
            [resolve_open_loop_entry(item, round_id) for item in previous["active"]]
            + previous["resolved"]
        )
    else:
        active_items = dedupe_lines(
            previous["active"] + [f"[{round_id}][{decision}] {reason}" for reason in reasons]
        )
        resolved_items = previous["resolved"]
    content = render_open_loops(active=active_items, resolved=resolved_items)
    write_text(path, content)
    return path


def run_cycle(
    workspace: Path,
    round_id: str,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    candidate_repo: Path | None = None,
    candidate_patch: Path | None = None,
    patch_strip: int = 1,
    hypothesis_key: str | None = None,
    benchmark_command: str | None = None,
    apply_command: str | None = None,
    rollback_command: str | None = None,
    auto_apply_rollback: bool = False,
    candidate_report: Path | None = None,
    candidate_output_dir: Path | None = None,
    promote_label: str | None = None,
    sync_patterns_enabled: bool = False,
) -> dict[str, object]:
    baseline_report = resolve_baseline_report(workspace=workspace, label=baseline_label)
    candidate_root = resolve_candidate_repo(candidate_repo)
    if not candidate_root.exists():
        raise RuntimeError(f"candidate repo does not exist: {candidate_root}")
    if candidate_patch is not None:
        candidate_patch = candidate_patch.resolve()
    if candidate_patch is not None and apply_command is not None:
        raise RuntimeError("use either candidate_patch or apply_command, not both")
    initialized = iteration_init.initialize_round(
        workspace=workspace,
        round_id=round_id,
        objective=objective,
        baseline=baseline_label,
        owner=owner,
        candidate=candidate,
    )
    round_dir = Path(initialized["round_dir"])
    workspace_snapshots: dict[str, object] = {}
    apply_result: dict[str, object] | None = None
    rollback_result: dict[str, object] | None = None

    if candidate_repo is not None or apply_command is not None or rollback_command is not None or candidate_patch is not None:
        stage_name = "before-apply" if apply_command is not None or candidate_patch is not None else "before-eval"
        workspace_snapshots[stage_name] = capture_candidate_snapshot(
            round_dir=round_dir,
            candidate_root=candidate_root,
            stage=stage_name,
        )

    if candidate_patch is not None:
        apply_result = apply_patch_file(
            candidate_root=candidate_root,
            patch_path=candidate_patch,
            patch_strip=patch_strip,
        )
        workspace_snapshots["after-apply"] = capture_candidate_snapshot(
            round_dir=round_dir,
            candidate_root=candidate_root,
            stage="after-apply",
        )
    elif apply_command is not None:
        apply_result = run_command(apply_command, cwd=candidate_root)
        workspace_snapshots["after-apply"] = capture_candidate_snapshot(
            round_dir=round_dir,
            candidate_root=candidate_root,
            stage="after-apply",
        )

    if candidate_report is None:
        output_dir = candidate_output_dir or (workspace / "runs" / round_id)
        candidate_report = run_benchmarks(
            output_dir=output_dir,
            candidate_repo=candidate_root,
            benchmark_command=benchmark_command,
        )
    else:
        candidate_report = candidate_report.resolve()

    comparison = benchmark_compare.compare_results(
        baseline=baseline_registry.load_json(baseline_report),
        candidate=baseline_registry.load_json(candidate_report),
    )

    ledger_path = Path(initialized["ledger"])
    reflection_path = Path(initialized["reflection"])
    round_memory_path = Path(initialized["round_memory"])
    self_feedback_path = Path(initialized["self_feedback"])
    state_path = round_dir / "state.json"
    open_loops_path = update_open_loops(workspace=workspace, round_id=round_id, comparison=comparison)

    write_text(
        ledger_path,
        render_ledger(
            round_id=round_id,
            objective=objective,
            baseline_label=baseline_label,
            owner=owner,
            candidate=candidate,
            candidate_repo=candidate_repo,
            baseline_report=baseline_report,
            candidate_report=candidate_report,
            comparison=comparison,
        ),
    )
    write_text(reflection_path, render_reflection(candidate=candidate, comparison=comparison))
    write_text(
        round_memory_path,
        render_round_memory(
            round_id=round_id,
            objective=objective,
            baseline_label=baseline_label,
            owner=owner,
            candidate=candidate,
            comparison=comparison,
        ),
    )
    write_text(
        self_feedback_path,
        render_self_feedback(candidate=candidate, comparison=comparison),
    )
    context_chain_path = sync_context_chain(workspace=workspace)

    if (
        str(comparison.get("decision", "stop")) == "rollback"
        and auto_apply_rollback
    ):
        if rollback_command is not None:
            rollback_result = run_command(rollback_command, cwd=candidate_root)
        elif candidate_patch is not None:
            rollback_result = apply_patch_file(
                candidate_root=candidate_root,
                patch_path=candidate_patch,
                patch_strip=patch_strip,
                reverse=True,
            )
        if rollback_result is not None:
            workspace_snapshots["after-rollback"] = capture_candidate_snapshot(
                round_dir=round_dir,
                candidate_root=candidate_root,
                stage="after-rollback",
            )

    state = build_state(
        round_id=round_id,
        objective=objective,
        baseline_label=baseline_label,
        owner=owner,
        candidate=candidate,
        candidate_repo=candidate_root,
        candidate_patch=candidate_patch,
        patch_strip=patch_strip,
        hypothesis_key=hypothesis_key,
        benchmark_command=benchmark_command,
        apply_command=apply_command,
        rollback_command=rollback_command,
        auto_apply_rollback=auto_apply_rollback,
        baseline_report=baseline_report,
        candidate_report=candidate_report,
        comparison=comparison,
        round_memory_path=round_memory_path,
        self_feedback_path=self_feedback_path,
        context_chain_path=context_chain_path,
        workspace_snapshots=workspace_snapshots,
        apply_result=apply_result,
        rollback_result=rollback_result,
    )
    write_json(state_path, state)

    promotion_result: dict[str, object] | None = None
    if promote_label and bool(state.get("promotion_eligible")):
        promotion_result = baseline_promotion.promote_round(
            workspace=workspace,
            round_id=round_id,
            label=promote_label,
        )

    sync_result: dict[str, object] | None = None
    if sync_patterns_enabled:
        sync_result = pattern_sync.sync_patterns(workspace=workspace)

    return {
        "workspace": str(workspace),
        "round_dir": str(round_dir),
        "state": str(state_path),
        "ledger": str(ledger_path),
        "reflection": str(reflection_path),
        "round_memory": str(round_memory_path),
        "self_feedback": str(self_feedback_path),
        "memory_chain": str(context_chain_path),
        "open_loops": str(open_loops_path),
        "decision": comparison.get("decision"),
        "decision_reason": comparison.get("decision_reason", []),
        "promotion_eligible": bool(state.get("promotion_eligible")),
        "next_action": state.get("next_action"),
        "baseline_report": str(baseline_report),
        "candidate_report": str(candidate_report),
        "candidate_repo": str(candidate_root),
        "candidate_patch": str(candidate_patch) if candidate_patch is not None else None,
        "patch_strip": patch_strip,
        "hypothesis_key": hypothesis_key,
        "benchmark_command": benchmark_command,
        "apply_command": apply_command,
        "rollback_command": rollback_command,
        "auto_apply_rollback": auto_apply_rollback,
        "workspace_snapshots": workspace_snapshots,
        "apply_result": apply_result,
        "rollback_result": rollback_result,
        "promotion": promotion_result,
        "pattern_sync": sync_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one bounded-iteration cycle.")
    parser.add_argument("--workspace", default=".skill-iterations", help="Iteration workspace")
    parser.add_argument("--round-id", required=True, help="Round identifier")
    parser.add_argument("--objective", required=True, help="Round objective")
    parser.add_argument("--baseline-label", required=True, help="Registered baseline label")
    parser.add_argument("--owner", default="Technical Trinity", help="Lead owner")
    parser.add_argument("--candidate", default="<candidate-change>", help="Candidate change summary")
    parser.add_argument("--candidate-repo", dest="candidate_repo", help="Candidate repo or worktree root")
    parser.add_argument("--candidate-worktree", dest="candidate_repo", help="Alias for --candidate-repo")
    parser.add_argument("--candidate-patch", help="Patch file to apply inside the candidate workspace")
    parser.add_argument("--patch-strip", type=int, default=1, help="Strip count when applying candidate patch")
    parser.add_argument("--hypothesis-key", help="Stable key for same-hypothesis retry tracking")
    parser.add_argument("--benchmark-command", help="Command to generate benchmark-results.json, supports {output_dir}")
    parser.add_argument("--apply-command", help="Command to mutate the candidate workspace before benchmarking")
    parser.add_argument("--rollback-command", help="Command to restore the candidate workspace after a rollback decision")
    parser.add_argument("--auto-apply-rollback", action="store_true", help="Execute rollback-command automatically when the decision is rollback")
    parser.add_argument("--candidate-report", help="Existing candidate benchmark report")
    parser.add_argument("--candidate-output-dir", help="Output dir when running benchmarks automatically")
    parser.add_argument("--promote-label", help="Promote kept result to this baseline label")
    parser.add_argument("--sync-distilled-patterns", action="store_true", help="Rebuild distilled patterns after the round")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_cycle(
        workspace=Path(args.workspace).resolve(),
        round_id=args.round_id,
        objective=args.objective,
        baseline_label=args.baseline_label,
        owner=args.owner,
        candidate=args.candidate,
        candidate_repo=Path(args.candidate_repo).resolve() if args.candidate_repo else None,
        candidate_patch=Path(args.candidate_patch).resolve() if args.candidate_patch else None,
        patch_strip=args.patch_strip,
        hypothesis_key=args.hypothesis_key,
        benchmark_command=args.benchmark_command,
        apply_command=args.apply_command,
        rollback_command=args.rollback_command,
        auto_apply_rollback=args.auto_apply_rollback,
        candidate_report=Path(args.candidate_report).resolve() if args.candidate_report else None,
        candidate_output_dir=Path(args.candidate_output_dir).resolve()
        if args.candidate_output_dir
        else None,
        promote_label=args.promote_label,
        sync_patterns_enabled=args.sync_distilled_patterns,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
