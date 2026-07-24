#!/usr/bin/env python3
"""Full pipeline smoke test for virtual-intelligent-dev-team.

Tests the complete chain from route request through execution.

Usage:
    python scripts/smoke_test_full_pipeline.py [--work-dir /tmp/smoke-test]

Exit codes:
    0 - All smoke tests passed
    1 - One or more tests failed
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def run_command(cmd: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def test_route_request(work_dir: Path) -> dict:
    """Test route request functionality."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'route_request.py'),
         '--text', '设计一个Kafka实时数据管道',
         '--repo', str(work_dir)],
        work_dir
    )
    passed = result.returncode == 0 and 'Data Pipeline Guardian' in result.stdout
    return {
        "phase": "route_request",
        "passed": passed,
        "output": result.stdout[:200] if passed else result.stderr[:200],
    }


def test_harness_health(work_dir: Path) -> dict:
    """Test harness health check."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'check_harness_health.py'),
         '--repo', str(work_dir)],
        work_dir
    )
    passed = result.returncode == 0 and '"summary": "HEALTHY"' in result.stdout
    return {
        "phase": "harness_health",
        "passed": passed,
        "output": "HEALTHY" if passed else result.stderr[:200],
    }


def test_init_quick_slice(work_dir: Path) -> dict:
    """Test init quick slice."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'init_quick_slice.py'),
         '--root', str(work_dir)],
        work_dir
    )
    passed = result.returncode == 0
    anchor_exists = (work_dir / '.vidt/delivery' / 'current-slice.md').exists()
    return {
        "phase": "init_quick_slice",
        "passed": passed and anchor_exists,
        "output": "Anchor created" if anchor_exists else result.stderr[:200],
    }


def test_check_language_profiles(work_dir: Path) -> dict:
    """Test language profiles check."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'check_language_profiles.py')],
        work_dir
    )
    passed = result.returncode == 0
    return {
        "phase": "check_language_profiles",
        "passed": passed,
        "output": "Profiles valid" if passed else result.stderr[:200],
    }


def test_init_micro_practices(work_dir: Path) -> dict:
    """Test micro-practices initialization."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'init_micro_practices.py'),
         '--root', str(work_dir),
         '--text', 'Test micro practice setup'],
        work_dir
    )
    passed = result.returncode == 0
    ledger_exists = (work_dir / '.vidt/practices' / 'micro-practice-ledger.json').exists()
    return {
        "phase": "init_micro_practices",
        "passed": passed and ledger_exists,
        "output": "Ledger created" if ledger_exists else result.stderr[:200],
    }


def test_validate_virtual_team(work_dir: Path) -> dict:
    """Test virtual team validation."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'validate_virtual_team.py')],
        work_dir
    )
    passed = result.returncode == 0 and 'valid' in result.stdout.lower()
    return {
        "phase": "validate_virtual_team",
        "passed": passed,
        "output": "Validation passed" if passed else result.stderr[:200],
    }


def test_failure_path_invalid_route(work_dir: Path) -> dict:
    """Test failure path: invalid route request."""
    result = run_command(
        ['python', str(SKILL_DIR / 'scripts' / 'route_request.py'),
         '--text', '',  # Empty text should fail gracefully
         '--repo', str(work_dir)],
        work_dir
    )
    # Should either fail gracefully or return a fallback/clarification response
    graceful = result.returncode == 0 or 'clarification' in result.stdout.lower() or 'fallback' in result.stdout.lower()
    return {
        "phase": "failure_path_invalid_route",
        "passed": graceful,
        "output": "Graceful handling" if graceful else result.stderr[:200],
    }


def smoke_test(work_dir: Path) -> dict:
    """Run full smoke test suite."""
    phases = [
        test_route_request,
        test_harness_health,
        test_init_quick_slice,
        test_check_language_profiles,
        test_init_micro_practices,
        test_validate_virtual_team,
        test_failure_path_invalid_route,
    ]

    results = []
    all_passed = True

    for phase_func in phases:
        result = phase_func(work_dir)
        results.append(result)
        if not result["passed"]:
            all_passed = False

    return {
        "ok": all_passed,
        "phases": results,
        "passed_count": sum(1 for r in results if r["passed"]),
        "total_count": len(results),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Full pipeline smoke test")
    parser.add_argument(
        "--work-dir",
        default=None,
        help="Working directory for smoke test (default: temp dir)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    args = parser.parse_args(argv)

    work_dir = Path(args.work_dir) if args.work_dir else Path(tempfile.mkdtemp(prefix="vidt-smoke-"))

    try:
        result = smoke_test(work_dir)
        indent = 2 if args.pretty else None
        print(json.dumps(result, ensure_ascii=False, indent=indent))
        return 0 if result["ok"] else 1
    finally:
        if args.work_dir is None:
            shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
