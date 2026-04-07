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
RESPONSE_PACK_SCRIPT = SCRIPT_DIR / "generate_response_pack.py"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
VERSION_PATH = SKILL_DIR / "VERSION"
SIDECAR_SCHEMA_PATH = SKILL_DIR / "references" / "response-pack-sidecar-schema.md"
SIDECAR_SCHEMA_JSON_PATH = SKILL_DIR / "references" / "response-pack-sidecar.schema.json"
MARKDOWN_PATH_RE = re.compile(r"(?<![\w./-])((?:assets|references|scripts)/[A-Za-z0-9_./-]+\.(?:md|json|py))(?![\w./-])")
BARE_REFERENCE_RE = re.compile(r"^\s*-\s+`([A-Za-z0-9_.-]+\.(?:md|json))`\s*$")
SCRIPT_COMMAND_RE = re.compile(r"python\s+(scripts/[A-Za-z0-9_.-]+\.py)\b")
SCHEMA_VERSION_RE = re.compile(r"版本：`([^`]+)`")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return data


def _check(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _resolve_markdown_path(raw_path: str, source_path: Path, skill_dir: Path) -> Path:
    if raw_path.startswith(("assets/", "references/", "scripts/")):
        return (skill_dir / raw_path).resolve()
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
    response_pack_script = resolved_skill_dir / "scripts" / "generate_response_pack.py"
    response_contract_script = resolved_skill_dir / "scripts" / "response_contract.py"
    sidecar_schema_path = resolved_skill_dir / "references" / "response-pack-sidecar-schema.md"
    sidecar_schema_json_path = resolved_skill_dir / "references" / "response-pack-sidecar.schema.json"
    route_script = resolved_skill_dir / "scripts" / "route_request.py"
    index_paths = [
        resolved_skill_dir / "references" / "tooling-command-index.md",
        resolved_skill_dir / "references" / "runtime-routing-index.md",
    ]
    local_route_request = load_module(
        f"virtual_team_contract_lint_route_request_{resolved_skill_dir.name}",
        route_script,
    )
    local_response_pack = (
        load_module(
            f"virtual_team_contract_lint_response_pack_{resolved_skill_dir.name}",
            response_pack_script,
        )
        if response_pack_script.exists()
        else None
    )
    local_response_contract = (
        load_module(
            f"virtual_team_contract_lint_response_contract_{resolved_skill_dir.name}",
            response_contract_script,
        )
        if response_contract_script.exists()
        else None
    )
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

    _check(
        response_pack_script.exists(),
        errors,
        "Missing scripts/generate_response_pack.py. Restore the response-pack generator before release.",
    )
    _check(
        response_contract_script.exists(),
        errors,
        "Missing scripts/response_contract.py. Restore the shared response contract helper before release.",
    )
    _check(
        sidecar_schema_path.exists(),
        errors,
        "Missing references/response-pack-sidecar-schema.md. Restore the sidecar schema document before release.",
    )
    _check(
        sidecar_schema_json_path.exists(),
        errors,
        "Missing references/response-pack-sidecar.schema.json. Restore the executable sidecar schema before release.",
    )
    checks.append(
        {
            "name": "response-pack-sidecar-files",
            "passed": (
                response_pack_script.exists()
                and response_contract_script.exists()
                and sidecar_schema_path.exists()
                and sidecar_schema_json_path.exists()
            ),
        }
    )

    schema_constant = getattr(local_response_contract, "SIDECAR_SCHEMA_VERSION", "")
    _check(
        isinstance(schema_constant, str) and schema_constant.strip() != "",
        errors,
        "response_contract.py must expose a non-empty SIDECAR_SCHEMA_VERSION constant.",
    )

    schema_doc_version = ""
    if sidecar_schema_path.exists():
        schema_doc_text = sidecar_schema_path.read_text(encoding="utf-8")
        match = SCHEMA_VERSION_RE.search(schema_doc_text)
        schema_doc_version = match.group(1).strip() if match else ""
        _check(
            schema_doc_version != "",
            errors,
            "response-pack-sidecar-schema.md must declare its schema version in the `版本：` header.",
        )
        if isinstance(schema_constant, str) and schema_constant.strip():
            _check(
                schema_doc_version == schema_constant,
                errors,
                f"Sidecar schema version mismatch: schema doc `{schema_doc_version}` != response_contract `{schema_constant}`.",
            )

    build_payload = getattr(local_response_pack, "build_response_pack_payload", None)
    _check(
        callable(build_payload),
        errors,
        "generate_response_pack.py must expose build_response_pack_payload for machine-readable response packs.",
    )
    payload: dict[str, object] = {}
    if callable(build_payload):
        payload = build_payload({})
        _check(
            payload.get("schema_version") == schema_constant,
            errors,
            "build_response_pack_payload must expose schema_version that matches response_contract.SIDECAR_SCHEMA_VERSION.",
        )
        required_sections = {
            "team_dispatch",
            "execution_result",
            "evidence",
            "next_action",
            "resume",
            "git_workflow",
            "governance",
        }
        missing_sections = sorted(section for section in required_sections if section not in payload)
        _check(
            len(missing_sections) == 0,
            errors,
            f"build_response_pack_payload is missing required top-level sections: {missing_sections}.",
        )
        if hasattr(local_response_contract, "validate_response_pack_payload"):
            sample_payloads = {
                "default": payload,
                "planning": build_payload({"needs_pre_development_planning": True}),
                "release": build_payload({"needs_release_gate": True}),
                "iteration": build_payload(
                    {
                        "needs_iteration": True,
                        "iteration_profile": {
                            "round_cap_online": 3,
                            "round_cap_offline": 120,
                            "allowed_decisions": ["keep", "retry", "rollback", "stop"],
                        },
                        "progress_anchor_recommended": ".skill-iterations/current-round-memory.md",
                    }
                ),
            }
            schema_validation_failures: list[str] = []
            for sample_name, sample_payload in sample_payloads.items():
                try:
                    local_response_contract.validate_response_pack_payload(sample_payload)
                except Exception as exc:
                    schema_validation_failures.append(f"{sample_name}: {exc}")
            _check(
                len(schema_validation_failures) == 0,
                errors,
                "response-pack sidecar schema validation failed for sample payloads: "
                + "; ".join(schema_validation_failures),
            )
        else:
            schema_validation_failures = ["response_contract.validate_response_pack_payload missing"]
        checks.append(
            {
                "name": "response-pack-sidecar-contract",
                "passed": (
                    len(missing_sections) == 0
                    and payload.get("schema_version") == schema_constant
                    and len(schema_validation_failures) == 0
                ),
                "details": {
                    "schema_version": payload.get("schema_version"),
                    "required_sections": sorted(required_sections),
                    "schema_json": str(sidecar_schema_json_path),
                },
            }
        )
    else:
        checks.append({"name": "response-pack-sidecar-contract", "passed": False})

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
        plan = local_route_request.build_process_plan(repo_strategy=repo_strategy, **flags)
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

    for index_path in index_paths:
        refs = _collect_markdown_references(index_path)
        missing_refs = []
        for raw_ref in refs:
            resolved = _resolve_markdown_path(raw_ref, index_path, resolved_skill_dir)
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
