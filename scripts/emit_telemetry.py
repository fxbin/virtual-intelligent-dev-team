#!/usr/bin/env python3
"""emit_telemetry.py — 层间 telemetry 写入器 + intent drift 探针。

契约来源: references/observability-protocol.md
唯一写入 .vidt/metrics/telemetry.jsonl 的脚本。

功能:
1. 记录每层执行的 telemetry（13 必填字段 + 1 可选 known_shortcut）
2. intent drift 探针（drift_score = 3 子分平均）
3. drift_score > 0.50 触发 circuit_breaker.record_failure
4. 采样率 < 1.0 强制 known_shortcut 标注

author: fxbin
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from circuit_breaker import CircuitBreaker
from observability_config import (
    BREAKER_STATES,
    DEFAULT_SAMPLING_RATE,
    DRIFT_CRITICAL_THRESHOLD,
    DRIFT_WARN_THRESHOLD,
    LAYER_VALUES,
    OUTCOME_VALUES,
    SLO_LATENCY_TARGETS,
)

DEFAULT_TELEMETRY_DIR = Path(".vidt/metrics")
DEFAULT_TELEMETRY_FILE = DEFAULT_TELEMETRY_DIR / "telemetry.jsonl"
ABSTRACTION_KEYWORDS_PATH = SCRIPT_DIR / "abstraction_keywords.yaml"

# 向后兼容：常量已在 observability_config 中定义，此处通过 import 暴露
# 外部模块仍可 from emit_telemetry import DRIFT_CRITICAL_THRESHOLD 等

TOKEN_SPLIT_PATTERN = re.compile(r"[^\w]+")


def load_abstraction_keywords(
    config_path: Path = ABSTRACTION_KEYWORDS_PATH,
    lang: str | None = None,
) -> list[str]:
    """从 abstraction_keywords.yaml 加载关键字列表

    参数:
        config_path: yaml 配置路径
        lang: 语言标识（如 'rust'），None 时加载 core 档

    返回:
        关键字列表
    """
    if not config_path.exists():
        return ["class", "def", "module", "config", "interface", "type", "struct", "trait", "enum"]

    try:
        import yaml
    except ImportError:
        return ["class", "def", "module", "config", "interface", "type", "struct", "trait", "enum"]

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if lang and lang in data.get("extended", {}):
        keywords = data["extended"][lang]
    else:
        keywords = data.get("core", [])

    return [str(kw) for kw in keywords] if keywords else ["class", "def", "module", "config"]


def build_abstraction_pattern(keywords: list[str]) -> re.Pattern[str]:
    """根据关键字列表构建 ABSTRACTION_PATTERN 正则

    参数:
        keywords: 关键字列表

    返回:
        编译后的 re.Pattern
    """
    if not keywords:
        keywords = ["class", "def", "module", "config"]
    pattern = r"^\s*(?:" + "|".join(re.escape(kw) for kw in keywords) + r")\s+\w+"
    return re.compile(pattern, re.MULTILINE)


ABSTRACTION_PATTERN = build_abstraction_pattern(load_abstraction_keywords())


def validate_abstraction_keywords_schema(
    config_path: Path = ABSTRACTION_KEYWORDS_PATH,
) -> list[str]:
    """校验 abstraction_keywords.yaml 的 schema 结构

    校验规则：
    1. 文件必须存在
    2. 顶层必须有 version 字段且为非空字符串
    3. 顶层必须有 core 字段且为非空 list
    4. core 中每个元素必须为非空字符串
    5. 顶层必须有 extended 字段且为 dict（可为空）
    6. extended 中每个 value 必须为 list[str]

    参数:
        config_path: yaml 配置路径

    返回:
        错误信息列表，空列表表示通过
    """
    errors: list[str] = []

    if not config_path.exists():
        return [f"abstraction_keywords.yaml not found at {config_path}"]

    try:
        import yaml
    except ImportError:
        return ["PyYAML not installed, cannot validate abstraction_keywords.yaml schema"]

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return [f"abstraction_keywords.yaml YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return ["abstraction_keywords.yaml top-level must be a mapping"]

    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("abstraction_keywords.yaml: 'version' must be a non-empty string")

    core = data.get("core")
    if not isinstance(core, list):
        errors.append("abstraction_keywords.yaml: 'core' must be a list")
    elif not core:
        errors.append("abstraction_keywords.yaml: 'core' must not be empty")
    else:
        for i, item in enumerate(core):
            if not isinstance(item, str) or not item.strip():
                errors.append(
                    f"abstraction_keywords.yaml: core[{i}] must be a non-empty string"
                )

    extended = data.get("extended")
    if extended is None:
        errors.append("abstraction_keywords.yaml: 'extended' field is missing (can be empty dict)")
    elif not isinstance(extended, dict):
        errors.append("abstraction_keywords.yaml: 'extended' must be a mapping")
    else:
        for lang, kws in extended.items():
            if not isinstance(kws, list):
                errors.append(
                    f"abstraction_keywords.yaml: extended.{lang} must be a list"
                )
                continue
            for i, item in enumerate(kws):
                if not isinstance(item, str) or not item.strip():
                    errors.append(
                        f"abstraction_keywords.yaml: extended.{lang}[{i}] must be a non-empty string"
                    )

    return errors


def _utc_now() -> str:
    """返回当前 UTC 时间的 ISO8601 字符串"""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _tokenize(text: str) -> list[str]:
    """将文本切分为关键词列表，过滤长度 < 2 的词"""
    if not text:
        return []
    tokens = TOKEN_SPLIT_PATTERN.split(text)
    return [t for t in tokens if len(t) >= 2]


def _read_file_content(path: Path) -> str:
    """安全读取文件内容，失败返回空串"""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def compute_drift_score(
    work_order_text: str,
    artifact_paths: list[str],
    tool_boundary: str,
    scope: str,
    repo: Path,
) -> tuple[float, dict[str, float]]:
    """计算 intent drift 分数

    drift_score = (keyword_miss_rate + tool_boundary_breach_rate + unrequested_abstraction_rate) / 3

    参数:
        work_order_text: WorkOrder 原始文本
        artifact_paths: 产出文件路径列表
        tool_boundary: 允许的文件目录前缀
        scope: WorkOrder scope 描述（当前用于日志，未参与计算）
        repo: 仓库根路径

    返回:
        (drift_score, sub_scores) — drift_score ∈ [0,1]，sub_scores 含 3 个子分
    """
    keywords = _tokenize(work_order_text)
    if keywords:
        artifact_contents = [
            _read_file_content(repo / p) for p in artifact_paths
        ]
        combined = "\n".join(artifact_contents).lower()
        hit_count = sum(1 for kw in keywords if kw.lower() in combined)
        keyword_miss_rate = 1.0 - (hit_count / len(keywords))
    else:
        keyword_miss_rate = 0.0

    if artifact_paths:
        breach_count = 0
        for p in artifact_paths:
            normalized = p.replace("\\", "/").strip("/")
            boundary = tool_boundary.replace("\\", "/").strip("/")
            if boundary and not normalized.startswith(boundary):
                breach_count += 1
        tool_boundary_breach_rate = breach_count / len(artifact_paths)
    else:
        tool_boundary_breach_rate = 0.0

    if artifact_paths:
        abstraction_count = 0
        for p in artifact_paths:
            content = _read_file_content(repo / p)
            abstraction_count += len(ABSTRACTION_PATTERN.findall(content))
        unrequested_abstraction_rate = min(
            abstraction_count / max(len(artifact_paths), 1),
            1.0,
        )
    else:
        unrequested_abstraction_rate = 0.0

    drift_score = (
        keyword_miss_rate
        + tool_boundary_breach_rate
        + unrequested_abstraction_rate
    ) / 3.0

    sub_scores = {
        "keyword_miss_rate": round(keyword_miss_rate, 4),
        "tool_boundary_breach_rate": round(tool_boundary_breach_rate, 4),
        "unrequested_abstraction_rate": round(unrequested_abstraction_rate, 4),
    }
    return round(drift_score, 4), sub_scores


def emit_telemetry(
    layer: str,
    step_id: str,
    latency_seconds: float,
    outcome: str,
    repo: Path,
    work_order_ref: str = "",
    artifact_ref: str = "",
    drift_score: float = 0.0,
    sampling_rate: float = DEFAULT_SAMPLING_RATE,
    known_shortcut: str = "",
    breaker: CircuitBreaker | None = None,
) -> dict[str, object]:
    """组装并写入一条 telemetry 记录，联动 circuit breaker

    参数:
        layer: 六个 closure 或 verifier 子图之一
        step_id: 步骤唯一标识
        latency_seconds: 该层单次执行耗时
        outcome: success / failure / held / degraded
        repo: 仓库根路径（定位 telemetry.jsonl）
        work_order_ref: 关联 WorkOrder ID
        artifact_ref: 产出文件路径
        drift_score: drift 分数，非 delivery 层强制 0.0
        sampling_rate: 采样率 [0,1]
        known_shortcut: 采样率 < 1.0 时的天花板 + 升级路径标注
        breaker: CircuitBreaker 实例，None 时内部新建

    返回:
        写入的 telemetry 记录 dict
    """
    if layer not in LAYER_VALUES:
        raise ValueError(f"layer must be one of {sorted(LAYER_VALUES)}, got '{layer}'")
    if outcome not in OUTCOME_VALUES:
        raise ValueError(f"outcome must be one of {sorted(OUTCOME_VALUES)}, got '{outcome}'")
    if not 0.0 <= sampling_rate <= 1.0:
        raise ValueError(f"sampling_rate must be in [0,1], got {sampling_rate}")
    if sampling_rate < DEFAULT_SAMPLING_RATE and not known_shortcut:
        raise ValueError("known_shortcut is required when sampling_rate < 1.0")

    if layer != "delivery":
        drift_score = 0.0

    drift_flag = drift_score > DRIFT_WARN_THRESHOLD

    sampled = random.random() < sampling_rate

    if breaker is None:
        breaker = CircuitBreaker()

    state_before = str(breaker.get_state(layer).get("state", "closed"))

    if sampled:
        if drift_score > DRIFT_CRITICAL_THRESHOLD:
            breaker.record_failure(layer, f"intent drift critical (score={drift_score})")
        elif outcome == "failure":
            breaker.record_failure(layer, "layer outcome failure")
        elif outcome == "success":
            breaker.record_success(layer)
    else:
        if outcome == "failure":
            breaker.record_failure(layer, "layer outcome failure (unsampled drift skipped)")
        elif outcome == "success":
            breaker.record_success(layer)

    state_after = str(breaker.get_state(layer).get("state", "closed"))

    record: dict[str, object] = {
        "timestamp": _utc_now(),
        "step_id": step_id,
        "layer": layer,
        "latency_seconds": round(latency_seconds, 4),
        "outcome": outcome,
        "breaker_state_before": state_before,
        "breaker_state_after": state_after,
        "drift_score": round(drift_score, 4),
        "drift_flag": drift_flag,
        "work_order_ref": work_order_ref,
        "artifact_ref": artifact_ref,
        "sampled": sampled,
        "sampling_rate": sampling_rate,
    }
    if sampling_rate < DEFAULT_SAMPLING_RATE:
        record["known_shortcut"] = known_shortcut

    telemetry_file = repo / DEFAULT_TELEMETRY_FILE
    telemetry_file.parent.mkdir(parents=True, exist_ok=True)
    with telemetry_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def self_test() -> int:
    """自测：telemetry 写入 + drift 探针 + breaker 联动 + 采样校验"""
    import tempfile

    tmpdir = Path(tempfile.mkdtemp(prefix="emit-tel-self-test-"))
    failures: list[str] = []

    breaker_config = tmpdir / "breaker-config.json"
    breaker_state = tmpdir / "breaker-state.json"
    escalation_sink = tmpdir / "escalation.jsonl"
    breaker_config.write_text(
        json.dumps({
            "layers": {
                "delivery": {
                    "max_consecutive_failures": 3,
                    "cooldown_seconds": 60,
                    "escalation_sink_path": str(escalation_sink),
                },
                "verifier": {
                    "max_consecutive_failures": 5,
                    "cooldown_seconds": 60,
                    "escalation_sink_path": str(escalation_sink),
                },
            }
        }),
        encoding="utf-8",
    )
    breaker = CircuitBreaker(
        config_path=breaker_config,
        state_file=breaker_state,
        escalation_sink=escalation_sink,
    )

    record = emit_telemetry(
        layer="delivery",
        step_id="step-test-001",
        latency_seconds=12.4,
        outcome="success",
        repo=tmpdir,
        work_order_ref="wo-001",
        artifact_ref="src/auth.py",
        drift_score=0.15,
        breaker=breaker,
    )

    if record["layer"] != "delivery":
        failures.append("FAIL: layer 未正确写入")
    if record["drift_score"] != 0.15:
        failures.append("FAIL: drift_score 未正确写入")
    if record["drift_flag"] is not False:
        failures.append("FAIL: drift_score=0.15 不应触发 drift_flag")
    if record["breaker_state_before"] != "closed":
        failures.append("FAIL: breaker_state_before 应为 closed")
    if record["breaker_state_after"] != "closed":
        failures.append("FAIL: success 后 breaker_state_after 应为 closed")

    telemetry_file = tmpdir / DEFAULT_TELEMETRY_FILE
    if not telemetry_file.exists():
        failures.append("FAIL: telemetry.jsonl 未创建")
    else:
        lines = telemetry_file.read_text(encoding="utf-8").strip().split("\n")
        if len(lines) != 1:
            failures.append(f"FAIL: 应写入 1 条记录，实际 {len(lines)} 条")
        else:
            parsed = json.loads(lines[0])
            for field in (
                "timestamp", "step_id", "layer", "latency_seconds",
                "outcome", "breaker_state_before", "breaker_state_after",
                "drift_score", "drift_flag", "work_order_ref",
                "artifact_ref", "sampled", "sampling_rate",
            ):
                if field not in parsed:
                    failures.append(f"FAIL: 记录缺少必填字段 {field}")

    artifact = tmpdir / "src" / "auth.py"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "class AuthService:\n    def login(self, user, password):\n        pass\n",
        encoding="utf-8",
    )

    drift_score, sub = compute_drift_score(
        work_order_text="实现用户登录功能",
        artifact_paths=["src/auth.py"],
        tool_boundary="src/",
        scope="login",
        repo=tmpdir,
    )
    if not 0.0 <= drift_score <= 1.0:
        failures.append(f"FAIL: drift_score 应在 [0,1]，实际 {drift_score}")
    if "keyword_miss_rate" not in sub:
        failures.append("FAIL: sub_scores 缺少 keyword_miss_rate")
    if "tool_boundary_breach_rate" not in sub:
        failures.append("FAIL: sub_scores 缺少 tool_boundary_breach_rate")
    if "unrequested_abstraction_rate" not in sub:
        failures.append("FAIL: sub_scores 缺少 unrequested_abstraction_rate")

    drift_record = emit_telemetry(
        layer="delivery",
        step_id="step-test-002",
        latency_seconds=45.0,
        outcome="success",
        repo=tmpdir,
        drift_score=0.55,
        breaker=breaker,
    )
    if drift_record["drift_flag"] is not True:
        failures.append("FAIL: drift_score=0.55 应触发 drift_flag")
    state_after_critical = breaker.get_state("delivery")
    if int(state_after_critical.get("consecutive_failures", 0)) < 1:
        failures.append("FAIL: drift_score>0.50 应触发 breaker record_failure")

    try:
        emit_telemetry(
            layer="invalid_layer",
            step_id="step-test-003",
            latency_seconds=1.0,
            outcome="success",
            repo=tmpdir,
            breaker=breaker,
        )
        failures.append("FAIL: 非法 layer 应抛 ValueError")
    except ValueError:
        pass

    try:
        emit_telemetry(
            layer="delivery",
            step_id="step-test-004",
            latency_seconds=1.0,
            outcome="success",
            repo=tmpdir,
            sampling_rate=0.3,
            breaker=breaker,
        )
        failures.append("FAIL: sampling_rate<1.0 无 known_shortcut 应抛 ValueError")
    except ValueError:
        pass

    sampled_record = emit_telemetry(
        layer="delivery",
        step_id="step-test-005",
        latency_seconds=5.0,
        outcome="success",
        repo=tmpdir,
        sampling_rate=0.3,
        known_shortcut="采样率 0.3 会漏掉低频 drift；升级路径：调至 1.0 全量覆盖",
        breaker=breaker,
    )
    if "known_shortcut" not in sampled_record:
        failures.append("FAIL: sampling_rate<1.0 时记录应含 known_shortcut")
    if sampled_record["sampling_rate"] != 0.3:
        failures.append("FAIL: sampling_rate 未正确写入")

    verifier_record = emit_telemetry(
        layer="verifier",
        step_id="step-test-006",
        latency_seconds=3.0,
        outcome="success",
        repo=tmpdir,
        drift_score=0.8,
        breaker=breaker,
    )
    if verifier_record["drift_score"] != 0.0:
        failures.append("FAIL: 非 delivery 层 drift_score 应强制 0.0")

    # schema 校验：默认 abstraction_keywords.yaml 必须通过
    schema_errors = validate_abstraction_keywords_schema()
    if schema_errors:
        failures.append(
            "FAIL: 默认 abstraction_keywords.yaml schema 校验失败: "
            + "; ".join(schema_errors)
        )

    # schema 校验：构造非法 yaml（core 缺失）必须报错
    bad_yaml = tmpdir / "bad-abstraction-keywords.yaml"
    bad_yaml.write_text("version: \"1.0.0\"\nextended: {}\n", encoding="utf-8")
    bad_errors = validate_abstraction_keywords_schema(config_path=bad_yaml)
    if not bad_errors:
        failures.append("FAIL: 缺失 core 字段的 yaml 应报 schema 错误")

    if failures:
        for f in failures:
            print(f"[SELF-TEST] {f}")
        return 1
    print("[SELF-TEST] emit_telemetry.py 全部通过")
    return 0


def main() -> int:
    """CLI 入口"""
    if "--self-test" in sys.argv:
        return self_test()

    if "--validate-schema" in sys.argv:
        errors = validate_abstraction_keywords_schema()
        if errors:
            for e in errors:
                print(f"[ERROR] {e}")
            return 1
        print("[OK] abstraction_keywords.yaml schema 校验通过")
        return 0

    parser = argparse.ArgumentParser(
        description="层间 telemetry 写入器 + intent drift 探针"
    )
    parser.add_argument("--layer", required=True, help="六个 closure 或 verifier 子图之一")
    parser.add_argument("--step-id", required=True, help="步骤唯一标识")
    parser.add_argument("--latency", type=float, required=True, help="该层执行耗时（秒）")
    parser.add_argument("--outcome", required=True, help="success/failure/held/degraded")
    parser.add_argument("--work-order-ref", default="", help="关联 WorkOrder ID")
    parser.add_argument("--artifact-ref", default="", help="产出文件路径")
    parser.add_argument("--drift-score", type=float, default=0.0, help="drift 分数")
    parser.add_argument("--sampling-rate", type=float, default=DEFAULT_SAMPLING_RATE, help="采样率")
    parser.add_argument("--known-shortcut", default="", help="采样率<1.0 时的天花板+升级路径")
    parser.add_argument("--repo", default=".", help="仓库根路径")
    parser.add_argument("--lang", default=None, help="目标语言（如 rust/kotlin/scala，默认加载 core 档）")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    parser.add_argument(
        "--validate-schema",
        action="store_true",
        help="校验 abstraction_keywords.yaml schema 后退出（早期拦截，无需其他必填参数）",
    )
    args = parser.parse_args()

    global ABSTRACTION_PATTERN
    if args.lang:
        keywords = load_abstraction_keywords(lang=args.lang)
        ABSTRACTION_PATTERN = build_abstraction_pattern(keywords)

    if args.self_test:
        return self_test()

    try:
        record = emit_telemetry(
            layer=args.layer,
            step_id=args.step_id,
            latency_seconds=args.latency,
            outcome=args.outcome,
            repo=Path(args.repo).resolve(),
            work_order_ref=args.work_order_ref,
            artifact_ref=args.artifact_ref,
            drift_score=args.drift_score,
            sampling_rate=args.sampling_rate,
            known_shortcut=args.known_shortcut,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
