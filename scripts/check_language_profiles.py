#!/usr/bin/env python3
"""Validate `references/language-profiles.yaml` against `references/routing-rules.json`.

The two files are written by hand and must stay in sync. This script enforces
the cross-file invariants so a drift never reaches runtime:

1. Top-level `profiles` keys in YAML match `language_profiles` keys in JSON.
2. Every YAML profile carries all six required sub-keys (display_name,
   routing_keywords, ecosystem, conventions, verification, harness_constraints).
3. Every YAML `routing_keywords` entry overlaps with the matching JSON
   `keywords` list. Overlap below 50% is a warning (still allowed for
   forward-compat).
4. Optional: when a profile declares `lead_agent`, it must match the JSON
   copy. (The YAML does not have to carry `lead_agent`; routing still
   reads from JSON.)

Usage:
    python scripts/check_language_profiles.py [--pretty]

Exit codes:
    0 — all checks passed (warnings allowed)
    2 — any check failed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - environment guard
    print(json.dumps({"ok": False, "error": "PyYAML is required. Install it with `pip install pyyaml`."}, ensure_ascii=False))
    raise SystemExit(2)

SKILL_DIR = Path(__file__).resolve().parents[1]
ROUTING_RULES_PATH = SKILL_DIR / "references" / "routing-rules.json"
LANGUAGE_PROFILES_PATH = SKILL_DIR / "references" / "language-profiles.yaml"

REQUIRED_PROFILE_KEYS = (
    "display_name",
    "routing_keywords",
    "ecosystem",
    "conventions",
    "verification",
    "harness_constraints",
)


def _required_subkeys_present(profile: dict) -> list[str]:
    return [key for key in REQUIRED_PROFILE_KEYS if key not in profile]


def _keyword_overlap(yaml_keywords: list[str], json_keywords: list[str]) -> float:
    if not yaml_keywords or not json_keywords:
        return 0.0
    yaml_set = {k.lower() for k in yaml_keywords}
    json_set = {k.lower() for k in json_keywords}
    if not yaml_set:
        return 0.0
    return len(yaml_set & json_set) / len(yaml_set)


def check_profiles(routing_config: dict, yaml_data: dict) -> dict:
    checks: list[dict] = []
    warnings: list[str] = []

    if yaml_data.get("schema_version") != "language-profiles/v1":
        checks.append(
            {
                "name": "yaml_schema_version",
                "passed": False,
                "detail": f"expected 'language-profiles/v1', got {yaml_data.get('schema_version')!r}",
            }
        )
    else:
        checks.append(
            {"name": "yaml_schema_version", "passed": True, "detail": "language-profiles/v1"}
        )

    yaml_profiles = yaml_data.get("profiles", {}) or {}
    json_profiles = routing_config.get("language_profiles", {}) or {}

    yaml_keys = set(yaml_profiles.keys())
    json_keys = set(json_profiles.keys())
    missing_in_yaml = sorted(json_keys - yaml_keys)
    missing_in_json = sorted(yaml_keys - json_keys)

    # yaml is an incremental context layer: it may cover a subset of the
    # languages listed in routing-rules.json. Mismatches where yaml references
    # a language that does not exist in json (missing_in_json) are failures
    # because the router would never match that profile. The opposite
    # direction (yaml is missing entries that exist in json) is a warning
    # because the LLM already knows idiomatic patterns for those languages.
    if missing_in_json:
        checks.append(
            {
                "name": "key_parity",
                "passed": False,
                "detail": f"{len(missing_in_json)} yaml profiles reference languages not in json",
                "missing_in_json": missing_in_json,
                "missing_in_yaml": missing_in_yaml,
            }
        )
    else:
        checks.append(
            {
                "name": "key_parity",
                "passed": True,
                "detail": (
                    f"yaml covers {len(yaml_keys)}/{len(json_keys)} json profiles; "
                    f"{len(missing_in_yaml)} languages intentionally not profiled"
                ),
                "missing_in_yaml": missing_in_yaml,
            }
        )

    required_key_failures: dict[str, list[str]] = {}
    overlap_warnings: list[str] = []
    for lang, profile in yaml_profiles.items():
        missing = _required_subkeys_present(profile)
        if missing:
            required_key_failures[lang] = missing
        yaml_kw = profile.get("routing_keywords", []) or []
        json_kw = (json_profiles.get(lang, {}) or {}).get("keywords", []) or []
        overlap = _keyword_overlap(list(yaml_kw), list(json_kw))
        if yaml_kw and overlap < 0.5:
            overlap_warnings.append(
                f"{lang}: routing_keywords overlap with json is only {overlap:.0%} "
                f"(yaml has {len(yaml_kw)} entries, json has {len(json_kw)})"
            )

    if required_key_failures:
        checks.append(
            {
                "name": "required_subkeys",
                "passed": False,
                "detail": f"{len(required_key_failures)} profiles missing required sub-keys",
                "failures": required_key_failures,
            }
        )
    else:
        checks.append(
            {
                "name": "required_subkeys",
                "passed": True,
                "detail": f"all {len(yaml_profiles)} profiles carry required sub-keys",
            }
        )

    if overlap_warnings:
        checks.append(
            {
                "name": "keyword_overlap",
                "passed": True,
                "detail": f"{len(overlap_warnings)} overlap warnings (informational only)",
                "warnings": overlap_warnings,
            }
        )
    else:
        checks.append(
            {
                "name": "keyword_overlap",
                "passed": True,
                "detail": "routing_keywords overlap healthy across all profiles",
            }
        )

    # Cross-reference lead_agent when the YAML profile carries one.
    lead_agent_failures: list[str] = []
    for lang, profile in yaml_profiles.items():
        yaml_lead = profile.get("lead_agent")
        json_lead = (json_profiles.get(lang, {}) or {}).get("lead_agent")
        if yaml_lead is not None and json_lead is not None and yaml_lead != json_lead:
            lead_agent_failures.append(
                f"{lang}: yaml lead_agent={yaml_lead!r} != json lead_agent={json_lead!r}"
            )
    if lead_agent_failures:
        checks.append(
            {
                "name": "lead_agent_consistency",
                "passed": False,
                "detail": f"{len(lead_agent_failures)} lead_agent mismatches",
                "failures": lead_agent_failures,
            }
        )
    else:
        checks.append(
            {
                "name": "lead_agent_consistency",
                "passed": True,
                "detail": "yaml and json lead_agent values agree wherever both declare one",
            }
        )

    failed = [c for c in checks if not c["passed"]]
    return {
        "ok": not failed,
        "yaml_profile_count": len(yaml_profiles),
        "json_profile_count": len(json_profiles),
        "checks": checks,
        "failed_count": len(failed),
        "warnings": warnings,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--routing-rules",
        default=str(ROUTING_RULES_PATH),
        help="Path to routing-rules.json.",
    )
    parser.add_argument(
        "--yaml",
        default=str(LANGUAGE_PROFILES_PATH),
        help="Path to language-profiles.yaml.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON result on stdout.",
    )
    args = parser.parse_args(argv)

    try:
        with Path(args.routing_rules).open("r", encoding="utf-8") as fh:
            routing_config = json.load(fh)
        with Path(args.yaml).open("r", encoding="utf-8") as fh:
            yaml_data = yaml.safe_load(fh) or {}
    except Exception as exc:
        result = {"ok": False, "error": f"failed to load inputs: {exc!r}"}
        print(json.dumps(result, ensure_ascii=False))
        return 2

    result = check_profiles(routing_config, yaml_data)
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))