#!/usr/bin/env python3
"""Run one verify_action eval with the same deterministic fixture as the local benchmark.

The repository-level blind audit executes commands in a subprocess. This adapter keeps
stateful checks isolated by reusing `run_benchmarks.prepare_verify_action_fixture`
instead of reading whatever `.vidt/` artifacts happen to exist in the caller's
workspace.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_EVALS_PATH = SKILL_DIR / "evals" / "evals.json"
VERIFY_ACTION_SCRIPT = SCRIPT_DIR / "verify_action.py"
RUN_BENCHMARKS_SCRIPT = SCRIPT_DIR / "run_benchmarks.py"
CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify_action_module = load_module("virtual_team_blind_verify_action", VERIFY_ACTION_SCRIPT)
benchmark_module = load_module("virtual_team_blind_run_benchmarks", RUN_BENCHMARKS_SCRIPT)


def load_eval(evals_path: Path, *, text: str, check: str) -> dict[str, object]:
    payload = json.loads(evals_path.read_text(encoding="utf-8"))
    evals = payload.get("evals", []) if isinstance(payload, dict) else []
    matches = [
        item
        for item in evals
        if isinstance(item, dict)
        and str(item.get("runner", "route")) == "verify_action"
        and str(item.get("prompt", "")) == text
        and str(item.get("check", "")) == check
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one verify_action eval for check={check!r} and prompt={text!r}; found {len(matches)}"
        )
    return matches[0]


def run_eval(item: dict[str, object]) -> dict[str, object]:
    prompt = str(item.get("prompt", ""))
    check = str(item.get("check", "")).strip()
    assistant_agents = item.get("assistant_agents", [])
    if not isinstance(assistant_agents, list):
        assistant_agents = []

    config = verify_action_module.load_config(CONFIG_PATH)
    with tempfile.TemporaryDirectory(prefix=f"virtual-team-blind-verify-{item.get('id')}-") as tmp:
        fixture_repo, fixture_kwargs = benchmark_module.prepare_verify_action_fixture(item, Path(tmp))
        verify_kwargs: dict[str, object] = {
            "text": prompt,
            "config": config,
            "repo_path": fixture_repo,
            "check": check,
            "process_skill": str(item.get("process_skill", "")).strip() or None,
            "lead_agent": str(item.get("lead_agent", "")).strip() or None,
            "assistant_agents": [str(agent) for agent in assistant_agents if str(agent).strip()],
            "handoff_type": str(item.get("handoff_type", "")).strip() or None,
            "dispatch_text": str(item.get("dispatch_text", "")) or None,
            "breaker_layer": str(item.get("breaker_layer", "")).strip() or None,
        }
        verify_kwargs.update(fixture_kwargs)
        return verify_action_module.verify_action(**verify_kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="Exact eval prompt.")
    parser.add_argument("--check", required=True, help="verify_action check name.")
    parser.add_argument("--evals", default=str(DEFAULT_EVALS_PATH), help="Path to evals.json.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    item = load_eval(Path(args.evals).resolve(), text=args.text, check=args.check)
    result = run_eval(item)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
