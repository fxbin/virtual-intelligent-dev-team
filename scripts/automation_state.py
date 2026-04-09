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
    state_root = ".skill-auto/state"
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
