#!/usr/bin/env python3
"""Initialize durable project context for virtual-intelligent-dev-team."""

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


def init_project_context(root: Path, overwrite: bool = False) -> dict[str, object]:
    target = root / ".vidt/context" / "project-context.md"
    status = copy_template(
        SKILL_DIR / "assets" / "project-context-template.md",
        target,
        overwrite,
    )
    return {
        "ok": True,
        "root": str(root),
        "overwrite": overwrite,
        "actions": [
            {
                "kind": "project-context",
                "target": str(target.relative_to(root)),
                "status": status,
            }
        ],
        "resume_anchor": ".vidt/context/project-context.md",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize durable project context.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing context.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = init_project_context(Path(args.root).resolve(), overwrite=args.overwrite)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
