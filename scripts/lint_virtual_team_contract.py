#!/usr/bin/env python3
"""Mechanical contract checks for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
VERSION_PATH = SKILL_DIR / "VERSION"
INDEX_PATHS = [
    SKILL_DIR / "references" / "tooling-command-index.md",
    SKILL_DIR / "references" / "runtime-routing-index.md",
]
MARKDOWN_PATH_RE = re.compile(r"(?<![\w./-])((?:assets|references|scripts)/[A-Za-z0-9_./-]+\.(?:md|json|py))(?![\w./-])")
BARE_REFERENCE_RE = re.compile(r"^\s*-\s+`([A-Za-z0-9_.-]+\.(?:md|json))`\s*$")
SCRIPT_COMMAND_RE = re.compile(r"python\s+(scripts/[A-Za-z0-9_.-]+\.py)\b")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_contract_lint_route_request", ROUTE_SCRIPT)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def _check(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _resolve_markdown_path(raw_path: str, source_path: Path) -> Path:
    if raw_path.startswith(("assets/", "references/", "scripts/")):
        return (SKILL_DIR / raw_path).resolve()
    return (source_path.parent / raw_path).resolve()


def _collect_markdown_references(source_path: Path) -> list[str]:
    text = source_path.read_text(encoding="utf-8")
    refs = set(MARKDOWN_PATH_RE.findall(text))
    if source_path.name == "runtime-routing-index.md":
        for line in text.splitlines():
            match = BARE_REFERENCE_RE.match(line)
            if match:
                refs.add(match.group(1))
    return sorted(refs)


def lint_contract(skill_dir: Path | None = None) -> dict[str, object]:
    resolved_skill_dir = skill_dir.resolve() if skill_dir is not None else SKILL_DIR
    config_path = resolved_skill_dir / "references" / "routing-rules.json"
    version_path = resolved_skill_dir / "VERSION"
    config = load_json(config_path)
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    version = version_path.read_text(encoding="utf-8").strip()
    config_version = str(config.get("meta", {}).get("version", "")).strip()
    _check(
        version == config_version,
        errors,
        f"VERSION mismatch: `{version}` != routing-rules meta.version `{config_version}`. Fix both files together before release.",
    )
    checks.append({"name": "version-sync", "passed": version == config_version})

    lead_agents = config.get("process_skill_lead_agents", {})
    process_rules = config.get("process_skill_rules", {})
    if not isinstance(lead_agents, dict):
        raise RuntimeError("routing-rules.json process_skill_lead_agents must be an object")
    if not isinstance(process_rules, dict):
        raise RuntimeError("routing-rules.json process_skill_rules must be an object")

    lead_keys = {key for key in lead_agents if isinstance(key, str)}
    rule_keys = {key for key in process_rules if isinstance(key, str)}
    missing_in_rules = sorted(lead_keys - rule_keys)
    missing_in_leads = sorted(rule_keys - lead_keys)
    _check(
        len(missing_in_rules) == 0,
        errors,
        f"process_skill_lead_agents has no matching process_skill_rules for: {missing_in_rules}. Add trigger rules before exposing that process skill.",
    )
    _check(
        len(missing_in_leads) == 0,
        errors,
        f"process_skill_rules has no lead mapping for: {missing_in_leads}. Add process_skill_lead_agents entries so routing stays executable.",
    )
    checks.append(
        {
            "name": "process-skill-key-sync",
            "passed": len(missing_in_rules) == 0 and len(missing_in_leads) == 0,
            "details": {
                "lead_agent_keys": sorted(lead_keys),
                "rule_keys": sorted(rule_keys),
            },
        }
    )

    repo_strategy = {"strategy": "trunk-main", "base_branch": "main"}
    skill_flags = {
        "pre-development-planning": {"needs_pre_development_planning": True},
        "bounded-iteration": {"needs_iteration": True},
        "using-git-worktrees": {"needs_worktree": True},
        "release-gate": {"needs_release_gate": True},
        "git-workflow": {"needs_git_workflow": True},
    }
    for skill_name, flags in skill_flags.items():
        plan = route_request.build_process_plan(repo_strategy=repo_strategy, **flags)
        matching = [item for item in plan if isinstance(item, dict) and item.get("skill") == skill_name]
        _check(
            len(matching) == 1,
            errors,
            f"build_process_plan does not emit exactly one `{skill_name}` entry. Update route_request.py so the process plan stays contract-complete.",
        )
        if len(matching) != 1:
            checks.append({"name": f"process-plan-{skill_name}", "passed": False})
            continue
        entry = matching[0]
        reference = entry.get("reference")
        _check(
            isinstance(reference, str) and reference != "",
            errors,
            f"Process skill `{skill_name}` is missing its `reference` field in build_process_plan. Point it to the owning playbook.",
        )
        if isinstance(reference, str) and reference:
            reference_path = (resolved_skill_dir / reference).resolve()
            _check(
                reference_path.exists(),
                errors,
                f"Process skill `{skill_name}` points to missing reference `{reference}`. Restore the file or update the process plan reference.",
            )
        commands = entry.get("commands", [])
        _check(
            isinstance(commands, list) and len(commands) > 0,
            errors,
            f"Process skill `{skill_name}` has no command examples. Add at least one runnable command so the operator path is discoverable.",
        )
        if isinstance(commands, list):
            for command in commands:
                if not isinstance(command, str):
                    continue
                for script_path in SCRIPT_COMMAND_RE.findall(command):
                    resolved_script = (resolved_skill_dir / script_path).resolve()
                    _check(
                        resolved_script.exists(),
                        errors,
                        f"Process skill `{skill_name}` references missing script `{script_path}` in command `{command}`. Fix the command or add the script.",
                    )
        checks.append({"name": f"process-plan-{skill_name}", "passed": True})

    for index_path in INDEX_PATHS:
        refs = _collect_markdown_references(index_path)
        missing_refs = []
        for raw_ref in refs:
            resolved = _resolve_markdown_path(raw_ref, index_path)
            if not resolved.exists():
                missing_refs.append(raw_ref)
        _check(
            len(missing_refs) == 0,
            errors,
            f"{index_path.name} references missing files: {missing_refs}. Update the index so it only points to real assets.",
        )
        text = index_path.read_text(encoding="utf-8")
        missing_scripts = []
        for script_path in SCRIPT_COMMAND_RE.findall(text):
            resolved = (resolved_skill_dir / script_path).resolve()
            if not resolved.exists():
                missing_scripts.append(script_path)
        _check(
            len(missing_scripts) == 0,
            errors,
            f"{index_path.name} contains commands for missing scripts: {missing_scripts}. Repair the command index before release.",
        )
        checks.append(
            {
                "name": f"index-{index_path.name}",
                "passed": len(missing_refs) == 0 and len(missing_scripts) == 0,
                "details": {"references_checked": refs},
            }
        )

    return {
        "ok": len(errors) == 0,
        "skill_dir": str(resolved_skill_dir),
        "version": version,
        "checks": checks,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint virtual-intelligent-dev-team mechanical contract.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = lint_contract()
        exit_code = 0 if result["ok"] else 2
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
        exit_code = 2

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
