#!/usr/bin/env python3
"""Create the Harness engineering constraint file before implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_OUTPUT = ".vidt/harness/engineering-constraints.md"


def build_constraints_markdown(summary: str, *, artifact_path: str = DEFAULT_OUTPUT) -> str:
    summary = summary.strip() or "<task summary>"
    return f"""# Harness Engineering Constraints

Task summary: {summary}

## Scope

- In scope:
- Out of scope:

## Non-Negotiable Constraints

- Preserve user-owned work and unrelated local changes.
- Match the existing project structure before adding new abstractions.
- Keep the change to the smallest defensible implementation bundle.

## Forbidden Changes

- Do not rewrite unrelated files.
- Do not change public contracts without explicit acceptance criteria.
- Do not skip verification before declaring the task complete.

## Verification Evidence

- Commands:
- Artifacts:
- Manual checks:

## Rollback And Stop Conditions

- Roll back when verification regresses or a higher-priority constraint breaks.
- Stop and ask when a missing decision would change scope, contract, or risk.

## Resume Anchor

- Constraint file: `{artifact_path}`
"""


def init_constraints(root: Path, *, output: str, summary: str) -> dict[str, object]:
    root = root.resolve()
    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    existed = output_path.exists()
    if not existed:
        output_path.write_text(build_constraints_markdown(summary, artifact_path=output), encoding="utf-8")
    return {
        "ok": True,
        "created": not existed,
        "path": str(output_path),
        "relative_path": output,
        "summary": summary.strip() or "<task summary>",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize Harness engineering constraints.")
    parser.add_argument("--root", default=".", help="Project root where .vidt/harness should be created.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Constraint file path relative to root.")
    parser.add_argument("--summary", default="<task summary>", help="Short task summary for the constraint file.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = init_constraints(Path(args.root), output=args.output, summary=args.summary)
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
