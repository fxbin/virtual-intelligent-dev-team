#!/usr/bin/env python3
"""Update a micro-practice ledger entry and refresh its markdown view."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RESPONSE_CONTRACT_SCRIPT = SCRIPT_DIR / "response_contract.py"
INIT_MICRO_PRACTICES_SCRIPT = SCRIPT_DIR / "init_micro_practices.py"
DEFAULT_LEDGER_PATH = Path(".vidt/practices") / "micro-practice-ledger.json"
DEFAULT_MARKDOWN_PATH = Path(".vidt/practices") / "micro-practice-ledger.md"
VALID_STATUSES = {"active", "satisfied", "blocked"}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


response_contract = load_module("virtual_team_update_micro_practices_response_contract", RESPONSE_CONTRACT_SCRIPT)
init_micro_practices = load_module("virtual_team_update_micro_practices_init", INIT_MICRO_PRACTICES_SCRIPT)


def load_ledger(ledger_path: Path) -> dict[str, object]:
    with ledger_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise RuntimeError("micro-practice ledger must be a JSON object")
    response_contract.validate_micro_practice_ledger(payload)
    return payload


def repo_root_from_ledger(ledger_path: Path) -> Path:
    for parent in ledger_path.parents:
        if parent.name == ".vidt":
            return parent.parent
    return ledger_path.parent


def compact_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def find_practice(practices: object, name: str) -> dict[str, object]:
    if not isinstance(practices, list):
        raise RuntimeError("micro-practice ledger active_practices must be an array")
    matches = [
        item
        for item in practices
        if isinstance(item, dict) and str(item.get("name", "")).strip() == name
    ]
    if not matches:
        available = sorted(
            str(item.get("name", "")).strip()
            for item in practices
            if isinstance(item, dict) and str(item.get("name", "")).strip()
        )
        raise ValueError(f"Unknown micro-practice `{name}`. Available practices: {', '.join(available) or 'none'}")
    if len(matches) > 1:
        raise ValueError(f"Micro-practice `{name}` appears more than once; repair the ledger before updating it")
    return matches[0]


def update_micro_practice(
    *,
    ledger_path: Path,
    name: str,
    status: str,
    evidence: list[str] | None = None,
    next_check: str | None = None,
    replace_evidence: bool = False,
    markdown_path: Path | None = None,
) -> dict[str, object]:
    resolved_ledger = ledger_path.resolve()
    normalized_status = status.strip()
    if normalized_status not in VALID_STATUSES:
        raise ValueError(f"Unsupported status `{status}`. Use one of: {', '.join(sorted(VALID_STATUSES))}")

    ledger = load_ledger(resolved_ledger)
    practice = find_practice(ledger.get("active_practices"), name.strip())

    previous_status = str(practice.get("status", "")).strip()
    previous_evidence = compact_string_list(practice.get("evidence"))
    incoming_evidence = compact_string_list(evidence or [])
    if replace_evidence:
        updated_evidence = incoming_evidence
    else:
        updated_evidence = previous_evidence[:]
        for item in incoming_evidence:
            if item not in updated_evidence:
                updated_evidence.append(item)
    if normalized_status == "satisfied" and not updated_evidence:
        raise ValueError("A satisfied micro-practice must keep at least one evidence item")

    practice["status"] = normalized_status
    practice["evidence"] = updated_evidence
    if next_check is not None:
        practice["next_check"] = next_check.strip()
    elif normalized_status == "satisfied":
        practice["next_check"] = "Evidence captured; keep this practice satisfied unless new scope reopens it."
    elif normalized_status == "blocked":
        practice["next_check"] = "Resolve the blocker or record why the workflow must stop."
    elif not str(practice.get("next_check", "")).strip():
        practice["next_check"] = "Capture concrete evidence before declaring the practice satisfied."

    response_contract.validate_micro_practice_ledger(ledger)
    resolved_ledger.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    repo_root = repo_root_from_ledger(resolved_ledger)
    resolved_markdown = (
        markdown_path.resolve()
        if markdown_path is not None
        else repo_root / DEFAULT_MARKDOWN_PATH
    )
    resolved_markdown.parent.mkdir(parents=True, exist_ok=True)
    resolved_markdown.write_text(init_micro_practices.render_markdown(ledger), encoding="utf-8")

    ledger_rel = str(resolved_ledger.relative_to(repo_root)) if resolved_ledger.is_relative_to(repo_root) else str(resolved_ledger)
    markdown_rel = (
        str(resolved_markdown.relative_to(repo_root))
        if resolved_markdown.is_relative_to(repo_root)
        else str(resolved_markdown)
    )
    return {
        "ok": True,
        "ledger": ledger_rel,
        "markdown": markdown_rel,
        "practice": name.strip(),
        "previous_status": previous_status,
        "status": normalized_status,
        "evidence": updated_evidence,
        "next_check": str(practice.get("next_check", "")),
        "resume_anchor": ledger_rel,
        "recommended_command": f"python scripts/evaluate_micro_practices.py --ledger {ledger_rel} --pretty",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update one micro-practice ledger entry.")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER_PATH), help="Path to micro-practice ledger JSON.")
    parser.add_argument("--name", required=True, help="Micro-practice name to update.")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES), help="New practice status.")
    parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Evidence string to append. Repeat the flag to add multiple evidence items.",
    )
    parser.add_argument("--replace-evidence", action="store_true", help="Replace evidence instead of appending.")
    parser.add_argument("--next-check", help="Next check note to store on the practice.")
    parser.add_argument("--markdown", help="Optional markdown ledger path to refresh.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = update_micro_practice(
        ledger_path=Path(args.ledger).resolve(),
        name=args.name,
        status=args.status,
        evidence=[str(item) for item in args.evidence],
        next_check=args.next_check,
        replace_evidence=args.replace_evidence,
        markdown_path=Path(args.markdown).resolve() if args.markdown else None,
    )
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
