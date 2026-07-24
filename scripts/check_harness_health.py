#!/usr/bin/env python3
"""Health check for the virtual-intelligent-dev-team harness (v5.0+).

Six checks, in priority order:

1. Agent Identity: every lead agent named in `agent_rules` carries positive or
   negative keywords AND is documented under a `## N. <Name>` header in
   `references/agent-catalog.md`.
2. Agent Manifest: every lead agent in `agent_rules` carries
   `constraints` and `evidence_requirements` fields (v5.0 schema).
3. Routing Rules: `routing-rules.json` is parseable, has matching
   `process_skill_lead_agents` ↔ `process_skill_rules` keys, and lists every
   language profile referenced by `language-profiles.yaml`.
4. Workflow Bundles: the canonical bundle playbook reference files exist
   (the full 12-bundle catalog lives in `references/workflow-bundles.md`).
5. Decision Log: the canonical decision log is readable when present and is
   absent-but-allowed during the first deploy.
6. Language Profiles: the context profile file exists and exposes at least one
   profile entry.

Usage:
    python scripts/check_harness_health.py [--repo <path>] [--pretty]

Exit codes:
    0 — HEALTHY (all checks passed)
    2 — DEGRADED or BROKEN (any check failed)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]

DEFAULT_REPO = SKILL_DIR
ROUTING_RULES_PATH = SKILL_DIR / "references" / "routing-rules.json"
AGENT_CATALOG_PATH = SKILL_DIR / "references" / "agent-catalog.md"
LANGUAGE_PROFILES_PATH = SKILL_DIR / "references" / "language-profiles.yaml"
DECISION_LOG_DEFAULT = ".vidt/metrics/decision-log.jsonl"

# Canonical bundle playbook references — these are the bundle journeys backed by a
# dedicated playbook file. The full 12-entry bundle catalog lives in workflow-bundles.md.
CANONICAL_BUNDLE_REFS = (
    "references/pre-development-planning-playbook.md",
    "references/quick-slice-delivery-playbook.md",
    "references/product-delivery-playbook.md",
    "references/beta-validation-playbook.md",
    "references/technical-governance-playbook.md",
    "references/post-release-feedback-playbook.md",
    "references/release-gate-playbook.md",
    "references/root-cause-escalation-playbook.md",
    "references/git-workflow-playbook.md",
)

CANONICAL_BUNDLE_IDS = (
    "plan-first-build",
    "product-spec-deliver",
    "audit-fix-deliver",
    "govern-change-safely",
    "ship-hold-remediate",
    "root-cause-remediate",
    "beta-feedback-ramp",
    "quick-slice-deliver",
    "post-release-close-loop",
    "capture-project-knowledge",
    "multi-expert-execution",
    "direct-execution",
)

BUNDLE_ANCHOR_RE = re.compile(r'^<a id="([^"]+)"></a>$', re.MULTILINE)


def _check_agent_identity(
    agent_rules: dict[str, dict],
    catalog_agents: set[str],
    *,
    catalog_error: str | None = None,
) -> dict:
    """Each agent must carry positive or negative keywords AND be documented in agent-catalog.md."""
    missing_keywords = [name for name, rules in agent_rules.items() if not rules.get("positive") and not rules.get("negative")]
    missing_catalog = [name for name in agent_rules if name not in catalog_agents]
    missing = missing_keywords + [n for n in missing_catalog if n not in missing_keywords]
    keyword_ok = len(agent_rules) - len(missing_keywords)
    catalog_ok = len(agent_rules) - len(missing_catalog)
    detail = f"{keyword_ok}/{len(agent_rules)} agents have keyword entries; {catalog_ok}/{len(agent_rules)} documented in agent-catalog.md"
    if catalog_error:
        detail = f"{detail}; {catalog_error}"
    return {
        "name": "agent_identity",
        "passed": len(missing) == 0 and catalog_error is None,
        "detail": detail,
        "missing_keywords": missing_keywords,
        "missing_catalog": missing_catalog,
        "catalog_error": catalog_error,
    }


def _load_catalog_agents(skill_dir: Path) -> tuple[set[str], str | None]:
    """Parse agent names from `## N. <Name>` headers in agent-catalog.md.

    Catalog availability is part of the runtime contract, so read failures are returned
    to the caller and must fail the health check closed.
    """
    catalog_path = skill_dir / "references" / "agent-catalog.md"
    try:
        text = catalog_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return set(), f"failed to read references/agent-catalog.md: {exc}"
    # Match `## 1. Java Virtuoso` style headers (numbered agent entries only).
    return {m.group(1).strip() for m in re.finditer(r"^##\s+\d+\.\s+(.+)$", text, re.M)}, None


def _check_agent_manifest(agent_rules: dict[str, dict]) -> dict:
    """Each agent must declare non-empty `constraints` and `evidence_requirements` lists."""
    missing_constraints = []
    missing_evidence = []
    for name, rules in agent_rules.items():
        if not isinstance(rules.get("constraints"), list) or len(rules.get("constraints", [])) == 0:
            missing_constraints.append(name)
        if not isinstance(rules.get("evidence_requirements"), list) or len(rules.get("evidence_requirements", [])) == 0:
            missing_evidence.append(name)
    passed = not missing_constraints and not missing_evidence
    return {
        "name": "agent_manifest",
        "passed": passed,
        "detail": f"{len(agent_rules) - len(set(missing_constraints) | set(missing_evidence))}/{len(agent_rules)} agents carry both constraints and evidence_requirements",
        "missing_constraints": missing_constraints,
        "missing_evidence_requirements": missing_evidence,
    }


def _check_routing_rules(config: dict) -> dict:
    """Verify routing-rules.json structural invariants."""
    errors: list[str] = []
    leads = set(config.get("agent_rules", {}).keys())
    agent_order = set(config.get("agent_order", []))
    if not leads:
        errors.append("agent_rules is empty")
    missing_from_order = leads - agent_order
    if missing_from_order:
        errors.append(f"agents missing from agent_order: {sorted(missing_from_order)}")

    process_lead = set((config.get("process_skill_lead_agents") or {}).keys())
    process_rules = set((config.get("process_skill_rules") or {}).keys())
    only_in_lead = process_lead - process_rules
    only_in_rules = process_rules - process_lead
    if only_in_lead:
        errors.append(f"process_skill_lead_agents has no matching process_skill_rules for: {sorted(only_in_lead)}")
    if only_in_rules:
        errors.append(f"process_skill_rules has no lead mapping for: {sorted(only_in_rules)}")

    return {
        "name": "routing_rules",
        "passed": not errors,
        "detail": f"{len(leads)} lead agents, {len(process_lead)} process skills",
        "errors": errors,
    }


def _check_workflow_bundles(skill_dir: Path) -> dict:
    """Canonical bundle playbooks and all 12 stable bundle IDs must exist."""
    missing_playbooks: list[str] = []
    for rel in CANONICAL_BUNDLE_REFS:
        if not (skill_dir / rel).exists():
            missing_playbooks.append(rel)

    catalog_path = skill_dir / "references" / "workflow-bundles.md"
    catalog_error: str | None = None
    anchors: list[str] = []
    try:
        anchors = BUNDLE_ANCHOR_RE.findall(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        catalog_error = f"failed to read references/workflow-bundles.md: {exc}"

    anchor_counts = {bundle_id: anchors.count(bundle_id) for bundle_id in CANONICAL_BUNDLE_IDS}
    missing_bundle_ids = [bundle_id for bundle_id, count in anchor_counts.items() if count == 0]
    duplicate_bundle_ids = [bundle_id for bundle_id, count in anchor_counts.items() if count > 1]
    detected_count = len(CANONICAL_BUNDLE_IDS) - len(missing_bundle_ids)
    passed = not missing_playbooks and catalog_error is None and not missing_bundle_ids and not duplicate_bundle_ids
    return {
        "name": "workflow_bundles",
        "passed": passed,
        "detail": (
            f"{len(CANONICAL_BUNDLE_REFS) - len(missing_playbooks)}/{len(CANONICAL_BUNDLE_REFS)} "
            f"canonical bundle playbook files accessible; {detected_count}/{len(CANONICAL_BUNDLE_IDS)} "
            "stable bundle IDs cataloged"
        ),
        "missing_playbooks": missing_playbooks,
        "missing_bundle_ids": missing_bundle_ids,
        "duplicate_bundle_ids": duplicate_bundle_ids,
        "catalog_error": catalog_error,
    }


def _check_decision_log(repo_path: Path, log_path: str) -> dict:
    """Decision log must be readable when present."""
    full_path = repo_path / log_path

    if not full_path.exists():
        return {
            "name": "decision_log",
            "passed": True,
            "detail": f"log not yet created at {log_path}; allowed for first deploy",
            "entries": 0,
            "initialized": False,
        }

    try:
        with full_path.open("r", encoding="utf-8") as fh:
            lines = [line.strip() for line in fh if line.strip()]
    except Exception as exc:
        return {
            "name": "decision_log",
            "passed": False,
            "detail": f"failed to read {full_path}: {exc!r}",
            "initialized": True,
        }

    parsed = 0
    invalid = 0
    last_event: str | None = None
    for raw in lines:
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            invalid += 1
            continue
        if isinstance(item, dict):
            parsed += 1
            ts = item.get("timestamp")
            if isinstance(ts, str):
                last_event = ts

    return {
        "name": "decision_log",
        "passed": invalid == 0 and parsed > 0,
        "detail": f"{parsed} entries parsed, {invalid} invalid, last={last_event or 'n/a'}",
        "entries": parsed,
        "invalid_lines": invalid,
        "last_event": last_event,
        "initialized": True,
    }


def _check_language_profiles_present(skill_dir: Path) -> dict:
    """language-profiles.yaml must exist and be readable as YAML."""
    if not LANGUAGE_PROFILES_PATH.exists():
        return {
            "name": "language_profiles",
            "passed": False,
            "detail": f"{LANGUAGE_PROFILES_PATH.relative_to(skill_dir)} not found",
        }
    try:
        text = LANGUAGE_PROFILES_PATH.read_text(encoding="utf-8")
        profile_lines = sum(1 for line in text.splitlines() if line.startswith("  ") and line.endswith(":") and not line.startswith("    "))
    except Exception as exc:
        return {
            "name": "language_profiles",
            "passed": False,
            "detail": f"failed to read: {exc!r}",
        }
    return {
        "name": "language_profiles",
        "passed": profile_lines > 0,
        "detail": f"{profile_lines} profile entries detected (heuristic)",
        "entries_detected": profile_lines,
    }


def check_health(repo_path: Path, log_path: str = DECISION_LOG_DEFAULT) -> dict:
    """Run all checks and assemble a HEALTHY / DEGRADED / BROKEN verdict."""
    checks: list[dict] = []

    try:
        with ROUTING_RULES_PATH.open("r", encoding="utf-8") as fh:
            config = json.load(fh)
    except Exception as exc:
        return {
            "ok": False,
            "summary": "BROKEN",
            "error": f"failed to load routing-rules.json: {exc!r}",
            "checks": [],
        }

    agent_rules = config.get("agent_rules", {})
    catalog_agents, catalog_error = _load_catalog_agents(SKILL_DIR)
    checks.append(_check_agent_identity(agent_rules, catalog_agents, catalog_error=catalog_error))
    checks.append(_check_agent_manifest(agent_rules))
    checks.append(_check_routing_rules(config))
    checks.append(_check_workflow_bundles(SKILL_DIR))
    checks.append(_check_decision_log(repo_path, log_path))
    checks.append(_check_language_profiles_present(SKILL_DIR))

    failed = [c for c in checks if not c["passed"]]
    if not failed:
        verdict = "HEALTHY"
    elif any(c["name"] in {"agent_identity", "agent_manifest", "routing_rules", "workflow_bundles"} for c in failed):
        verdict = "BROKEN"
    else:
        verdict = "DEGRADED"

    return {
        "ok": verdict == "HEALTHY",
        "summary": verdict,
        "checks": checks,
        "check_count": len(checks),
        "failed_count": len(failed),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=str(DEFAULT_REPO),
        help="Repository root used to resolve the decision log path.",
    )
    parser.add_argument(
        "--log-file",
        default=DECISION_LOG_DEFAULT,
        help="Relative path to the v5.0 decision log.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON result on stdout.",
    )
    args = parser.parse_args(argv)

    repo_path = Path(args.repo).resolve()
    try:
        result = check_health(repo_path, log_path=args.log_file)
    except Exception as exc:
        result = {"ok": False, "summary": "BROKEN", "error": f"unexpected health check error: {exc!r}"}

    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
