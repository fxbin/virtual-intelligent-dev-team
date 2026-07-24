#!/usr/bin/env python3
"""Initialize a micro-practice ledger from a routed request."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
LEDGER_PATH = Path(".vidt/practices") / "micro-practice-ledger.json"
LEDGER_MARKDOWN_PATH = Path(".vidt/practices") / "micro-practice-ledger.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("virtual_team_init_micro_practices_route_request", ROUTE_SCRIPT)
response_contract = load_module("virtual_team_init_micro_practices_response_contract", RESPONSE_CONTRACT_SCRIPT)


def build_ledger(result: dict[str, object], source_request: str) -> dict[str, object]:
    practices = result.get("micro_practices", [])
    if not isinstance(practices, list):
        practices = []
    active_practices: list[dict[str, object]] = []
    for item in practices:
        if not isinstance(item, dict):
            continue
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []
        active_practices.append(
            {
                "name": str(item.get("name", "")),
                "reference": str(item.get("reference", "")),
                "reason": str(item.get("reason", "")),
                "evidence": [str(value) for value in evidence if str(value).strip()],
                "status": "active",
                "next_check": "Capture concrete evidence before declaring the practice satisfied.",
            }
        )
    return {
        "schema_version": "micro-practice-ledger/v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workflow_bundle": str(result.get("workflow_bundle", "direct-execution")),
        "source_request": source_request,
        "active_practices": active_practices,
        "resume_hint": "Read this ledger with the bundle resume anchor before continuing delivery.",
    }


def render_markdown(ledger: dict[str, object]) -> str:
    practices = ledger.get("active_practices", [])
    if not isinstance(practices, list):
        practices = []
    lines = [
        "# Micro-Practice Ledger",
        "",
        f"- Workflow bundle: {ledger.get('workflow_bundle', 'direct-execution')}",
        f"- Generated at: {ledger.get('generated_at', '')}",
        f"- Resume hint: {ledger.get('resume_hint', '')}",
        "",
        "## Active Practices",
    ]
    if not practices:
        lines.append("- none")
    for item in practices:
        if not isinstance(item, dict):
            continue
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []
        status = str(item.get("status", "active"))
        evidence_label = "Evidence needed" if status == "active" else "Evidence captured"
        lines.extend(
            [
                f"- {item.get('name', '')}",
                f"  - Reference: {item.get('reference', '')}",
                f"  - Reason: {item.get('reason', '')}",
                f"  - {evidence_label}: {', '.join(str(value) for value in evidence) if evidence else 'none'}",
                f"  - Status: {status}",
                f"  - Next check: {item.get('next_check', '')}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def init_micro_practices(
    *,
    root: Path,
    text: str,
    config_path: Path = DEFAULT_CONFIG_PATH,
    overwrite: bool = False,
) -> dict[str, object]:
    config = route_request.load_config(config_path)
    governance = config.setdefault("governance", {})
    if isinstance(governance, dict):
        fast_track = governance.setdefault("fast_track_control", {})
        if isinstance(fast_track, dict):
            fast_track["write_event_log"] = False
    result = route_request.route_request(text, config, repo_path=root)
    ledger = build_ledger(result, text)
    response_contract.validate_micro_practice_ledger(ledger)

    ledger_path = root / LEDGER_PATH
    markdown_path = root / LEDGER_MARKDOWN_PATH
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    actions: list[dict[str, str]] = []
    for path, content, kind in [
        (ledger_path, json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", "micro-practice-ledger-json"),
        (markdown_path, render_markdown(ledger), "micro-practice-ledger-markdown"),
    ]:
        if path.exists() and not overwrite:
            status = "skipped"
        else:
            status = "updated" if path.exists() else "created"
            path.write_text(content, encoding="utf-8")
        actions.append(
            {
                "kind": kind,
                "target": str(path.relative_to(root)),
                "status": status,
            }
        )
    return {
        "ok": True,
        "root": str(root),
        "workflow_bundle": ledger["workflow_bundle"],
        "active_practices": [str(item.get("name", "")) for item in ledger["active_practices"]],
        "actions": actions,
        "resume_anchor": str(LEDGER_PATH),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize micro-practice ledger anchors.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--text", required=True, help="Original user request text.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Routing config JSON.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing ledger files.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_micro_practices(
        root=Path(args.root).resolve(),
        text=args.text,
        config_path=Path(args.config).resolve(),
        overwrite=args.overwrite,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
