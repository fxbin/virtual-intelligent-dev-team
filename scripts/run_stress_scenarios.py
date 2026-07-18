#!/usr/bin/env python3
"""P2-15 多角色失败场景压测脚本

执行 7 个失败场景，收集 agent 崩溃点，输出 trace_summary（机器校验）和 fix_scope（root-cause/symptom）。

ponytail 融入：
- comprehension-first 嵌入 trace_summary 字段（机器校验真实文件路径 + caller 列表）
- root-cause 修复嵌入 fix_scope 字段（root-cause: 多 caller 共享函数 / symptom: 单 path 修补）
- ONE runnable check 原则：每场景一个可运行检查，无框架无 fixture

author: fxbin
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCENARIOS_DIR = SKILL_DIR / "evals" / "stress-scenarios"

ROUTE_SCRIPT = SCRIPT_DIR / "route_request.py"
VERIFY_ACTION_SCRIPT = SCRIPT_DIR / "verify_action.py"
CIRCUIT_BREAKER_SCRIPT = SCRIPT_DIR / "circuit_breaker.py"
BASELINE_REGISTRY_SCRIPT = SCRIPT_DIR / "register_benchmark_baseline.py"
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "routing-rules.json"
EXPECTED_SCENARIO_COUNT = 12
MIN_ROOT_CAUSE_RATIO = 0.8


def load_module(name: str, path: Path):
    """从指定路径加载 Python 模块（不依赖 sys.path）"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route_request = load_module("stress_route_request", ROUTE_SCRIPT)
verify_action_module = load_module("stress_verify_action", VERIFY_ACTION_SCRIPT)
circuit_breaker_module = load_module("stress_circuit_breaker", CIRCUIT_BREAKER_SCRIPT)


def load_config() -> dict[str, object]:
    """加载 routing-rules.json 配置"""
    return route_request.load_config(DEFAULT_CONFIG_PATH)


def load_scenario(path: Path) -> dict[str, object]:
    """加载场景 JSON 文件"""
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_scenarios() -> list[dict[str, object]]:
    """加载 evals/stress-scenarios/ 下全部场景 JSON，按文件名排序"""
    files = sorted(SCENARIOS_DIR.glob("*.json"))
    return [load_scenario(f) for f in files]


def run_verify_action_check(
    scenario: dict[str, object],
    config: dict[str, object],
    workspace: Path,
) -> dict[str, object]:
    """执行 verify_action check 类场景

    参数:
        scenario: 场景 JSON dict
        config: routing 配置
        workspace: 临时工作区路径

    返回:
        执行结果 dict，含 actual_caught / allowed / summary / raw_result
    """
    trigger = scenario.get("trigger", {})
    if not isinstance(trigger, dict):
        trigger = {}
    check_name = str(trigger.get("check", ""))
    setup_data = trigger.get("setup_data", {})
    if not isinstance(setup_data, dict):
        setup_data = {}

    kwargs: dict[str, object] = {
        "text": "stress test scenario for " + str(scenario.get("scenario_id", "")),
        "config": config,
        "repo_path": SKILL_DIR,
        "check": check_name,
    }

    if check_name == "contract-lock":
        spec_data = setup_data.get("contract_spec", {})
        spec_path = workspace / "contract-spec.json"
        spec_path.write_text(json.dumps(spec_data, ensure_ascii=False, indent=2), encoding="utf-8")
        kwargs["contract_spec"] = spec_path
    elif check_name == "lead-prejudgment":
        kwargs["dispatch_text"] = str(setup_data.get("dispatch_text", ""))
    elif check_name == "spec-violation":
        worker_content = str(setup_data.get("worker_output_content", ""))
        worker_path = workspace / "worker-output.txt"
        worker_path.write_text(worker_content, encoding="utf-8")
        kwargs["worker_output"] = worker_path

    try:
        result = verify_action_module.verify_action(**kwargs)
        allowed = bool(result.get("allowed"))
        actual_caught = not allowed
        return {
            "actual_caught": actual_caught,
            "allowed": allowed,
            "summary": str(result.get("summary", "")),
            "raw_result": result,
            "error": None,
        }
    except Exception as exc:
        return {
            "actual_caught": False,
            "allowed": None,
            "summary": "",
            "raw_result": None,
            "error": repr(exc),
        }


