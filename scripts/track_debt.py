#!/usr/bin/env python3
"""Debt ledger 追踪脚本。

功能:
1. 扫描 completion-evidence 中的 known_shortcuts,更新 debt ledger
2. /debt 命令:输出当前 debt 概览
3. /resolve 命令:标记某个 debt 为已解决

用法:
    python track_debt.py scan --evidence <path> --ledger <path>
    python track_debt.py /debt --ledger <path>
    python track_debt.py /resolve --ledger <path> --id DEBT-001
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_LEDGER_PATH = SKILL_DIR / "assets" / "debt-ledger-template.json"
DEFAULT_EVIDENCE_PATH = Path(".vidt/evidence") / "completion-evidence.json"

SHORTCUT_MARKER = "known-shortcut"


def load_ledger(ledger_path: Path) -> dict[str, object]:
    """加载 debt ledger 文件,不存在时返回空 ledger 结构"""
    if not ledger_path.exists():
        return {
            "schema_version": "debt-ledger/v1",
            "generated_at": "",
            "source_request": "",
            "entries": [],
            "summary": {"total": 0, "open": 0, "resolved": 0},
        }
    with ledger_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger_path: Path, ledger: dict[str, object]) -> None:
    """保存 debt ledger 到文件,并更新 summary"""
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    open_count = sum(1 for e in entries if isinstance(e, dict) and e.get("status") == "open")
    resolved_count = sum(1 for e in entries if isinstance(e, dict) and e.get("status") == "resolved")
    ledger["entries"] = entries
    ledger["summary"] = {
        "total": len(entries),
        "open": open_count,
        "resolved": resolved_count,
    }
    ledger["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)


def load_evidence(evidence_path: Path) -> dict[str, object]:
    """加载 completion-evidence 文件"""
    if not evidence_path.exists():
        return {}
    with evidence_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def scan_shortcuts(evidence_path: Path, ledger_path: Path) -> dict[str, object]:
    """扫描 completion-evidence 中的 known_shortcuts,更新 debt ledger"""
    evidence = load_evidence(evidence_path)
    shortcuts = evidence.get("known_shortcuts", [])
    if not isinstance(shortcuts, list):
        shortcuts = []

    ledger = load_ledger(ledger_path)
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    existing_locations = {
        e.get("location") for e in entries if isinstance(e, dict)
    }

    new_count = 0
    for idx, shortcut in enumerate(shortcuts):
        if not isinstance(shortcut, dict):
            continue
        location = str(shortcut.get("location", ""))
        if location in existing_locations:
            continue
        debt_id = f"DEBT-{len(entries) + 1:03d}"
        entries.append({
            "id": debt_id,
            "location": location,
            "shortcut_type": "known-shortcut",
            "description": str(shortcut.get("description", "")),
            "ceiling": str(shortcut.get("ceiling", "")),
            "upgrade_path": str(shortcut.get("upgrade_path", "")),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "open",
            "resolved_at": None,
            "resolution": None,
        })
        new_count += 1

    save_ledger(ledger_path, ledger)

    return {
        "action": "scan",
        "evidence_path": str(evidence_path),
        "ledger_path": str(ledger_path),
        "new_entries": new_count,
        "total_entries": len(entries),
        "summary": ledger.get("summary", {}),
    }


def show_debt(ledger_path: Path) -> dict[str, object]:
    """输出当前 debt 概览"""
    ledger = load_ledger(ledger_path)
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    open_entries = [e for e in entries if isinstance(e, dict) and e.get("status") == "open"]
    resolved_entries = [e for e in entries if isinstance(e, dict) and e.get("status") == "resolved"]

    return {
        "action": "debt_overview",
        "ledger_path": str(ledger_path),
        "summary": {
            "total": len(entries),
            "open": len(open_entries),
            "resolved": len(resolved_entries),
        },
        "open_entries": open_entries,
        "resolved_entries": resolved_entries,
    }


def resolve_debt(ledger_path: Path, debt_id: str, resolution: str) -> dict[str, object]:
    """标记某个 debt 为已解决"""
    ledger = load_ledger(ledger_path)
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    found = False
    for entry in entries:
        if isinstance(entry, dict) and entry.get("id") == debt_id:
            entry["status"] = "resolved"
            entry["resolved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            entry["resolution"] = resolution
            found = True
            break

    if not found:
        return {
            "action": "resolve",
            "debt_id": debt_id,
            "found": False,
            "message": f"Debt entry {debt_id} not found",
        }

    save_ledger(ledger_path, ledger)

    return {
        "action": "resolve",
        "debt_id": debt_id,
        "found": True,
        "resolution": resolution,
        "resolved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": ledger.get("summary", {}),
    }


def self_test() -> int:
    """自测:验证 scan/debt/resolve 流程"""
    import tempfile

    tmpdir = Path(tempfile.mkdtemp(prefix="debt-test-"))
    evidence_path = tmpdir / "evidence.json"
    ledger_path = tmpdir / "ledger.json"

    evidence = {
        "known_shortcuts": [
            {
                "location": "src/cache.py:42",
                "ceiling": "QPS < 100",
                "upgrade_path": "引入 Redis",
            },
            {
                "location": "src/auth.py:100",
                "ceiling": "用户数 < 1000",
                "upgrade_path": "迁移到 OAuth2",
            },
        ]
    }
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False))

    failures: list[str] = []

    scan_result = scan_shortcuts(evidence_path, ledger_path)
    if scan_result["new_entries"] != 2:
        failures.append(f"FAIL: scan 应新增 2 条,实际 {scan_result['new_entries']}")

    scan_again = scan_shortcuts(evidence_path, ledger_path)
    if scan_again["new_entries"] != 0:
        failures.append(f"FAIL: 二次 scan 应新增 0 条(去重),实际 {scan_again['new_entries']}")

    debt_result = show_debt(ledger_path)
    if debt_result["summary"]["open"] != 2:
        failures.append(f"FAIL: open 应为 2,实际 {debt_result['summary']['open']}")

    resolve_result = resolve_debt(ledger_path, "DEBT-001", "已引入 Redis")
    if not resolve_result["found"]:
        failures.append("FAIL: resolve DEBT-001 未找到")

    debt_after = show_debt(ledger_path)
    if debt_after["summary"]["open"] != 1 or debt_after["summary"]["resolved"] != 1:
        failures.append(
            f"FAIL: resolve 后 open=1 resolved=1,实际 open={debt_after['summary']['open']} resolved={debt_after['summary']['resolved']}"
        )

    if failures:
        for f in failures:
            print(f"  {f}")
        print(f"\nSelf-test FAILED ({len(failures)} assertion(s))")
        return 1

    print("Self-test PASSED: scan/debt/resolve 流程全部正常")
    print("  - scan 新增 2 条 known-shortcut")
    print("  - 二次 scan 去重")
    print("  - /debt 概览正确")
    print("  - /resolve 标记已解决")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track known-shortcut debt entries from completion evidence.")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    parser.add_argument("command", nargs="?", choices=["scan", "/debt", "/resolve"], help="命令")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE_PATH, help="completion-evidence 文件路径")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH, help="debt ledger 文件路径")
    parser.add_argument("--id", help="要 resolve 的 debt ID(如 DEBT-001)")
    parser.add_argument("--resolution", default="", help="resolve 说明")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.self_test:
        raise SystemExit(self_test())

    if not args.command:
        raise SystemExit("command is required (scan, /debt, /resolve, or use --self-test)")

    if args.command == "scan":
        result = scan_shortcuts(args.evidence, args.ledger)
    elif args.command == "/debt":
        result = show_debt(args.ledger)
    elif args.command == "/resolve":
        if not args.id:
            raise SystemExit("--id is required for /resolve")
        result = resolve_debt(args.ledger, args.id, args.resolution)
    else:
        raise SystemExit(f"Unknown command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
