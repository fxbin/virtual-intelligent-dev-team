#!/usr/bin/env python3
"""observability_config.py — 可观测性协议常量的唯一 source of truth。

契约来源: references/observability-protocol.md
所有 telemetry / drift / SLO 相关常量集中在此文件，scripts/emit_telemetry.py 与
scripts/inspect_decision_log.py 通过 import 引用，避免硬编码漂移。

author: fxbin
"""

from __future__ import annotations

# 六个 closure + verifier 子图枚举（与 observability-protocol.md §5.1 对齐）
LAYER_VALUES: frozenset[str] = frozenset({
    "planning",
    "routing",
    "delivery",
    "iteration",
    "release",
    "drill",
    "verifier",
})

# outcome 枚举（与 observability-protocol.md §5.1 outcome 字段对齐）
OUTCOME_VALUES: frozenset[str] = frozenset({"success", "failure", "held", "degraded"})

# breaker 状态枚举（与 observability-protocol.md §5.1 breaker_state_* 字段对齐）
BREAKER_STATES: frozenset[str] = frozenset({"closed", "open", "half_open"})

# drift 阈值（与 observability-protocol.md §4.2 对齐）
DRIFT_WARN_THRESHOLD: float = 0.30
DRIFT_CRITICAL_THRESHOLD: float = 0.50

# 默认采样率（与 observability-protocol.md §4.3 对齐）
DEFAULT_SAMPLING_RATE: float = 1.0

# 每层 SLO 阈值（单位：秒，与 observability-protocol.md §3 对齐）
SLO_LATENCY_TARGETS: dict[str, float] = {
    "planning": 30.0,
    "routing": 10.0,
    "delivery": 120.0,
    "iteration": 90.0,
    "release": 60.0,
    "drill": 300.0,
    "verifier": 15.0,
}

# p99 滚动窗口大小（与 observability-protocol.md §3 "最近 20 次" 对齐）
P99_WINDOW_SIZE: int = 20

# 窗口内最小样本数，低于此值 SLO 标 insufficient_data
P99_MIN_SAMPLES: int = 5

# Delivery 层重试上限（与 observability-protocol.md §3 重试上限对齐）
DELIVERY_MAX_RETRIES: int = 2
