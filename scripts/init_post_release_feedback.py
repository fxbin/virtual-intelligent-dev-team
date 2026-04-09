#!/usr/bin/env python3
"""Initialize post-release feedback workspace anchors for virtual-intelligent-dev-team."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def copy_template(source: Path, target: Path, overwrite: bool) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        return "skipped"
    existed = target.exists()
    shutil.copyfile(source, target)
    return "updated" if existed else "created"


def init_post_release_feedback(root: Path, overwrite: bool = False) -> dict[str, object]:
    specs = [
        (
            SKILL_DIR / "assets" / "post-release-rollout-summary-template.md",
            root / ".skill-post-release" / "rollout-summary.md",
            "rollout-summary",
        ),
        (
            SKILL_DIR / "assets" / "post-release-feedback-ledger-template.md",
            root / ".skill-post-release" / "feedback-ledger.md",
            "feedback-ledger",
        ),
        (
            SKILL_DIR / "assets" / "post-release-signal-report-template.json",
            root / ".skill-post-release" / "current-signals.json",
            "signal-report",
        ),
        (
            SKILL_DIR / "assets" / "post-release-triage-summary-template.md",
            root / ".skill-post-release" / "triage-summary.md",
            "triage-summary",
        ),
    ]
    actions: list[dict[str, str]] = []
    artifacts: list[str] = []
    for source, target, kind in specs:
        actions.append(
            {
                "kind": kind,
                "target": str(target.relative_to(root)),
                "status": copy_template(source, target, overwrite),
            }
        )
        artifacts.append(str(target))
    return {
        "ok": True,
        "root": str(root),
        "overwrite": overwrite,
        "actions": actions,
        "artifacts": artifacts,
        "resume_anchor": str(root / ".skill-post-release" / "triage-summary.md"),
        "evaluation_command": "python scripts/evaluate_post_release_feedback.py --report .skill-post-release/current-signals.json --pretty",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize post-release feedback workspace anchors.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing anchors.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_post_release_feedback(Path(args.root).resolve(), overwrite=args.overwrite)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
