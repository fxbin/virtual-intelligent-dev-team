#!/usr/bin/env python3
"""Run a capped multi-round bounded-iteration loop from a candidate plan."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re


SCRIPT_DIR = Path(__file__).resolve().parent
RUN_CYCLE_SCRIPT = SCRIPT_DIR / "run_iteration_cycle.py"
SYNC_SCRIPT = SCRIPT_DIR / "sync_distilled_patterns.py"
MATERIALIZE_PATCH_SCRIPT = SCRIPT_DIR / "materialize_candidate_patch.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


iteration_cycle = load_module("virtual_team_iteration_cycle_loop", RUN_CYCLE_SCRIPT)
pattern_sync = load_module("virtual_team_pattern_sync_loop", SYNC_SCRIPT)
candidate_materializer = load_module("virtual_team_candidate_materializer_loop", MATERIALIZE_PATCH_SCRIPT)


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return read_text(path)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def compute_plan_digest(plan: dict[str, object]) -> str:
    content = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def resolve_optional_path(value: object, base_dir: Path) -> Path | None:
    if not isinstance(value, str) or value.strip() == "":
        return None
    return resolve_path(value, base_dir)


def default_candidate_brief_path(base_dir: Path, round_id: str) -> Path:
    return (base_dir / "candidate-briefs" / f"{round_id}.json").resolve()


def default_candidate_patch_path(base_dir: Path, round_id: str) -> Path:
    return (base_dir / "patches" / f"{round_id}.patch").resolve()


def normalize_mutation_plan(value: object) -> dict[str, object] | None:
    return dict(value) if isinstance(value, dict) else None


def normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip() != ""]


def normalize_mutation_catalog(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, object]] = []
    for raw in value:
        if not isinstance(raw, dict):
            continue
        mutation_plan = normalize_mutation_plan(raw.get("mutation_plan"))
        if mutation_plan is None:
            operations = raw.get("operations")
            if isinstance(operations, list):
                mutation_plan = {
                    "mode": str(raw.get("mode", "patch")).strip() or "patch",
                    "operations": [dict(item) for item in operations if isinstance(item, dict)],
                }
        if mutation_plan is None:
            continue
        try:
            priority = int(raw.get("priority", 0))
        except (TypeError, ValueError):
            priority = 0
        items.append(
            {
                "id": str(raw.get("id", raw.get("name", "mutation-rule"))).strip() or "mutation-rule",
                "priority": priority,
                "when_any_keywords": normalize_string_list(raw.get("when_any_keywords")),
                "when_all_keywords": normalize_string_list(raw.get("when_all_keywords")),
                "when_no_keywords": normalize_string_list(raw.get("when_no_keywords")),
                "mutation_plan": mutation_plan,
            }
        )
    return items


def normalize_hypothesis_key(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "default-hypothesis"


def hypothesis_key_from_text(value: str) -> str:
    compact = " ".join(value.split())
    return normalize_hypothesis_key(compact[:120])


def render_command_template(template: str, round_id: str, round_number: int) -> str:
    return (
        template.replace("{round_id}", round_id)
        .replace("{round_number}", str(round_number))
    )


def render_runtime_template(template: str, values: dict[str, object]) -> str:
    normalized = {key: ("" if value is None else str(value)) for key, value in values.items()}
    return template.format(**normalized)


def render_template_object(value: object, values: dict[str, object]) -> object:
    if isinstance(value, str):
        return render_runtime_template(value, values)
    if isinstance(value, list):
        return [render_template_object(item, values) for item in value]
    if isinstance(value, dict):
        return {str(key): render_template_object(item, values) for key, item in value.items()}
    return value


def round_id_for_index(index: int) -> str:
    return f"round-{index:02d}"


def round_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("round-")
    try:
        return (int(suffix), path.name)
    except ValueError:
        return (10**9, path.name)


def loop_output_paths(workspace: Path, plan_path: Path) -> tuple[Path, Path]:
    loops_dir = workspace / "loops"
    return (
        loops_dir / f"{plan_path.stem}-state.json",
        loops_dir / f"{plan_path.stem}-summary.json",
    )


def normalize_round_entries(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def normalize_attempts(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    attempts: dict[str, int] = {}
    for key, raw in value.items():
        normalized = normalize_hypothesis_key(str(key))
        try:
            attempts[normalized] = max(int(raw), 0)
        except (TypeError, ValueError):
            continue
    return attempts


def normalize_nonnegative_int(value: object) -> int | None:
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return None
    if normalized < 0:
        return None
    return normalized


def decision_counts_from_rounds(rounds_run: list[dict[str, object]]) -> dict[str, int]:
    counts = {
        "keep": 0,
        "retry": 0,
        "rollback": 0,
        "stop": 0,
    }
    for item in rounds_run:
        if not isinstance(item, dict):
            continue
        decision = str(item.get("decision", "")).strip()
        if decision in counts:
            counts[decision] += 1
    return counts


def compute_consecutive_non_keep_rounds(rounds_run: list[dict[str, object]]) -> int:
    streak = 0
    for item in reversed(rounds_run):
        if not isinstance(item, dict):
            continue
        decision = str(item.get("decision", "")).strip()
        if decision in {"retry", "rollback"}:
            streak += 1
            continue
        break
    return streak


def load_existing_loop_progress(state_path: Path, summary_path: Path) -> dict[str, object] | None:
    for path in (state_path, summary_path):
        if not path.exists():
            continue
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return None


def build_loop_payload(
    workspace: Path,
    plan_path: Path,
    plan_digest: str,
    state_path: Path,
    summary_path: Path,
    started_at: str,
    owner: str,
    objective: str,
    baseline_label: str,
    active_baseline: str,
    autonomous_candidate_generation: bool,
    generated_rounds: int,
    max_same_hypothesis_retries: int,
    max_consecutive_non_keep_rounds: int | None,
    auto_pivot_on_stagnation: bool,
    hypothesis_attempts: dict[str, int],
    consecutive_non_keep_rounds: int,
    blocked_hypothesis_keys: set[str],
    pivot_count: int,
    pivot_history: list[dict[str, object]],
    pending_generation_reason: str | None,
    rounds_run: list[dict[str, object]],
    halt_reason: str,
    sync_result: dict[str, object] | None,
    status: str,
    resume_requested: bool,
    resumed_from_existing: bool,
) -> dict[str, object]:
    last_round_id = ""
    if rounds_run:
        last_round_id = str(rounds_run[-1].get("round_id", "")).strip()
    return {
        "workspace": str(workspace),
        "plan": str(plan_path),
        "plan_digest": plan_digest,
        "state": str(state_path),
        "summary": str(summary_path),
        "started_at": started_at,
        "updated_at": now_iso(),
        "status": status,
        "resume_requested": resume_requested,
        "resumed_from_existing": resumed_from_existing,
        "owner": owner,
        "objective": objective,
        "initial_baseline_label": baseline_label,
        "final_baseline_label": active_baseline,
        "autonomous_candidate_generation": autonomous_candidate_generation,
        "auto_generated_rounds": generated_rounds,
        "max_same_hypothesis_retries": max_same_hypothesis_retries,
        "max_consecutive_non_keep_rounds": max_consecutive_non_keep_rounds,
        "auto_pivot_on_stagnation": auto_pivot_on_stagnation,
        "hypothesis_attempts": hypothesis_attempts,
        "consecutive_non_keep_rounds": consecutive_non_keep_rounds,
        "blocked_hypothesis_keys": sorted(blocked_hypothesis_keys),
        "pivot_count": pivot_count,
        "pivot_history": pivot_history,
        "pending_generation_reason": pending_generation_reason,
        "decision_counts": decision_counts_from_rounds(rounds_run),
        "rounds_run": rounds_run,
        "round_count": len(rounds_run),
        "last_round_id": last_round_id or None,
        "next_round_number": len(rounds_run) + 1,
        "halt_reason": halt_reason,
        "pattern_sync": sync_result,
        "memory_chain": str(workspace / "iteration-context-chain.md"),
    }


def persist_loop_progress(
    workspace: Path,
    plan_path: Path,
    plan_digest: str,
    state_path: Path,
    summary_path: Path,
    started_at: str,
    owner: str,
    objective: str,
    baseline_label: str,
    active_baseline: str,
    autonomous_candidate_generation: bool,
    generated_rounds: int,
    max_same_hypothesis_retries: int,
    max_consecutive_non_keep_rounds: int | None,
    auto_pivot_on_stagnation: bool,
    hypothesis_attempts: dict[str, int],
    consecutive_non_keep_rounds: int,
    blocked_hypothesis_keys: set[str],
    pivot_count: int,
    pivot_history: list[dict[str, object]],
    pending_generation_reason: str | None,
    rounds_run: list[dict[str, object]],
    halt_reason: str,
    sync_result: dict[str, object] | None,
    status: str,
    resume_requested: bool,
    resumed_from_existing: bool,
) -> dict[str, object]:
    payload = build_loop_payload(
        workspace=workspace,
        plan_path=plan_path,
        plan_digest=plan_digest,
        state_path=state_path,
        summary_path=summary_path,
        started_at=started_at,
        owner=owner,
        objective=objective,
        baseline_label=baseline_label,
        active_baseline=active_baseline,
        autonomous_candidate_generation=autonomous_candidate_generation,
        generated_rounds=generated_rounds,
        max_same_hypothesis_retries=max_same_hypothesis_retries,
        max_consecutive_non_keep_rounds=max_consecutive_non_keep_rounds,
        auto_pivot_on_stagnation=auto_pivot_on_stagnation,
        hypothesis_attempts=hypothesis_attempts,
        consecutive_non_keep_rounds=consecutive_non_keep_rounds,
        blocked_hypothesis_keys=blocked_hypothesis_keys,
        pivot_count=pivot_count,
        pivot_history=pivot_history,
        pending_generation_reason=pending_generation_reason,
        rounds_run=rounds_run,
        halt_reason=halt_reason,
        sync_result=sync_result,
        status=status,
        resume_requested=resume_requested,
        resumed_from_existing=resumed_from_existing,
    )
    write_json(state_path, payload)
    if status == "completed":
        write_json(summary_path, payload)
    return payload


def extract_actionable_lines(content: str) -> list[str]:
    ignored = {
        "none",
        "none.",
        "none yet.",
        "no hard regressions observed",
        "no durable positive signal recorded yet",
        "no decision reason recorded",
    }
    ignored_prefixes = (
        "Round ID:",
        "Owner:",
        "Objective:",
        "Baseline:",
        "Candidate:",
        "Overall result:",
        "Key deltas:",
    )
    lines: list[str] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line.startswith("-"):
            continue
        text = line.lstrip("-").strip()
        if text.startswith("[") and "]" in text:
            text = text.split("]", 1)[1].strip()
        normalized = " ".join(text.split())
        if normalized == "":
            continue
        if normalized.lower() in ignored:
            continue
        if normalized.startswith(ignored_prefixes):
            continue
        lines.append(normalized)
    return lines


def collect_focus_candidates(
    workspace: Path,
    last_result: dict[str, object] | None,
    objective: str,
) -> list[str]:
    sources = [
        read_if_exists(workspace / "open-loops.md"),
        read_if_exists(workspace / "iteration-context-chain.md"),
        read_if_exists(workspace / "distilled-patterns.md"),
    ]
    latest_state = latest_round_state(workspace)
    latest_round_id = str(latest_state.get("round_id", "")).strip()
    if latest_round_id:
        sources.insert(1, read_if_exists(workspace / latest_round_id / "self-feedback.md"))
        sources.insert(2, read_if_exists(workspace / latest_round_id / "round-memory.md"))

    candidates: list[str] = []
    seen: set[str] = set()

    def append_candidate(raw: str) -> None:
        normalized = " ".join(raw.split())
        if normalized == "" or normalized in seen:
            return
        seen.add(normalized)
        candidates.append(normalized[:180])

    for content in sources:
        for line in extract_actionable_lines(content):
            append_candidate(line)

    if isinstance(last_result, dict):
        reasons = last_result.get("decision_reason", [])
        if isinstance(reasons, list):
            for reason in reasons:
                append_candidate(str(reason))

    append_candidate(objective)
    return candidates


def latest_round_state(workspace: Path) -> dict[str, object]:
    round_dirs = sorted((path for path in workspace.glob("round-*") if path.is_dir()), key=round_sort_key)
    for round_dir in reversed(round_dirs):
        state_path = round_dir / "state.json"
        if state_path.exists():
            return load_json(state_path)
    return {}


def build_generated_path(template: str, round_id: str, round_number: int, base_dir: Path) -> Path:
    rendered = template.format(round_id=round_id, round_number=round_number)
    return resolve_path(rendered, base_dir)


def build_template_values(
    *,
    workspace: Path,
    plan_path: Path,
    round_id: str,
    round_number: int,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    hypothesis_key: str,
    candidate_repo: Path | None,
    candidate_patch: Path | None,
    candidate_output_dir: Path | None,
    candidate_brief: Path | None,
) -> dict[str, object]:
    return {
        "workspace": workspace,
        "plan": plan_path,
        "round_id": round_id,
        "round_number": round_number,
        "objective": objective,
        "baseline_label": baseline_label,
        "owner": owner,
        "candidate": candidate,
        "hypothesis_key": hypothesis_key,
        "candidate_repo": candidate_repo,
        "candidate_patch": candidate_patch,
        "candidate_output_dir": candidate_output_dir,
        "candidate_brief": candidate_brief,
    }


def build_mutation_template_values(
    *,
    workspace: Path,
    plan_path: Path,
    round_id: str,
    round_number: int,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    focus: str,
    hypothesis_key: str,
    candidate_repo: Path | None,
    candidate_patch: Path | None,
    candidate_output_dir: Path | None,
    candidate_brief: Path | None,
    last_decision: str | None,
    last_decision_reason: str | None,
    generation_reason: str | None,
) -> dict[str, object]:
    values = build_template_values(
        workspace=workspace,
        plan_path=plan_path,
        round_id=round_id,
        round_number=round_number,
        objective=objective,
        baseline_label=baseline_label,
        owner=owner,
        candidate=candidate,
        hypothesis_key=hypothesis_key,
        candidate_repo=candidate_repo,
        candidate_patch=candidate_patch,
        candidate_output_dir=candidate_output_dir,
        candidate_brief=candidate_brief,
    )
    values.update(
        {
            "focus": focus,
            "last_decision": last_decision,
            "last_decision_reason": last_decision_reason,
            "generation_reason": generation_reason,
        }
    )
    return values


def render_materialize_command(
    template: str | None,
    *,
    workspace: Path,
    plan_path: Path,
    round_id: str,
    round_number: int,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    hypothesis_key: str,
    candidate_repo: Path | None,
    candidate_patch: Path | None,
    candidate_output_dir: Path | None,
    candidate_brief: Path | None,
) -> str | None:
    if not template:
        return None
    return render_runtime_template(
        template,
        build_template_values(
            workspace=workspace,
            plan_path=plan_path,
            round_id=round_id,
            round_number=round_number,
            objective=objective,
            baseline_label=baseline_label,
            owner=owner,
            candidate=candidate,
            hypothesis_key=hypothesis_key,
            candidate_repo=candidate_repo,
            candidate_patch=candidate_patch,
            candidate_output_dir=candidate_output_dir,
            candidate_brief=candidate_brief,
        ),
    )


def build_candidate_item(
    item: dict[str, object],
    index: int,
    default_owner: str,
    objective: str,
    baseline_label: str,
    workspace: Path,
    plan_path: Path,
    base_dir: Path,
    candidate_repo_template: str | None,
    candidate_patch_template: str | None,
    candidate_brief_template: str | None,
    candidate_output_dir_template: str | None,
    benchmark_command_template: str | None,
    apply_command_template: str | None,
    rollback_command_template: str | None,
    materialize_command_template: str | None,
    default_auto_apply_rollback: bool,
    default_patch_strip: int,
) -> dict[str, object]:
    round_id = str(item.get("round_id", round_id_for_index(index)))
    candidate_repo_value = item.get("candidate_repo", item.get("candidate_worktree"))
    candidate_patch_value = item.get("candidate_patch")
    candidate_brief_value = item.get("candidate_brief")
    candidate_output_dir_value = item.get("candidate_output_dir")
    candidate_repo = resolve_optional_path(candidate_repo_value, base_dir)
    if candidate_repo is None and candidate_repo_template:
        candidate_repo = build_generated_path(
            candidate_repo_template,
            round_id=round_id,
            round_number=index,
            base_dir=base_dir,
        )
    candidate_patch = resolve_optional_path(candidate_patch_value, base_dir)
    if candidate_patch is None and candidate_patch_template:
        candidate_patch = build_generated_path(
            candidate_patch_template,
            round_id=round_id,
            round_number=index,
            base_dir=base_dir,
        )
    candidate_brief = resolve_optional_path(candidate_brief_value, base_dir)
    if candidate_brief is None and candidate_brief_template:
        candidate_brief = build_generated_path(
            candidate_brief_template,
            round_id=round_id,
            round_number=index,
            base_dir=base_dir,
        )
    candidate_output_dir = resolve_optional_path(candidate_output_dir_value, base_dir)
    if candidate_output_dir is None and candidate_output_dir_template:
        candidate_output_dir = build_generated_path(
            candidate_output_dir_template,
            round_id=round_id,
            round_number=index,
            base_dir=base_dir,
        )
    benchmark_command = str(item.get("benchmark_command", "")).strip() or None
    if benchmark_command is None and benchmark_command_template:
        benchmark_command = render_command_template(
            benchmark_command_template,
            round_id=round_id,
            round_number=index,
        )
    apply_command = str(item.get("apply_command", "")).strip() or None
    if apply_command is None and apply_command_template:
        apply_command = render_command_template(
            apply_command_template,
            round_id=round_id,
            round_number=index,
        )
    rollback_command = str(item.get("rollback_command", "")).strip() or None
    if rollback_command is None and rollback_command_template:
        rollback_command = render_command_template(
            rollback_command_template,
            round_id=round_id,
            round_number=index,
        )
    candidate = str(item.get("candidate", "<candidate-change>")).strip() or "<candidate-change>"
    owner = str(item.get("owner", default_owner)).strip() or default_owner
    hypothesis_key = normalize_hypothesis_key(
        str(item.get("hypothesis_key", hypothesis_key_from_text(str(item.get("candidate", round_id)))))
    )
    if candidate_brief is None and (
        materialize_command_template or str(item.get("materialize_command", "")).strip()
    ):
        candidate_brief = default_candidate_brief_path(base_dir=base_dir, round_id=round_id)
    materialize_command = str(item.get("materialize_command", "")).strip() or None
    if materialize_command is None and materialize_command_template:
        materialize_command = render_materialize_command(
            materialize_command_template,
            workspace=workspace,
            plan_path=plan_path,
            round_id=round_id,
            round_number=index,
            objective=objective,
            baseline_label=baseline_label,
            owner=owner,
            candidate=candidate,
            hypothesis_key=hypothesis_key,
            candidate_repo=candidate_repo,
            candidate_patch=candidate_patch,
            candidate_output_dir=candidate_output_dir,
            candidate_brief=candidate_brief,
        )
    mutation_plan = normalize_mutation_plan(item.get("mutation_plan"))
    return {
        "round_id": round_id,
        "candidate": candidate,
        "owner": owner,
        "hypothesis_key": hypothesis_key,
        "benchmark_command": benchmark_command,
        "apply_command": apply_command,
        "rollback_command": rollback_command,
        "materialize_command": materialize_command,
        "mutation_plan": mutation_plan,
        "mutation_plan_source": "explicit" if mutation_plan is not None else None,
        "mutation_focus": None,
        "auto_apply_rollback": bool(item.get("auto_apply_rollback", default_auto_apply_rollback)),
        "candidate_patch": candidate_patch,
        "candidate_brief": candidate_brief,
        "patch_strip": max(int(item.get("patch_strip", default_patch_strip)), 0),
        "candidate_report": resolve_optional_path(item.get("candidate_report"), base_dir),
        "candidate_output_dir": candidate_output_dir,
        "candidate_repo": candidate_repo,
        "promote_label": str(item.get("promote_label", f"accepted-{round_id}")).strip()
        or f"accepted-{round_id}",
    }


def choose_focus_text(
    workspace: Path,
    last_result: dict[str, object] | None,
    objective: str,
    blocked_hypothesis_keys: set[str] | None = None,
    allow_blocked_fallback: bool = True,
) -> str | None:
    blocked = {
        normalize_hypothesis_key(str(item))
        for item in (blocked_hypothesis_keys or set())
        if str(item).strip() != ""
    }
    first_candidate: str | None = None
    for candidate in collect_focus_candidates(workspace=workspace, last_result=last_result, objective=objective):
        if first_candidate is None:
            first_candidate = candidate
        if hypothesis_key_from_text(candidate) in blocked:
            continue
        return candidate
    if allow_blocked_fallback:
        return first_candidate or objective
    return None


def generation_sources(workspace: Path, last_round_id: str) -> list[str]:
    candidates = [
        workspace / "iteration-context-chain.md",
        workspace / "open-loops.md",
        workspace / "distilled-patterns.md",
    ]
    if last_round_id != "":
        candidates.extend(
            [
                workspace / last_round_id / "round-memory.md",
                workspace / last_round_id / "self-feedback.md",
            ]
        )
    return [str(path) for path in candidates if path.exists()]


def score_mutation_catalog_rule(rule: dict[str, object], haystack: str) -> tuple[int, int, int] | None:
    any_keywords = [keyword.lower() for keyword in normalize_string_list(rule.get("when_any_keywords"))]
    all_keywords = [keyword.lower() for keyword in normalize_string_list(rule.get("when_all_keywords"))]
    no_keywords = [keyword.lower() for keyword in normalize_string_list(rule.get("when_no_keywords"))]

    if any(keyword in haystack for keyword in no_keywords):
        return None
    if any_keywords:
        any_matches = sum(1 for keyword in any_keywords if keyword in haystack)
        if any_matches == 0:
            return None
    else:
        any_matches = 0
    all_matches = sum(1 for keyword in all_keywords if keyword in haystack)
    if all_keywords and all_matches != len(all_keywords):
        return None

    try:
        priority = int(rule.get("priority", 0))
    except (TypeError, ValueError):
        priority = 0
    return (priority, all_matches, any_matches)


def synthesize_mutation_plan_from_catalog(
    catalog: list[dict[str, object]],
    *,
    workspace: Path,
    plan_path: Path,
    round_id: str,
    round_number: int,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    focus: str,
    hypothesis_key: str,
    candidate_repo: Path | None,
    candidate_patch: Path | None,
    candidate_output_dir: Path | None,
    candidate_brief: Path | None,
    generation_reason: str | None,
    last_result: dict[str, object] | None,
) -> tuple[dict[str, object] | None, str | None]:
    latest_state = latest_round_state(workspace)
    last_decision = str((last_result or {}).get("decision", latest_state.get("decision", ""))).strip() or None
    last_reasons = (last_result or {}).get("decision_reason", latest_state.get("decision_reason", []))
    if not isinstance(last_reasons, list):
        last_reasons = []
    last_reason_text = "; ".join(str(reason) for reason in last_reasons if str(reason).strip() != "")
    open_loops = read_if_exists(workspace / "open-loops.md")
    context_chain = read_if_exists(workspace / "iteration-context-chain.md")
    distilled_patterns = read_if_exists(workspace / "distilled-patterns.md")
    haystack = " ".join(
        part.strip().lower()
        for part in [
            candidate,
            focus,
            objective,
            generation_reason or "",
            last_decision or "",
            last_reason_text,
            open_loops,
            context_chain,
            distilled_patterns,
        ]
        if part.strip() != ""
    )
    best_rule: dict[str, object] | None = None
    best_score: tuple[int, int, int] | None = None
    for rule in catalog:
        score = score_mutation_catalog_rule(rule, haystack)
        if score is None:
            continue
        if best_score is None or score > best_score:
            best_rule = rule
            best_score = score
    if best_rule is None:
        return None, None

    values = build_mutation_template_values(
        workspace=workspace,
        plan_path=plan_path,
        round_id=round_id,
        round_number=round_number,
        objective=objective,
        baseline_label=baseline_label,
        owner=owner,
        candidate=candidate,
        focus=focus,
        hypothesis_key=hypothesis_key,
        candidate_repo=candidate_repo,
        candidate_patch=candidate_patch,
        candidate_output_dir=candidate_output_dir,
        candidate_brief=candidate_brief,
        last_decision=last_decision,
        last_decision_reason=last_reason_text or None,
        generation_reason=generation_reason,
    )
    mutation_plan = render_template_object(best_rule["mutation_plan"], values)
    if not isinstance(mutation_plan, dict):
        raise RuntimeError("rendered mutation plan must be a JSON object")
    return mutation_plan, str(best_rule.get("id", "mutation-rule"))


def build_candidate_brief_payload(
    *,
    workspace: Path,
    plan_path: Path,
    round_id: str,
    round_number: int,
    objective: str,
    baseline_label: str,
    owner: str,
    candidate: str,
    candidate_source: str,
    hypothesis_key: str,
    candidate_repo: Path | None,
    candidate_patch: Path | None,
    candidate_brief: Path | None,
    candidate_output_dir: Path | None,
    candidate_report: Path | None,
    benchmark_command: str | None,
    apply_command: str | None,
    rollback_command: str | None,
    materialize_command: str | None,
    mutation_plan: dict[str, object] | None,
    mutation_plan_source: str | None,
    mutation_focus: str | None,
    auto_apply_rollback: bool,
    patch_strip: int,
    prior_attempts: int,
    generated_from: list[str] | None,
    generation_reason: str | None,
    last_result: dict[str, object] | None,
) -> dict[str, object]:
    latest_state = latest_round_state(workspace)
    last_round_id = str(latest_state.get("round_id", "")).strip()
    last_decision = str((last_result or {}).get("decision", latest_state.get("decision", ""))).strip() or None
    last_reasons = (last_result or {}).get("decision_reason", latest_state.get("decision_reason", []))
    if not isinstance(last_reasons, list):
        last_reasons = []
    return {
        "workspace": str(workspace),
        "plan": str(plan_path),
        "round_id": round_id,
        "round_number": round_number,
        "objective": objective,
        "baseline_label": baseline_label,
        "owner": owner,
        "candidate": candidate,
        "candidate_source": candidate_source,
        "hypothesis_key": hypothesis_key,
        "candidate_repo": str(candidate_repo) if candidate_repo is not None else None,
        "candidate_patch": str(candidate_patch) if candidate_patch is not None else None,
        "candidate_brief": str(candidate_brief) if candidate_brief is not None else None,
        "candidate_output_dir": str(candidate_output_dir) if candidate_output_dir is not None else None,
        "candidate_report": str(candidate_report) if candidate_report is not None else None,
        "benchmark_command": benchmark_command,
        "apply_command": apply_command,
        "rollback_command": rollback_command,
        "materialize_command": materialize_command,
        "mutation_plan": mutation_plan,
        "mutation_plan_source": mutation_plan_source,
        "mutation_focus": mutation_focus,
        "auto_apply_rollback": auto_apply_rollback,
        "patch_strip": patch_strip,
        "prior_attempts": prior_attempts,
        "iteration_context_chain": str(workspace / "iteration-context-chain.md"),
        "open_loops": str(workspace / "open-loops.md"),
        "distilled_patterns": str(workspace / "distilled-patterns.md"),
        "last_round_id": last_round_id or None,
        "last_decision": last_decision,
        "last_decision_reason": [str(reason) for reason in last_reasons],
        "generated_from": generated_from or [],
        "generation_reason": generation_reason,
    }


def synthesize_candidate(
    workspace: Path,
    round_number: int,
    objective: str,
    baseline_label: str,
    owner: str,
    last_result: dict[str, object] | None,
    plan_path: Path,
    base_dir: Path,
    candidate_repo_template: str | None,
    candidate_patch_template: str | None,
    candidate_brief_template: str | None,
    candidate_output_dir_template: str | None,
    benchmark_command_template: str | None,
    apply_command_template: str | None,
    rollback_command_template: str | None,
    materialize_command_template: str | None,
    default_auto_apply_rollback: bool,
    default_patch_strip: int,
    blocked_hypothesis_keys: set[str] | None = None,
    pivot_reason: str | None = None,
) -> tuple[dict[str, object] | None, str]:
    round_id = round_id_for_index(round_number)
    latest_state = latest_round_state(workspace)
    last_round_id = str(latest_state.get("round_id", "")).strip()
    decision = str((last_result or {}).get("decision", latest_state.get("decision", ""))).strip()
    blocked = {
        normalize_hypothesis_key(str(item))
        for item in (blocked_hypothesis_keys or set())
        if str(item).strip() != ""
    }
    focus = choose_focus_text(
        workspace=workspace,
        last_result=last_result,
        objective=objective,
        blocked_hypothesis_keys=blocked,
        allow_blocked_fallback=len(blocked) == 0,
    )

    if focus is None or str(focus).strip() == "":
        return None, "no unblocked focus remains for another autonomous round"
    if decision == "stop" and pivot_reason is None:
        return None, "last round already reached stop"
    if pivot_reason is not None:
        candidate = f"pivot to the next bottleneck and test a fresh evidence-backed hypothesis for {focus}"
        generation_reason = pivot_reason
    elif decision == "rollback":
        candidate = f"narrow the change and remove the regression around {focus}"
        generation_reason = decision or "bootstrap"
    elif decision == "retry":
        candidate = f"change one execution variable and collect stronger evidence for {focus}"
        generation_reason = decision or "bootstrap"
    elif decision == "keep":
        candidate = f"build on the accepted baseline and optimize the next bottleneck: {focus}"
        generation_reason = decision or "bootstrap"
    else:
        candidate = f"establish the first evidence-backed optimization hypothesis for {focus}"
        generation_reason = decision or "bootstrap"

    candidate_repo = None
    if candidate_repo_template:
        candidate_repo = build_generated_path(
            candidate_repo_template,
            round_id=round_id,
            round_number=round_number,
            base_dir=base_dir,
        )
    candidate_patch = None
    if candidate_patch_template:
        candidate_patch = build_generated_path(
            candidate_patch_template,
            round_id=round_id,
            round_number=round_number,
            base_dir=base_dir,
        )
    candidate_output_dir = None
    if candidate_output_dir_template:
        candidate_output_dir = build_generated_path(
            candidate_output_dir_template,
            round_id=round_id,
            round_number=round_number,
            base_dir=base_dir,
        )
    candidate_brief = None
    if candidate_brief_template:
        candidate_brief = build_generated_path(
            candidate_brief_template,
            round_id=round_id,
            round_number=round_number,
            base_dir=base_dir,
        )
    hypothesis_key = hypothesis_key_from_text(focus)
    if candidate_brief is None and materialize_command_template:
        candidate_brief = default_candidate_brief_path(base_dir=base_dir, round_id=round_id)
    materialize_command = render_materialize_command(
        materialize_command_template,
        workspace=workspace,
        plan_path=plan_path,
        round_id=round_id,
        round_number=round_number,
        objective=objective,
        baseline_label=baseline_label,
        owner=owner,
        candidate=candidate,
        hypothesis_key=hypothesis_key,
        candidate_repo=candidate_repo,
        candidate_patch=candidate_patch,
        candidate_output_dir=candidate_output_dir,
        candidate_brief=candidate_brief,
    )

    return (
        {
            "round_id": round_id,
            "candidate": candidate,
            "owner": owner,
            "hypothesis_key": hypothesis_key,
            "benchmark_command": render_command_template(
                benchmark_command_template,
                round_id=round_id,
                round_number=round_number,
            )
            if benchmark_command_template
            else None,
            "apply_command": render_command_template(
                apply_command_template,
                round_id=round_id,
                round_number=round_number,
            )
            if apply_command_template
            else None,
            "rollback_command": render_command_template(
                rollback_command_template,
                round_id=round_id,
                round_number=round_number,
            )
            if rollback_command_template
            else None,
            "materialize_command": materialize_command,
            "mutation_plan": None,
            "mutation_plan_source": None,
            "mutation_focus": focus,
            "auto_apply_rollback": default_auto_apply_rollback,
            "candidate_patch": candidate_patch,
            "candidate_brief": candidate_brief,
            "patch_strip": default_patch_strip,
            "candidate_repo": candidate_repo,
            "candidate_output_dir": candidate_output_dir,
            "candidate_report": None,
            "promote_label": f"accepted-{round_id}",
            "generated_from": generation_sources(workspace, last_round_id),
            "generation_reason": generation_reason,
        },
        "",
    )


def load_hypothesis_attempts(workspace: Path) -> dict[str, int]:
    attempts: dict[str, int] = {}
    round_dirs = sorted((path for path in workspace.glob("round-*") if path.is_dir()), key=round_sort_key)
    for round_dir in round_dirs:
        state_path = round_dir / "state.json"
        if not state_path.exists():
            continue
        state = load_json(state_path)
        decision = str(state.get("decision", "")).strip()
        if decision not in {"retry", "rollback"}:
            continue
        hypothesis_key = str(state.get("hypothesis_key", "")).strip()
        if hypothesis_key == "":
            candidate = str(state.get("candidate", round_dir.name))
            hypothesis_key = hypothesis_key_from_text(candidate)
        normalized = normalize_hypothesis_key(hypothesis_key)
        attempts[normalized] = attempts.get(normalized, 0) + 1
    return attempts


def run_loop(workspace: Path, plan_path: Path, resume: bool = False) -> dict[str, object]:
    plan = load_json(plan_path)
    current_plan_digest = compute_plan_digest(plan)
    base_dir = plan_path.parent
    objective = str(plan.get("objective", "")).strip()
    baseline_label = str(plan.get("baseline_label", "")).strip()
    owner = str(plan.get("owner", "Technical Trinity")).strip() or "Technical Trinity"
    if objective == "" or baseline_label == "":
        raise RuntimeError("plan must include objective and baseline_label")

    loop_policy = plan.get("loop_policy", {})
    if not isinstance(loop_policy, dict):
        loop_policy = {}
    max_rounds = max(int(loop_policy.get("max_rounds", 3)), 1)
    advance_baseline_on_keep = bool(loop_policy.get("advance_baseline_on_keep", True))
    sync_patterns_at_end = bool(loop_policy.get("sync_patterns_at_end", True))
    max_same_hypothesis_retries = max(int(loop_policy.get("max_same_hypothesis_retries", 2)), 1)
    max_consecutive_non_keep_rounds = normalize_nonnegative_int(
        loop_policy.get("max_consecutive_non_keep_rounds", 0)
    )
    if max_consecutive_non_keep_rounds == 0:
        max_consecutive_non_keep_rounds = None
    auto_pivot_on_stagnation = bool(loop_policy.get("auto_pivot_on_stagnation", False))
    halt_on_decisions = loop_policy.get("halt_on_decisions", ["stop"])
    if not isinstance(halt_on_decisions, list):
        halt_on_decisions = ["stop"]
    autonomous_candidate_generation = bool(
        plan.get(
            "autonomous_candidate_generation",
            loop_policy.get("autonomous_candidate_generation", False),
        )
    )
    candidate_repo_template = str(
        plan.get("candidate_repo_template", plan.get("candidate_worktree_template", ""))
    ).strip() or None
    candidate_patch_template = str(plan.get("candidate_patch_template", "")).strip() or None
    candidate_brief_template = str(plan.get("candidate_brief_template", "")).strip() or None
    candidate_output_dir_template = str(plan.get("candidate_output_dir_template", "")).strip() or None
    benchmark_command_template = str(plan.get("benchmark_command_template", "")).strip() or None
    apply_command_template = str(plan.get("apply_command_template", "")).strip() or None
    rollback_command_template = str(plan.get("rollback_command_template", "")).strip() or None
    materialize_command_template = str(plan.get("materialize_command_template", "")).strip() or None
    mutation_catalog = normalize_mutation_catalog(plan.get("mutation_catalog"))
    default_auto_apply_rollback = bool(plan.get("auto_apply_rollback", False))
    default_patch_strip = max(int(plan.get("patch_strip", 1)), 0)

    candidates = plan.get("candidates", [])
    if not isinstance(candidates, list):
        candidates = []
    if len([item for item in candidates if isinstance(item, dict)]) == 0 and not autonomous_candidate_generation:
        raise RuntimeError("plan must include at least one candidate unless autonomous_candidate_generation is enabled")

    state_path, summary_path = loop_output_paths(workspace=workspace, plan_path=plan_path)
    rounds_run: list[dict[str, object]] = []
    active_baseline = baseline_label
    halt_reason = "candidate list exhausted"
    generated_rounds = 0
    last_result: dict[str, object] | None = None
    round_number = 1
    hypothesis_attempts = load_hypothesis_attempts(workspace)
    consecutive_non_keep_rounds = 0
    blocked_hypothesis_keys: set[str] = set()
    pivot_count = 0
    pivot_history: list[dict[str, object]] = []
    pending_generation_reason: str | None = None
    started_at = now_iso()
    resumed_from_existing = False

    if resume:
        existing = load_existing_loop_progress(state_path=state_path, summary_path=summary_path)
        if existing is not None:
            recorded_plan = str(existing.get("plan", "")).strip()
            if recorded_plan != "" and Path(recorded_plan).resolve() != plan_path.resolve():
                raise RuntimeError("resume state does not match the requested plan")
            recorded_digest = str(existing.get("plan_digest", "")).strip()
            if recorded_digest != "" and recorded_digest != current_plan_digest:
                raise RuntimeError("resume state does not match the current plan content")
            existing_status = str(existing.get("status", "")).strip()
            if existing_status == "completed":
                completed = dict(existing)
                completed["resume_requested"] = True
                completed["resumed_from_existing"] = True
                completed["state"] = str(state_path)
                completed["summary"] = str(summary_path)
                return completed
            rounds_run = normalize_round_entries(existing.get("rounds_run"))
            active_baseline = str(
                existing.get("final_baseline_label", existing.get("initial_baseline_label", baseline_label))
            ).strip() or baseline_label
            generated_rounds = max(int(existing.get("auto_generated_rounds", 0)), 0)
            hypothesis_attempts = normalize_attempts(existing.get("hypothesis_attempts")) or hypothesis_attempts
            consecutive_non_keep_rounds = normalize_nonnegative_int(existing.get("consecutive_non_keep_rounds"))
            if consecutive_non_keep_rounds is None:
                consecutive_non_keep_rounds = compute_consecutive_non_keep_rounds(rounds_run)
            blocked_hypothesis_keys = {
                normalize_hypothesis_key(item)
                for item in normalize_string_list(existing.get("blocked_hypothesis_keys"))
            }
            pivot_count = max(int(existing.get("pivot_count", 0)), 0)
            pivot_history = normalize_round_entries(existing.get("pivot_history"))
            pending_generation_reason = str(existing.get("pending_generation_reason", "")).strip() or None
            started_at = str(existing.get("started_at", started_at)).strip() or started_at
            last_result = rounds_run[-1] if rounds_run else None
            round_number = len(rounds_run) + 1
            resumed_from_existing = len(rounds_run) > 0 or existing_status == "running"

    while round_number <= max_rounds:
        source = "plan"
        if round_number <= len(candidates) and isinstance(candidates[round_number - 1], dict):
            candidate_item = build_candidate_item(
                candidates[round_number - 1],
                index=round_number,
                default_owner=owner,
                objective=objective,
                baseline_label=active_baseline,
                workspace=workspace,
                plan_path=plan_path,
                base_dir=base_dir,
                candidate_repo_template=candidate_repo_template,
                candidate_patch_template=candidate_patch_template,
                candidate_brief_template=candidate_brief_template,
                candidate_output_dir_template=candidate_output_dir_template,
                benchmark_command_template=benchmark_command_template,
                apply_command_template=apply_command_template,
                rollback_command_template=rollback_command_template,
                materialize_command_template=materialize_command_template,
                default_auto_apply_rollback=default_auto_apply_rollback,
                default_patch_strip=default_patch_strip,
            )
        elif autonomous_candidate_generation:
            candidate_item, stop_reason = synthesize_candidate(
                workspace=workspace,
                round_number=round_number,
                objective=objective,
                baseline_label=active_baseline,
                owner=owner,
                last_result=last_result,
                plan_path=plan_path,
                base_dir=base_dir,
                candidate_repo_template=candidate_repo_template,
                candidate_patch_template=candidate_patch_template,
                candidate_brief_template=candidate_brief_template,
                candidate_output_dir_template=candidate_output_dir_template,
                benchmark_command_template=benchmark_command_template,
                apply_command_template=apply_command_template,
                rollback_command_template=rollback_command_template,
                materialize_command_template=materialize_command_template,
                default_auto_apply_rollback=default_auto_apply_rollback,
                default_patch_strip=default_patch_strip,
                blocked_hypothesis_keys=blocked_hypothesis_keys,
                pivot_reason=pending_generation_reason,
            )
            if candidate_item is None:
                halt_reason = f"autonomous candidate generation stopped: {stop_reason}"
                break
            source = "auto-generated"
            generated_rounds += 1
            pending_generation_reason = None
        else:
            halt_reason = "candidate list exhausted"
            break

        while True:
            round_id = str(candidate_item["round_id"])
            candidate = str(candidate_item["candidate"])
            round_owner = str(candidate_item["owner"]).strip() or owner
            hypothesis_key = normalize_hypothesis_key(str(candidate_item["hypothesis_key"]))
            prior_attempts = hypothesis_attempts.get(hypothesis_key, 0)
            if prior_attempts < max_same_hypothesis_retries:
                break
            if not (source == "auto-generated" and auto_pivot_on_stagnation):
                halt_reason = f"same hypothesis retry budget exhausted: {hypothesis_key}"
                candidate_item = None
                break
            blocked_hypothesis_keys.add(hypothesis_key)
            pivot_count += 1
            pivot_reason = f"pivot after same hypothesis retry budget exhausted: {hypothesis_key}"
            pivot_history.append(
                {
                    "type": "same-hypothesis-budget",
                    "round_number": round_number,
                    "blocked_hypothesis_key": hypothesis_key,
                    "from_candidate": candidate,
                    "from_focus": str(candidate_item.get("mutation_focus", "")).strip() or None,
                    "reason": pivot_reason,
                }
            )
            candidate_item, stop_reason = synthesize_candidate(
                workspace=workspace,
                round_number=round_number,
                objective=objective,
                baseline_label=active_baseline,
                owner=owner,
                last_result=last_result,
                plan_path=plan_path,
                base_dir=base_dir,
                candidate_repo_template=candidate_repo_template,
                candidate_patch_template=candidate_patch_template,
                candidate_brief_template=candidate_brief_template,
                candidate_output_dir_template=candidate_output_dir_template,
                benchmark_command_template=benchmark_command_template,
                apply_command_template=apply_command_template,
                rollback_command_template=rollback_command_template,
                materialize_command_template=materialize_command_template,
                default_auto_apply_rollback=default_auto_apply_rollback,
                default_patch_strip=default_patch_strip,
                blocked_hypothesis_keys=blocked_hypothesis_keys,
                pivot_reason=pivot_reason,
            )
            if candidate_item is None:
                halt_reason = f"autonomous candidate generation stopped: {stop_reason}"
                break
        if candidate_item is None:
            break
        promote_label = str(candidate_item["promote_label"])
        mutation_focus = str(candidate_item.get("mutation_focus", "")).strip() or choose_focus_text(
            workspace=workspace,
            last_result=last_result,
            objective=objective,
        )
        if candidate_item.get("mutation_plan") is None and mutation_catalog:
            mutation_plan, rule_id = synthesize_mutation_plan_from_catalog(
                mutation_catalog,
                workspace=workspace,
                plan_path=plan_path,
                round_id=round_id,
                round_number=round_number,
                objective=objective,
                baseline_label=active_baseline,
                owner=round_owner,
                candidate=candidate,
                focus=mutation_focus,
                hypothesis_key=hypothesis_key,
                candidate_repo=candidate_item.get("candidate_repo"),
                candidate_patch=candidate_item.get("candidate_patch"),
                candidate_output_dir=candidate_item.get("candidate_output_dir"),
                candidate_brief=candidate_item.get("candidate_brief"),
                generation_reason=(
                    str(candidate_item.get("generation_reason"))
                    if candidate_item.get("generation_reason") is not None
                    else None
                ),
                last_result=last_result,
            )
            if mutation_plan is not None:
                candidate_item["mutation_plan"] = mutation_plan
                candidate_item["mutation_plan_source"] = f"catalog:{rule_id}" if rule_id else "catalog"
                candidate_item["mutation_focus"] = mutation_focus
        if candidate_item.get("mutation_plan") is not None:
            if candidate_item.get("candidate_brief") is None:
                candidate_item["candidate_brief"] = default_candidate_brief_path(base_dir=base_dir, round_id=round_id)
            if (
                candidate_item.get("candidate_patch") is None
                and isinstance(candidate_item.get("candidate_repo"), Path)
            ):
                candidate_item["candidate_patch"] = default_candidate_patch_path(base_dir=base_dir, round_id=round_id)
        candidate_brief = candidate_item.get("candidate_brief")
        if candidate_brief is None and candidate_item.get("materialize_command"):
            candidate_brief = default_candidate_brief_path(base_dir=base_dir, round_id=round_id)
        if isinstance(candidate_brief, Path):
            write_json(
                candidate_brief,
                build_candidate_brief_payload(
                    workspace=workspace,
                    plan_path=plan_path,
                    round_id=round_id,
                    round_number=round_number,
                    objective=objective,
                    baseline_label=active_baseline,
                    owner=round_owner,
                    candidate=candidate,
                    candidate_source=source,
                    hypothesis_key=hypothesis_key,
                    candidate_repo=candidate_item.get("candidate_repo"),
                    candidate_patch=candidate_item.get("candidate_patch"),
                    candidate_brief=candidate_brief,
                    candidate_output_dir=candidate_item.get("candidate_output_dir"),
                    candidate_report=candidate_item.get("candidate_report"),
                    benchmark_command=candidate_item.get("benchmark_command"),
                    apply_command=candidate_item.get("apply_command"),
                    rollback_command=candidate_item.get("rollback_command"),
                    materialize_command=candidate_item.get("materialize_command"),
                    mutation_plan=candidate_item.get("mutation_plan"),
                    mutation_plan_source=(
                        str(candidate_item.get("mutation_plan_source"))
                        if candidate_item.get("mutation_plan_source") is not None
                        else None
                    ),
                    mutation_focus=(
                        str(candidate_item.get("mutation_focus"))
                        if candidate_item.get("mutation_focus") is not None
                        else mutation_focus
                    ),
                    auto_apply_rollback=bool(candidate_item.get("auto_apply_rollback", False)),
                    patch_strip=int(candidate_item.get("patch_strip", default_patch_strip)),
                    prior_attempts=prior_attempts,
                    generated_from=candidate_item.get("generated_from"),
                    generation_reason=(
                        str(candidate_item.get("generation_reason"))
                        if candidate_item.get("generation_reason") is not None
                        else None
                    ),
                    last_result=last_result,
                ),
            )
        materialize_result: dict[str, object] | None = None
        materialize_command = candidate_item.get("materialize_command")
        if isinstance(materialize_command, str) and materialize_command.strip() != "":
            materialize_result = iteration_cycle.run_command(materialize_command, cwd=base_dir)
        elif (
            isinstance(candidate_brief, Path)
            and isinstance(candidate_item.get("candidate_patch"), Path)
            and isinstance(candidate_item.get("candidate_repo"), Path)
        ):
            brief_payload = load_json(candidate_brief)
            if candidate_materializer.can_materialize_brief_payload(brief_payload):
                materialize_result = candidate_materializer.materialize_brief(
                    brief_path=candidate_brief,
                    candidate_root=candidate_item["candidate_repo"],
                    patch_output=candidate_item["candidate_patch"],
                    patch_strip=int(candidate_item.get("patch_strip", default_patch_strip)),
                )

        result = iteration_cycle.run_cycle(
            workspace=workspace,
            round_id=round_id,
            objective=objective,
            baseline_label=active_baseline,
            owner=round_owner,
            candidate=candidate,
            hypothesis_key=hypothesis_key,
            candidate_patch=candidate_item.get("candidate_patch"),
            patch_strip=int(candidate_item.get("patch_strip", default_patch_strip)),
            benchmark_command=candidate_item.get("benchmark_command"),
            apply_command=candidate_item.get("apply_command"),
            rollback_command=candidate_item.get("rollback_command"),
            auto_apply_rollback=bool(candidate_item.get("auto_apply_rollback", False)),
            candidate_repo=candidate_item.get("candidate_repo"),
            candidate_report=candidate_item.get("candidate_report"),
            candidate_output_dir=candidate_item.get("candidate_output_dir"),
            promote_label=promote_label if advance_baseline_on_keep else None,
            sync_patterns_enabled=False,
        )
        result["round_id"] = round_id
        result["owner"] = round_owner
        result["candidate"] = candidate
        result["baseline_label"] = active_baseline
        result["promote_label"] = promote_label if advance_baseline_on_keep else None
        result["candidate_source"] = source
        result["hypothesis_key"] = hypothesis_key
        result["candidate_brief"] = str(candidate_brief) if isinstance(candidate_brief, Path) else None
        result["materialize_command"] = materialize_command
        result["materialize_result"] = materialize_result
        result["mutation_plan_source"] = candidate_item.get("mutation_plan_source")
        result["mutation_focus"] = candidate_item.get("mutation_focus", mutation_focus)
        if source == "auto-generated":
            result["generated_from"] = candidate_item.get("generated_from", [])
            result["generation_reason"] = candidate_item.get("generation_reason")
        rounds_run.append(result)
        last_result = result

        decision = str(result.get("decision", "stop"))
        if decision in {"retry", "rollback"}:
            hypothesis_attempts[hypothesis_key] = prior_attempts + 1
            consecutive_non_keep_rounds += 1
        else:
            consecutive_non_keep_rounds = 0
        if decision == "keep" and advance_baseline_on_keep:
            active_baseline = promote_label
        persist_loop_progress(
            workspace=workspace,
            plan_path=plan_path,
            plan_digest=current_plan_digest,
            state_path=state_path,
            summary_path=summary_path,
            started_at=started_at,
            owner=owner,
            objective=objective,
            baseline_label=baseline_label,
            active_baseline=active_baseline,
            autonomous_candidate_generation=autonomous_candidate_generation,
            generated_rounds=generated_rounds,
            max_same_hypothesis_retries=max_same_hypothesis_retries,
            max_consecutive_non_keep_rounds=max_consecutive_non_keep_rounds,
            auto_pivot_on_stagnation=auto_pivot_on_stagnation,
            hypothesis_attempts=hypothesis_attempts,
            consecutive_non_keep_rounds=consecutive_non_keep_rounds,
            blocked_hypothesis_keys=blocked_hypothesis_keys,
            pivot_count=pivot_count,
            pivot_history=pivot_history,
            pending_generation_reason=pending_generation_reason,
            rounds_run=rounds_run,
            halt_reason="",
            sync_result=None,
            status="running",
            resume_requested=resume,
            resumed_from_existing=resumed_from_existing,
        )

        if (
            max_consecutive_non_keep_rounds is not None
            and consecutive_non_keep_rounds >= max_consecutive_non_keep_rounds
        ):
            if source == "auto-generated" and auto_pivot_on_stagnation:
                blocked_hypothesis_keys.add(hypothesis_key)
                pivot_count += 1
                pending_generation_reason = (
                    f"pivot after consecutive non-keep budget exhausted: {consecutive_non_keep_rounds}"
                )
                pivot_history.append(
                    {
                        "type": "consecutive-non-keep-budget",
                        "round_id": round_id,
                        "round_number": round_number,
                        "blocked_hypothesis_key": hypothesis_key,
                        "from_candidate": candidate,
                        "from_focus": str(result.get("mutation_focus", mutation_focus)).strip() or None,
                        "reason": pending_generation_reason,
                    }
                )
                consecutive_non_keep_rounds = 0
                persist_loop_progress(
                    workspace=workspace,
                    plan_path=plan_path,
                    plan_digest=current_plan_digest,
                    state_path=state_path,
                    summary_path=summary_path,
                    started_at=started_at,
                    owner=owner,
                    objective=objective,
                    baseline_label=baseline_label,
                    active_baseline=active_baseline,
                    autonomous_candidate_generation=autonomous_candidate_generation,
                    generated_rounds=generated_rounds,
                    max_same_hypothesis_retries=max_same_hypothesis_retries,
                    max_consecutive_non_keep_rounds=max_consecutive_non_keep_rounds,
                    auto_pivot_on_stagnation=auto_pivot_on_stagnation,
                    hypothesis_attempts=hypothesis_attempts,
                    consecutive_non_keep_rounds=consecutive_non_keep_rounds,
                    blocked_hypothesis_keys=blocked_hypothesis_keys,
                    pivot_count=pivot_count,
                    pivot_history=pivot_history,
                    pending_generation_reason=pending_generation_reason,
                    rounds_run=rounds_run,
                    halt_reason="",
                    sync_result=None,
                    status="running",
                    resume_requested=resume,
                    resumed_from_existing=resumed_from_existing,
                )
                round_number += 1
                continue
            halt_reason = f"consecutive non-keep budget exhausted: {consecutive_non_keep_rounds}"
            break
        if decision in halt_on_decisions:
            halt_reason = f"halted on decision: {decision}"
            break
        round_number += 1
    else:
        halt_reason = "max_rounds reached"

    sync_result: dict[str, object] | None = None
    if sync_patterns_at_end:
        sync_result = pattern_sync.sync_patterns(workspace=workspace)

    return persist_loop_progress(
        workspace=workspace,
        plan_path=plan_path,
        plan_digest=current_plan_digest,
        state_path=state_path,
        summary_path=summary_path,
        started_at=started_at,
        owner=owner,
        objective=objective,
        baseline_label=baseline_label,
        active_baseline=active_baseline,
        autonomous_candidate_generation=autonomous_candidate_generation,
        generated_rounds=generated_rounds,
        max_same_hypothesis_retries=max_same_hypothesis_retries,
        max_consecutive_non_keep_rounds=max_consecutive_non_keep_rounds,
        auto_pivot_on_stagnation=auto_pivot_on_stagnation,
        hypothesis_attempts=hypothesis_attempts,
        consecutive_non_keep_rounds=consecutive_non_keep_rounds,
        blocked_hypothesis_keys=blocked_hypothesis_keys,
        pivot_count=pivot_count,
        pivot_history=pivot_history,
        pending_generation_reason=pending_generation_reason,
        rounds_run=rounds_run,
        halt_reason=halt_reason,
        sync_result=sync_result,
        status="completed",
        resume_requested=resume,
        resumed_from_existing=resumed_from_existing,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a capped iteration loop from a plan file.")
    parser.add_argument("--workspace", default=".skill-iterations", help="Iteration workspace")
    parser.add_argument("--plan", required=True, help="Path to iteration plan JSON")
    parser.add_argument("--resume", action="store_true", help="Resume a persisted loop state instead of starting over")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_loop(
        workspace=Path(args.workspace).resolve(),
        plan_path=Path(args.plan).resolve(),
        resume=args.resume,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
