#!/usr/bin/env python3
"""Verify completion evidence before done/ready/handoff claims."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
DEFAULT_EVIDENCE_PATH = Path(".vidt/evidence") / "completion-evidence.json"
COMMAND_PREFIXES = {
    "bun",
    "cargo",
    "deno",
    "git",
    "go",
    "gradle",
    "java",
    "jest",
    "make",
    "mvn",
    "node",
    "npm",
    "npx",
    "pnpm",
    "playwright",
    "pytest",
    "python",
    "python3",
    "rg",
    "ruff",
    "tox",
    "tsc",
    "uv",
    "vitest",
    "yarn",
}
ARTIFACT_SUFFIXES = {
    ".csv",
    ".html",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".pdf",
    ".png",
    ".sarif",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module(
    "virtual_team_verify_completion_evidence_response_contract",
    RESPONSE_CONTRACT_SCRIPT,
)


def compact_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def load_completion_evidence(evidence_path: Path) -> dict[str, object]:
    with evidence_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("completion evidence must be a JSON object")
    response_contract.validate_completion_evidence(payload)
    return payload


def is_effectively_none(values: list[str]) -> bool:
    if len(values) == 0:
        return False
    return all(value.lower() in {"none", "n/a", "not applicable"} for value in values)


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return stripped.startswith("<") and stripped.endswith(">")


def placeholder_values(values: list[str]) -> list[str]:
    return [value for value in values if is_placeholder(value)]


def infer_repo_root(evidence_path: Path) -> Path:
    for parent in evidence_path.parents:
        if parent.name == ".vidt":
            return parent.parent
    return evidence_path.parent


def is_command_ref(value: str) -> bool:
    stripped = value.strip()
    if stripped == "":
        return False
    first = stripped.split()[0]
    return first in COMMAND_PREFIXES


def is_path_like_ref(value: str) -> bool:
    stripped = value.strip()
    if stripped == "" or "://" in stripped or "\n" in stripped:
        return False
    candidate = Path(stripped)
    if stripped.startswith((".", "/", "~")) or "/" in stripped:
        return True
    return candidate.suffix.lower() in ARTIFACT_SUFFIXES


def evaluate_evidence_refs(evidence_refs: list[str], repo_root: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for raw in evidence_refs:
        value = raw.strip()
        if is_command_ref(value):
            checks.append(
                {
                    "ref": value,
                    "kind": "command",
                    "verifiable": True,
                    "exists": None,
                }
            )
            continue
        if is_path_like_ref(value):
            path = Path(value).expanduser()
            resolved = path if path.is_absolute() else repo_root / path
            checks.append(
                {
                    "ref": value,
                    "kind": "artifact",
                    "verifiable": resolved.exists(),
                    "exists": resolved.exists(),
                    "resolved_path": str(resolved),
                }
            )
            continue
        checks.append(
            {
                "ref": value,
                "kind": "note",
                "verifiable": False,
                "exists": None,
            }
        )
    return checks


def build_recommended_commands(evidence_rel: str, decision: str) -> list[str]:
    commands = []
    if decision != "complete":
        commands.append(
            "cp assets/completion-evidence-template.json "
            ".vidt/evidence/completion-evidence.json"
        )
    commands.append(
        f"python scripts/verify_completion_evidence.py --evidence {evidence_rel} --pretty"
    )
    return commands


def evaluate_completion_evidence(evidence_path: Path) -> dict[str, object]:
    resolved_evidence = evidence_path.resolve()
    repo_root = infer_repo_root(resolved_evidence)
    evidence_rel = (
        str(resolved_evidence.relative_to(repo_root))
        if resolved_evidence.is_relative_to(repo_root)
        else str(resolved_evidence)
    )

    payload = load_completion_evidence(resolved_evidence)
    result = payload.get("result", {})
    if not isinstance(result, dict):
        result = {}
    status = str(result.get("status", "")).strip()
    grade = str(payload.get("confidence_grade", "")).strip()
    covered_scope = compact_string_list(payload.get("covered_scope"))
    uncovered_scope = compact_string_list(payload.get("uncovered_scope"))
    residual_risk = compact_string_list(payload.get("residual_risk"))
    evidence_refs = compact_string_list(payload.get("evidence_refs"))
    evidence_ref_checks = evaluate_evidence_refs(evidence_refs, repo_root)

    worker_model = str(payload.get("worker_model", "")).strip()
    verifier_model = str(payload.get("verifier_model", "")).strip()
    same_model_self_review = (
        bool(worker_model)
        and bool(verifier_model)
        and worker_model == verifier_model
    )

    blockers: list[str] = []
    warnings: list[str] = []
    if status == "failed":
        blockers.append("evidence result status is failed")
    elif status in {"partial", "not_run"}:
        warnings.append(f"evidence result status is {status}")
    action = str(payload.get("evidence_action", "")).strip()
    summary = str(result.get("summary", "")).strip()
    if is_placeholder(action):
        warnings.append("evidence_action still contains a template placeholder")
    if is_placeholder(summary):
        warnings.append("result.summary still contains a template placeholder")
    if grade == "C":
        warnings.append("confidence grade C cannot support a completion claim")
    placeholder_scope = placeholder_values(covered_scope + uncovered_scope + residual_risk + evidence_refs)
    if placeholder_scope:
        warnings.append("completion evidence still contains template placeholders")
    if not is_effectively_none(uncovered_scope):
        warnings.append("uncovered_scope contains non-empty residual scope")
    if not is_effectively_none(residual_risk):
        warnings.append("residual_risk contains non-empty risk")
    if len(covered_scope) == 0:
        blockers.append("covered_scope is empty")
    if len(evidence_refs) == 0:
        blockers.append("evidence_refs is empty")
    missing_artifact_refs = [
        str(item.get("ref", ""))
        for item in evidence_ref_checks
        if item.get("kind") == "artifact" and not bool(item.get("exists"))
    ]
    if missing_artifact_refs:
        warnings.append("evidence_refs reference missing artifacts")
    if evidence_refs and not any(bool(item.get("verifiable")) for item in evidence_ref_checks):
        warnings.append("evidence_refs contain no verifiable command or existing artifact")
    if same_model_self_review and status == "passed":
        warnings.append(
            f"same model self-review detected (worker={worker_model}, verifier={verifier_model}); "
            "independent verification recommended"
        )

    if blockers:
        decision = "blocked"
        completion_allowed = False
        reason = "; ".join(blockers)
        next_action = "fix failed or structurally incomplete completion evidence before claiming completion"
    elif warnings:
        decision = "continue"
        completion_allowed = False
        reason = "; ".join(warnings)
        next_action = "close uncovered scope or residual risk, then re-run completion evidence verification"
    else:
        decision = "complete"
        completion_allowed = True
        reason = "completion evidence supports the claim"
        next_action = "use this completion evidence in the done/ready/handoff claim"

    return {
        "ok": completion_allowed,
        "source_gate": "completion-evidence",
        "decision": decision,
        "reason": reason,
        "completion_allowed": completion_allowed,
        "evidence_path": evidence_rel,
        "status": status,
        "confidence_grade": grade,
        "worker_model": worker_model,
        "verifier_model": verifier_model,
        "same_model_self_review": same_model_self_review,
        "blockers": blockers,
        "warnings": warnings,
        "covered_scope": covered_scope,
        "uncovered_scope": uncovered_scope,
        "residual_risk": residual_risk,
        "evidence_refs": evidence_refs,
        "evidence_ref_checks": evidence_ref_checks,
        "follow_up": {
            "next_action": next_action,
            "resume_anchor": evidence_rel,
            "recommended_commands": build_recommended_commands(evidence_rel, decision),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify completion evidence gate.")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH), help="Path to completion evidence JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = evaluate_completion_evidence(Path(args.evidence).resolve())
        exit_code = 0 if bool(result.get("ok")) else 1
    except Exception as exc:
        result = {"ok": False, "source_gate": "completion-evidence", "decision": "invalid", "error": str(exc)}
        exit_code = 2
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
