#!/usr/bin/env python3
"""Shared machine-readable automation state helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
from uuid import uuid4


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
SCHEMA_VERSION = "automation-state/v1"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module(
    "virtual_team_automation_state_response_contract",
    RESPONSE_CONTRACT_SCRIPT,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_run_id(prefix: str = "auto") -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def compact_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def build_automation_state(
    *,
    repo_root: Path,
    source_workflow: str,
    state_kind: str,
    mode: str,
    phase: str,
    status: str,
    decision: str,
    run_style: str = "foreground",
    safety_level: str = "standard",
    resume_requested: bool = False,
    detached_ready: bool = False,
    run_id: str | None = None,
    parent_run_id: str | None = None,
    execution_mode: str | None = None,
    resume_anchor: str = "",
    resume_artifacts: list[str] | None = None,
    recommended_next_step: str = "",
    handoff_target: str = "",
    primary_path: str | None = None,
    related_paths: list[str] | None = None,
    upstream_dependencies: list[str] | None = None,
    notes: list[str] | None = None,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    resolved_run_id = run_id or generate_run_id()
    state_root = ".vidt/auto/state"
    primary = primary_path or f"{state_root}/{state_kind}-{resolved_run_id}.json"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "run_id": resolved_run_id,
        "parent_run_id": parent_run_id,
        "source_workflow": source_workflow,
        "state_kind": state_kind,
        "mode": mode,
        "phase": phase,
        "status": status,
        "decision": decision,
        "execution_mode": execution_mode,
        "run_style": run_style,
        "safety_level": safety_level,
        "resume_requested": resume_requested,
        "detached_ready": detached_ready,
        "resume_anchor": resume_anchor,
        "resume_artifacts": compact_string_list(resume_artifacts),
        "recommended_next_step": recommended_next_step,
        "handoff_target": handoff_target,
        "state_paths": {
            "primary": primary,
            "related": compact_string_list(related_paths),
        },
        "upstream_dependencies": compact_string_list(upstream_dependencies),
        "notes": compact_string_list(notes),
        "metadata": metadata if isinstance(metadata, dict) else {},
    }
    response_contract.validate_automation_state(payload)
    return payload


def write_automation_state(
    *,
    repo_root: Path,
    source_workflow: str,
    state_kind: str,
    mode: str,
    phase: str,
    status: str,
    decision: str,
    run_style: str = "foreground",
    safety_level: str = "standard",
    resume_requested: bool = False,
    detached_ready: bool = False,
    run_id: str | None = None,
    parent_run_id: str | None = None,
    execution_mode: str | None = None,
    resume_anchor: str = "",
    resume_artifacts: list[str] | None = None,
    recommended_next_step: str = "",
    handoff_target: str = "",
    primary_path: str | None = None,
    related_paths: list[str] | None = None,
    upstream_dependencies: list[str] | None = None,
    notes: list[str] | None = None,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    payload = build_automation_state(
        repo_root=repo_root,
        source_workflow=source_workflow,
        state_kind=state_kind,
        mode=mode,
        phase=phase,
        status=status,
        decision=decision,
        run_style=run_style,
        safety_level=safety_level,
        resume_requested=resume_requested,
        detached_ready=detached_ready,
        run_id=run_id,
        parent_run_id=parent_run_id,
        execution_mode=execution_mode,
        resume_anchor=resume_anchor,
        resume_artifacts=resume_artifacts,
        recommended_next_step=recommended_next_step,
        handoff_target=handoff_target,
        primary_path=primary_path,
        related_paths=related_paths,
        upstream_dependencies=upstream_dependencies,
        notes=notes,
        metadata=metadata,
    )
    target = resolve_path(repo_root, str(payload["state_paths"]["primary"]))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


# ---- Workspace Journal (P1-10) ----

import hashlib

JOURNAL_VERSION = "workspace-journal/v1"
DEFAULT_JOURNAL_PATH = Path(".vidt/harness") / "workspace-journal.jsonl"


def compute_journal_hash(entry: dict[str, object]) -> str:
    """计算 journal entry 的 SHA-256 hash(因果链)"""
    raw = (
        str(entry.get("timestamp", ""))
        + str(entry.get("agent", ""))
        + str(entry.get("action", ""))
        + str(entry.get("reason", ""))
        + str(entry.get("spec_ref", ""))
        + str(entry.get("prev_hash", ""))
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def append_journal(
    journal_path: Path | None = None,
    *,
    agent: str,
    action: str,
    reason: str,
    spec_ref: str = "",
    layer: str = "",
    state_snapshot: dict[str, object] | None = None,
) -> dict[str, object]:
    """追加一条 journal entry(append-only + 因果链)

    参数:
        journal_path: journal 文件路径,默认 .vidt/harness/workspace-journal.jsonl
        agent: 执行动作的角色
        action: 动作类型
        reason: 动作理由
        spec_ref: 引用的 spec 条目
        layer: 所属层
        state_snapshot: 动作后的 state 快照
    """
    path = journal_path or DEFAULT_JOURNAL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, object]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").strip().split("\n"):
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    prev_hash = entries[-1].get("hash", "genesis") if entries else "genesis"
    entry: dict[str, object] = {
        "timestamp": now_iso(),
        "agent": agent,
        "action": action,
        "reason": reason,
        "spec_ref": spec_ref,
        "prev_hash": prev_hash,
        "layer": layer,
    }
    if state_snapshot is not None:
        entry["state_snapshot"] = state_snapshot
    entry["hash"] = compute_journal_hash(entry)

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def replay_journal(
    journal_path: Path | None = None,
    *,
    target_timestamp: str | None = None,
) -> dict[str, object]:
    """从 journal replay 重建状态

    参数:
        journal_path: journal 文件路径
        target_timestamp: 重建到这个时间点为止(含),None 表示重建到最新
    """
    path = journal_path or DEFAULT_JOURNAL_PATH
    if not path.exists():
        return {"entries": [], "reconstructed_state": {}, "entry_count": 0}

    entries: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").strip().split("\n"):
        line = line.strip()
        if line:
            try:
                entry = json.loads(line)
                if target_timestamp and str(entry.get("timestamp", "")) > target_timestamp:
                    break
                entries.append(entry)
            except json.JSONDecodeError:
                continue

    state: dict[str, object] = {}
    for entry in entries:
        agent = str(entry.get("agent", ""))
        action = str(entry.get("action", ""))
        key = f"{agent}:{action}"
        if "state_snapshot" in entry:
            snapshot = entry["state_snapshot"]
            if isinstance(snapshot, dict):
                state[key] = snapshot
        state[f"{key}_last_timestamp"] = entry.get("timestamp", "")
        state[f"{key}_last_reason"] = entry.get("reason", "")

    return {
        "entries": entries,
        "reconstructed_state": state,
        "entry_count": len(entries),
    }