def run_circuit_breaker_api(
    scenario: dict[str, object],
    workspace: Path,
) -> dict[str, object]:
    """执行 circuit_breaker_api 类场景

    参数:
        scenario: 场景 JSON dict
        workspace: 临时工作区路径

    返回:
        执行结果 dict，含 actual_caught / breaker_state / raw_results
    """
    trigger = scenario.get("trigger", {})
    if not isinstance(trigger, dict):
        trigger = {}
    setup_data = trigger.get("setup_data", {})
    if not isinstance(setup_data, dict):
        setup_data = {}

    layer = str(setup_data.get("layer", "verifier"))
    failure_count = int(setup_data.get("failure_count", 3))
    failure_reason = str(setup_data.get("failure_reason", "stress test failure"))

    config_path = workspace / "breaker-config.json"
    config_path.write_text(json.dumps({
        "layers": {
            layer: {
                "max_consecutive_failures": failure_count,
                "cooldown_seconds": 300,
                "escalation_sink_path": str(workspace / "escalation-queue.jsonl"),
            }
        }
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    state_file = workspace / "breaker-state.json"
    escalation_sink = workspace / "escalation-queue.jsonl"

    breaker = circuit_breaker_module.CircuitBreaker(
        config_path=config_path,
        state_file=state_file,
        escalation_sink=escalation_sink,
    )

    raw_results = []
    for i in range(failure_count):
        r = breaker.record_failure(layer, f"{failure_reason} ({i+1}/{failure_count})")
        raw_results.append(r)

    check_result = breaker.check(layer)
    actual_caught = not bool(check_result.get("allowed"))

    return {
        "actual_caught": actual_caught,
        "allowed": bool(check_result.get("allowed")),
        "breaker_state": str(check_result.get("state", "")),
        "summary": str(check_result.get("reason", "")),
        "raw_results": raw_results,
        "error": None,
    }


def run_file_operation(
    scenario: dict[str, object],
    workspace: Path,
) -> dict[str, object]:
    """执行 file_operation 类场景（baseline 删除后检测）

    参数:
        scenario: 场景 JSON dict
        workspace: 临时工作区路径

    返回:
        执行结果 dict，含 actual_caught / baseline_exists / details
    """
    trigger = scenario.get("trigger", {})
    if not isinstance(trigger, dict):
        trigger = {}
    setup_data = trigger.get("setup_data", {})
    if not isinstance(setup_data, dict):
        setup_data = {}

    label = str(setup_data.get("baseline_label", "stable"))
    delete_target = str(setup_data.get("delete_target", "benchmark-results.json"))

    baseline_workspace = workspace / "iteration-workspace"
    baselines_dir = baseline_workspace / "baselines"
    label_dir = baselines_dir / label
    label_dir.mkdir(parents=True, exist_ok=True)

    benchmark_path = label_dir / delete_target
    benchmark_path.write_text(json.dumps({
        "overall_passed": True,
        "evals_passed": 100,
        "failure_ids": [],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    registry_path = baselines_dir / "registry.json"
    registry_path.write_text(json.dumps({
        "baselines": [{
            "label": label,
            "registered_at": "2026-07-15T00:00:00Z",
            "source_report": str(benchmark_path),
            "stored_report": str(benchmark_path),
            "notes": "stress test baseline",
            "summary": {
                "overall_passed": True,
                "evals_passed": 1,
                "evals_total": 1,
            },
        }]
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    benchmark_path.unlink()
    baseline_exists = benchmark_path.exists()
    registry_exists = registry_path.exists()

    config = load_config()
    iter_result = verify_action_module.verify_action(
        text="Run another iteration against the stable baseline and stop on regression.",
        config=config,
        repo_path=workspace,
        check="iteration",
        iteration_workspace=baseline_workspace,
    )
    iter_summary = str(iter_result.get("summary", ""))
    iter_allowed = bool(iter_result.get("allowed"))
    system_detected = "baseline" in iter_summary.lower() and not iter_allowed

    return {
        "actual_caught": system_detected,
        "allowed": iter_allowed,
        "summary": f"baseline deleted={not baseline_exists}, registry exists={registry_exists}, iteration check detected={system_detected}",
        "raw_results": {
            "baseline_exists": baseline_exists,
            "registry_exists": registry_exists,
            "iteration_summary": iter_summary,
        },
        "error": None,
    }


def run_json_parse(
    scenario: dict[str, object],
    workspace: Path,
) -> dict[str, object]:
    """执行 json_parse 类场景（损坏 JSON 解析）

    参数:
        scenario: 场景 JSON dict
        workspace: 临时工作区路径

    返回:
        执行结果 dict，含 actual_caught / parse_error / error_type
    """
    trigger = scenario.get("trigger", {})
    if not isinstance(trigger, dict):
        trigger = {}
    setup_data = trigger.get("setup_data", {})
    if not isinstance(setup_data, dict):
        setup_data = {}

    corrupt_content = str(setup_data.get("corrupt_content", "{invalid json}"))
    corrupt_path = workspace / "corrupt-benchmark.json"
    corrupt_path.write_text(corrupt_content, encoding="utf-8")

    try:
        json.loads(corrupt_path.read_text(encoding="utf-8"))
        return {
            "actual_caught": False,
            "allowed": None,
            "summary": "corrupt JSON was parsed without error (unexpected)",
            "parse_error": False,
            "error_type": None,
            "error": None,
        }
    except json.JSONDecodeError as exc:
        return {
            "actual_caught": True,
            "allowed": None,
            "summary": f"JSONDecodeError caught: {exc}",
            "parse_error": True,
            "error_type": "JSONDecodeError",
            "error": None,
        }


def run_routing_tier_selection(
    scenario: dict[str, object],
    workspace: Path,
) -> dict[str, object]:
    """执行 routing_tier_selection 类场景（测试 select_runtime_tier 边界条件）

    参数:
        scenario: 场景 JSON dict
        workspace: 临时工作区路径

    返回:
        执行结果 dict，含 actual_caught / selected_tier / expected_tier / evidence
    """
    trigger = scenario.get("trigger", {})
    if not isinstance(trigger, dict):
        trigger = {}
    setup_data = trigger.get("setup_data", {})
    if not isinstance(setup_data, dict):
        setup_data = {}

    spawn_supported = bool(setup_data.get("spawn_supported", False))
    wait_supported = bool(setup_data.get("wait_supported", False))
    merge_supported = bool(setup_data.get("merge_supported", False))
    create_session_supported = bool(setup_data.get("create_session_supported", False))
    kill_session_supported = bool(setup_data.get("kill_session_supported", False))
    restart_session_supported = bool(setup_data.get("restart_session_supported", False))
    expected_tier = str(setup_data.get("expected_tier", "soft_orchestration_only"))
    run_smoke = bool(setup_data.get("run_smoke_test", True))

    host_caps = route_request.HostCapabilities(
        spawn_supported=spawn_supported,
        wait_supported=wait_supported,
        merge_supported=merge_supported,
        create_session_supported=create_session_supported,
        kill_session_supported=kill_session_supported,
        restart_session_supported=restart_session_supported,
        evidence_source="declared",
    )

    try:
        result = route_request.select_runtime_tier(
            candidate_runtime_claim="real_subagent_runtime",
            candidate_multi_session_claim="single_backend_multi_session",
            host_capabilities=host_caps,
            run_smoke_test=run_smoke,
        )
        selected_tier = result["runtime_claim"]
        actual_caught = selected_tier == expected_tier
        return {
            "actual_caught": actual_caught,
            "allowed": actual_caught,
            "summary": f"selected={selected_tier}, expected={expected_tier}, downgraded_from={result['downgraded_from']}",
            "selected_tier": selected_tier,
            "expected_tier": expected_tier,
            "evidence": result["evidence"],
            "error": None,
        }
    except Exception as exc:
        return {
            "actual_caught": False,
            "allowed": None,
            "summary": f"select_runtime_tier raised: {exc}",
            "selected_tier": None,
            "expected_tier": expected_tier,
            "evidence": None,
            "error": repr(exc),
        }


def search_callers(
    function_name: str,
    search_paths: list[Path],
    repo_root: Path,
    require_rg: bool = False,
    fallback_grep: bool = True,
) -> tuple[list[str], str]:
    """搜索函数调用方，优先使用 rg，fallback 到 Python re 模块

    参数:
        function_name: 要搜索的函数名
        search_paths: 搜索路径列表
        repo_root: 仓库根路径（用于生成相对路径）
        require_rg: True 时无 rg 抛 RuntimeError，不 fallback
        fallback_grep: True 时无 rg 使用 Python re 模块搜索

    返回:
        (callers_found, search_engine) — callers 为相对路径列表，engine 为 'rg' / 'python-re' / 'none'
    """
    if not function_name:
        return [], "none"

    rg_available = shutil.which("rg") is not None

    if rg_available:
        try:
            cmd = ["rg", "-l", "--no-heading", function_name] + [str(p) for p in search_paths]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                callers = [
                    line.strip().replace(str(repo_root) + "/", "")
                    for line in proc.stdout.strip().split("\n")
                    if line.strip()
                ]
                return callers, "rg"
            return [], "rg"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    if require_rg:
        raise RuntimeError(
            "rg is required (--require-rg set) but not found in PATH; "
            "install ripgrep or use --fallback-grep"
        )

    if not fallback_grep:
        return [], "none"

    callers: list[str] = []
    pattern = re.compile(re.escape(function_name))
    for search_path in search_paths:
        if not search_path.exists():
            continue
        if search_path.is_file():
            files_to_scan = [search_path]
        else:
            files_to_scan = [
                p for p in search_path.rglob("*")
                if p.is_file() and p.suffix in (".py", ".md", ".json", ".yaml", ".yml")
            ]
        for file_path in files_to_scan:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if pattern.search(content):
                    rel = str(file_path).replace(str(repo_root) + "/", "")
                    if rel not in callers:
                        callers.append(rel)
            except OSError:
                continue

    return callers, "python-re"


def generate_trace_summary(
    scenario: dict[str, object],
    repo_path: Path,
    require_rg: bool = False,
    fallback_grep: bool = True,
) -> dict[str, object]:
    """机器校验 trace_summary（obra 约束：非自报，引用真实文件路径 + caller 列表）

    参数:
        scenario: 场景 JSON dict
        repo_path: 技能根路径
        require_rg: True 时无 rg 抛 RuntimeError
        fallback_grep: True 时无 rg 使用 Python re fallback

    返回:
        trace_summary dict，含 files_verified / callers_found / caller_count / complete / search_engine
    """
    affected_files = scenario.get("affected_files", [])
    if not isinstance(affected_files, list):
        affected_files = []
    affected_function = str(scenario.get("affected_function", ""))

    files_verified: list[dict[str, object]] = []
    for rel_path in affected_files:
        full_path = repo_path / str(rel_path)
        exists = full_path.exists()
        files_verified.append({
            "path": str(rel_path),
            "exists": exists,
            "absolute": str(full_path),
        })

    callers_found, search_engine = search_callers(
        function_name=affected_function,
        search_paths=[repo_path / "scripts", repo_path / "references"],
        repo_root=repo_path,
        require_rg=require_rg,
        fallback_grep=fallback_grep,
    )

    caller_count = len(callers_found)
    all_files_exist = all(bool(f.get("exists")) for f in files_verified)
    complete = all_files_exist and caller_count > 0

    return {
        "files_verified": files_verified,
        "callers_found": callers_found,
        "caller_count": caller_count,
        "all_files_exist": all_files_exist,
        "complete": complete,
        "search_engine": search_engine,
    }


def compute_fix_scope(
    scenario: dict[str, object],
    trace_summary: dict[str, object],
) -> dict[str, object]:
    """计算 fix_scope（root-cause: 修共享函数一次 / symptom: 只修命中 path）

    scope 取场景 hint（语义判断），grep caller_count 做机器验证：
    - root-cause 要求 caller_count > 0（函数存在且有调用方）
    - symptom 无最低 caller 要求（局部修补）

    参数:
        scenario: 场景 JSON dict
        trace_summary: generate_trace_summary 的输出

    返回:
        fix_scope dict，含 scope / hint / validated / caller_count / reason
    """
    caller_count = int(trace_summary.get("caller_count", 0))
    hint = str(scenario.get("fix_scope_hint", ""))
    reason = str(scenario.get("fix_scope_reason", ""))

    scope = hint if hint in ("root-cause", "symptom") else "unknown"

    validated = True
    if scope == "root-cause":
        validated = caller_count > 0

    return {
        "scope": scope,
        "hint": hint,
        "validated": validated,
        "caller_count": caller_count,
        "reason": reason,
    }


def run_scenario(
    scenario: dict[str, object],
    config: dict[str, object],
    workspace: Path,
    require_rg: bool = False,
    fallback_grep: bool = True,
) -> dict[str, object]:
    """执行单个场景，生成完整结果（含 trace_summary + fix_scope）

    参数:
        scenario: 场景 JSON dict
        config: routing 配置
        workspace: 临时工作区路径
        require_rg: True 时无 rg 抛 RuntimeError
        fallback_grep: True 时无 rg 使用 Python re fallback

    返回:
        场景结果 dict
    """
    scenario_id = str(scenario.get("scenario_id", "unknown"))
    trigger = scenario.get("trigger", {})
    if not isinstance(trigger, dict):
        trigger = {}
    method = str(trigger.get("method", ""))
    expected = scenario.get("expected", {})
    if not isinstance(expected, dict):
        expected = {}
    expected_caught = bool(expected.get("caught", False))

    scenario_workspace = workspace / scenario_id
    scenario_workspace.mkdir(parents=True, exist_ok=True)

    if method == "verify_action_check":
        exec_result = run_verify_action_check(scenario, config, scenario_workspace)
    elif method == "circuit_breaker_api":
        exec_result = run_circuit_breaker_api(scenario, scenario_workspace)
    elif method == "file_operation":
        exec_result = run_file_operation(scenario, scenario_workspace)
    elif method == "json_parse":
        exec_result = run_json_parse(scenario, scenario_workspace)
    elif method == "routing_tier_selection":
        exec_result = run_routing_tier_selection(scenario, scenario_workspace)
    else:
        exec_result = {
            "actual_caught": False,
            "allowed": None,
            "summary": f"unknown trigger method: {method}",
            "error": f"unsupported method: {method}",
        }

    trace_summary = generate_trace_summary(
        scenario, SKILL_DIR,
        require_rg=require_rg,
        fallback_grep=fallback_grep,
    )
    fix_scope = compute_fix_scope(scenario, trace_summary)

    actual_caught = bool(exec_result.get("actual_caught", False))
    vulnerability_found = expected_caught and not actual_caught
    false_positive = not expected_caught and actual_caught

    if vulnerability_found:
        status = "failed"
    elif false_positive:
        status = "failed"
    elif not trace_summary.get("complete", False):
        status = "failed"
    elif exec_result.get("error"):
        status = "failed"
    elif not expected_caught and not actual_caught:
        status = "correctly_not_caught"
    else:
        status = "passed"

    return {
        "scenario_id": scenario_id,
        "description": str(scenario.get("description", "")),
        "target_layer": str(scenario.get("target_layer", "")),
        "failure_type": str(scenario.get("failure_type", "")),
        "method": method,
        "expected_caught": expected_caught,
        "actual_caught": actual_caught,
        "vulnerability_found": vulnerability_found,
        "status": status,
        "exec_summary": str(exec_result.get("summary", "")),
        "exec_error": exec_result.get("error"),
        "trace_summary": trace_summary,
        "fix_scope": fix_scope,
    }


def run_all_scenarios(
    workspace: Path,
    require_rg: bool = False,
    fallback_grep: bool = True,
) -> dict[str, object]:
    """加载并执行全部压测场景，聚合结果

    参数:
        workspace: 临时工作区路径
        require_rg: True 时无 rg 抛 RuntimeError
        fallback_grep: True 时无 rg 使用 Python re fallback

    返回:
        聚合结果 dict，含 scenarios / summary / fix_scope_root_cause_ratio
    """
    config = load_config()
    scenarios = load_all_scenarios()

    results = []
    for scenario in scenarios:
        result = run_scenario(
            scenario, config, workspace,
            require_rg=require_rg,
            fallback_grep=fallback_grep,
        )
        results.append(result)

    total = len(results)
    vulnerabilities = sum(1 for r in results if r.get("vulnerability_found"))
    passed = sum(1 for r in results if r.get("status") == "passed")
    correctly_not_caught = sum(1 for r in results if r.get("status") == "correctly_not_caught")
    failed = sum(1 for r in results if r.get("status") == "failed")
    trace_incomplete = sum(
        1 for r in results if not bool((r.get("trace_summary") or {}).get("complete"))
    )

    root_cause_count = sum(
        1
        for r in results
        if r.get("fix_scope", {}).get("scope") == "root-cause"
        and bool(r.get("fix_scope", {}).get("validated"))
    )
    fix_scope_root_cause_ratio = root_cause_count / total if total > 0 else 0.0

    count_ok = total == EXPECTED_SCENARIO_COUNT
    root_cause_ratio_ok = fix_scope_root_cause_ratio >= MIN_ROOT_CAUSE_RATIO
    gate_ok = (
        count_ok
        and failed == 0
        and correctly_not_caught == 0
        and trace_incomplete == 0
        and root_cause_ratio_ok
    )

    if not gate_ok:
        scenario_outcome = "semantic_error"
    else:
        scenario_outcome = "all_scenarios_passed"

    consistency_error = ""
    if scenario_outcome == "all_scenarios_passed" and failed > 0:
        consistency_error = "scenario_outcome=all_scenarios_passed 但存在 status=failed 场景，语义不一致"

    return {
        "ok": gate_ok,
        "total_scenarios": total,
        "expected_scenario_count": EXPECTED_SCENARIO_COUNT,
        "scenario_count_ok": count_ok,
        "vulnerabilities_found": vulnerabilities,
        "scenarios_passed": passed,
        "scenarios_correctly_not_caught": correctly_not_caught,
        "scenarios_failed": failed,
        "trace_incomplete": trace_incomplete,
        "scenario_outcome": scenario_outcome,
        "scenario_outcome_consistency_error": consistency_error,
        "fix_scope_root_cause_ratio": round(fix_scope_root_cause_ratio, 4),
        "min_root_cause_ratio": MIN_ROOT_CAUSE_RATIO,
        "root_cause_ratio_ok": root_cause_ratio_ok,
        "scenarios": results,
    }


def render_markdown_report(result: dict[str, object]) -> str:
    """渲染压测报告为 Markdown

    参数:
        result: run_all_scenarios 的输出

    返回:
        Markdown 格式报告字符串
    """
    lines: list[str] = []
    lines.append("# P2-15 压测报告")
    lines.append("")
    lines.append(f"- 场景总数: {result.get('total_scenarios', 0)}")
    lines.append(f"- 通过 (passed): {result.get('scenarios_passed', 0)}")
    lines.append(f"- 正确未捕获 (correctly_not_caught): {result.get('scenarios_correctly_not_caught', 0)}")
    lines.append(f"- 失败 (failed): {result.get('scenarios_failed', 0)}")
    lines.append(f"- 漏洞发现: {result.get('vulnerabilities_found', 0)}")
    lines.append(f"- trace 不完整: {result.get('trace_incomplete', 0)}")
    lines.append(f"- 场景总览: {result.get('scenario_outcome', '')}")
    if result.get("scenario_outcome_consistency_error"):
        lines.append(f"- **一致性错误**: {result.get('scenario_outcome_consistency_error')}")
    lines.append(f"- fix_scope root-cause 比例: {result.get('fix_scope_root_cause_ratio', 0)}")
    lines.append("")

    scenarios = result.get("scenarios", [])
    if not isinstance(scenarios, list):
        scenarios = []

    for s in scenarios:
        if not isinstance(s, dict):
            continue
        sid = s.get("scenario_id", "")
        status = s.get("status", "")
        target = s.get("target_layer", "")
        ftype = s.get("failure_type", "")
        expected = s.get("expected_caught", False)
        actual = s.get("actual_caught", False)
        vuln = s.get("vulnerability_found", False)
        ts = s.get("trace_summary", {})
        if not isinstance(ts, dict):
            ts = {}
        fs = s.get("fix_scope", {})
        if not isinstance(fs, dict):
            fs = {}

        lines.append(f"## {sid}")
        lines.append(f"- **状态**: {status}")
        lines.append(f"- **目标层**: {target}")
        lines.append(f"- **失败类型**: {ftype}")
        lines.append(f"- **预期拦截**: {expected} / **实际拦截**: {actual}")
        if vuln:
            lines.append(f"- **漏洞**: 是（系统未拦截预期失败）")
        lines.append(f"- **trace_summary**: complete={ts.get('complete', False)}, caller_count={ts.get('caller_count', 0)}")
        callers = ts.get("callers_found", [])
        if isinstance(callers, list) and callers:
            lines.append(f"  - callers: {', '.join(callers)}")
        lines.append(f"- **fix_scope**: {fs.get('scope', '')} (hint={fs.get('hint', '')}, validated={fs.get('validated', False)})")
        lines.append(f"- **执行摘要**: {s.get('exec_summary', '')}")
        if s.get("exec_error"):
            lines.append(f"- **错误**: {s.get('exec_error')}")
        lines.append("")

    return "\n".join(lines)


def self_test() -> int:
    """自测：验证场景加载 + trace_summary 生成 + fix_scope 计算 + rg/grep fallback

    返回:
        0 表示通过，1 表示失败
    """
    failures: list[str] = []

    scenarios = load_all_scenarios()
    if len(scenarios) != 12:
        failures.append(f"expected 12 scenarios, got {len(scenarios)}")

    scenario_ids = [str(s.get("scenario_id", "")) for s in scenarios]
    expected_ids = {
        "frontend-backend-contract-mismatch",
        "worker-self-pass",
        "lead-skips-verifier",
        "verifier-always-pass",
        "baseline-deleted",
        "json-corrupt",
        "resume-plan-drift",
        "routing-tier-selection-boundary",
        "routing-soft-fallback-downgrade",
        "routing-circuit-breaker-escalation",
        "drill-multi-session-lifecycle",
        "drill-soft-orchestration-degradation",
    }
    if set(scenario_ids) != expected_ids:
        failures.append(f"scenario IDs mismatch: {set(scenario_ids)} != {expected_ids}")

    for s in scenarios:
        ts = generate_trace_summary(s, SKILL_DIR, fallback_grep=True)
        if not ts.get("complete"):
            failures.append(
                f"trace_summary incomplete for {s.get('scenario_id')}: "
                f"files_exist={ts.get('all_files_exist')}, caller_count={ts.get('caller_count')}, "
                f"search_engine={ts.get('search_engine')}"
            )

    test_scenario = scenarios[0] if scenarios else {}
    fs = compute_fix_scope(test_scenario, generate_trace_summary(test_scenario, SKILL_DIR))
    if fs.get("scope") not in ("root-cause", "symptom"):
        failures.append(f"fix_scope scope invalid: {fs.get('scope')}")
    if "validated" not in fs:
        failures.append("fix_scope missing 'validated' field")

    callers, engine = search_callers(
        function_name="verify_action",
        search_paths=[SKILL_DIR / "scripts"],
        repo_root=SKILL_DIR,
        fallback_grep=True,
    )
    if not callers:
        failures.append(f"search_callers fallback returned no callers for verify_action (engine={engine})")
    if engine not in ("rg", "python-re"):
        failures.append(f"search_callers engine should be 'rg' or 'python-re', got '{engine}'")

    try:
        search_callers(
            function_name="verify_action",
            search_paths=[SKILL_DIR / "scripts"],
            repo_root=SKILL_DIR,
            require_rg=True,
            fallback_grep=False,
        )
        if shutil.which("rg") is None:
            failures.append("require_rg=True should raise RuntimeError when rg unavailable")
    except RuntimeError:
        pass

    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        print(f"\nSelf-test FAILED ({len(failures)} assertion(s))")
        return 1

    print("Self-test PASSED: all stress scenario checks valid")
    print(f"  - {len(scenarios)} scenarios loaded")
    print("  - trace_summary machine validation: all files exist + callers found")
    print("  - fix_scope computation: root-cause/symptom correctly determined")
    print("  - search_callers rg/python-re fallback: working")
    return 0


def main() -> None:
    """CLI 入口"""
    parser = argparse.ArgumentParser(
        description="P2-15 多角色失败场景压测脚本"
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="临时工作区路径（默认自动创建临时目录）",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="格式化 JSON 输出",
    )
    parser.add_argument(
        "--markdown",
        default=None,
        help="Markdown 报告输出路径",
    )
    parser.add_argument(
        "--require-rg",
        action="store_true",
        help="强制要求 rg，无 rg 时 fail 而非 fallback",
    )
    parser.add_argument(
        "--fallback-grep",
        action="store_true",
        default=True,
        help="无 rg 时使用 Python re 模块 fallback（默认启用）",
    )
    parser.add_argument(
        "--no-fallback-grep",
        dest="fallback_grep",
        action="store_false",
        help="禁用 Python re fallback，无 rg 时返回空 callers",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行自测",
    )
    args = parser.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if args.workspace:
        workspace = Path(args.workspace).resolve()
        workspace.mkdir(parents=True, exist_ok=True)
    else:
        workspace = Path(tempfile.mkdtemp(prefix="stress-scenarios-"))

    result = run_all_scenarios(
        workspace,
        require_rg=args.require_rg,
        fallback_grep=args.fallback_grep,
    )

    if args.markdown:
        report_path = Path(args.markdown)
        report_path.write_text(render_markdown_report(result), encoding="utf-8")
        result["markdown_report"] = str(report_path)

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if bool(result.get("ok")) else 1)


if __name__ == "__main__":
    main()
