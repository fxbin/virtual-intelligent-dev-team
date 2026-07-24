#!/usr/bin/env python3
"""脚本层 circuit breaker。

实现四要素:
1. ExternalCounter — 脚本侧计数器,不进 prompt,记连续失败次数
2. HardGate — 达到阈值后 hard exit,LLM 无法绕过
3. EscalationSink — 写入 escalation 队列文件
4. HalfOpenProbe — cooldown 后放一个试探请求,绿了才恢复
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG_PATH = SKILL_DIR / "references" / "circuit-breaker-config.json"
DEFAULT_STATE_DIR = Path(".vidt/harness")
DEFAULT_STATE_FILE = DEFAULT_STATE_DIR / "breaker-state.json"
DEFAULT_ESCALATION_SINK = DEFAULT_STATE_DIR / "escalation-queue.jsonl"

BREAKER_STATES = frozenset({"closed", "open", "half_open"})


class CircuitBreaker:
    """脚本层 circuit breaker,状态持久化到文件,LLM 无法绕过。"""

    def __init__(
        self,
        config_path: Path | None = None,
        state_file: Path | None = None,
        escalation_sink: Path | None = None,
    ) -> None:
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.state_file = state_file or DEFAULT_STATE_FILE
        self.escalation_sink = escalation_sink or DEFAULT_ESCALATION_SINK
        self._state_load_error: str | None = None
        self._config: dict[str, object] = self._load_config()
        self._state: dict[str, object] = self._load_state()

    def _load_config(self) -> dict[str, object]:
        if not self.config_path.exists():
            return {"layers": {}}
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _load_state(self) -> dict[str, object]:
        if not self.state_file.exists():
            return {"layers": {}}
        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict) or not isinstance(payload.get("layers"), dict):
                raise ValueError("breaker state must be an object with a layers object")
            return payload
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            self._state_load_error = f"{type(exc).__name__}: {exc}"
            return {"layers": {}}

    def _require_healthy_state(self) -> None:
        if self._state_load_error is not None:
            raise RuntimeError(
                f"breaker state is unreadable; repair or remove '{self.state_file}' explicitly: "
                f"{self._state_load_error}"
            )

    def _save_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open("w", encoding="utf-8") as f:
            json.dump(self._state, f, ensure_ascii=False, indent=2)

    def _get_layer_config(self, layer: str) -> dict[str, object]:
        layers = self._config.get("layers", {})
        if not isinstance(layers, dict):
            return {}
        layer_config = layers.get(layer, {})
        return layer_config if isinstance(layer_config, dict) else {}

    def _get_layer_state(self, layer: str) -> dict[str, object]:
        layers = self._state.setdefault("layers", {})
        if not isinstance(layers, dict):
            layers = {}
            self._state["layers"] = layers
        if layer not in layers:
            layers[layer] = {
                "state": "closed",
                "consecutive_failures": 0,
                "last_failure_time": None,
                "last_failure_reason": "",
                "opened_at": None,
                "half_open_probe_sent": False,
            }
        return layers[layer]

    def _write_escalation(self, layer: str, reason: str) -> None:
        """写入 escalation 队列文件(EscalationSink)"""
        self.escalation_sink.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "layer": layer,
            "reason": reason,
            "breaker_state": "open",
        }
        with self.escalation_sink.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_state(self, layer: str) -> dict[str, object]:
        """读取指定层的 breaker 状态"""
        if self._state_load_error is not None:
            return {
                "state": "open",
                "consecutive_failures": 0,
                "fail_closed": True,
                "load_error": self._state_load_error,
            }
        return dict(self._get_layer_state(layer))

    def check(self, layer: str) -> dict[str, object]:
        """检查指定层的 breaker 状态,返回是否允许通过(HardGate)"""
        if self._state_load_error is not None:
            return {
                "allowed": False,
                "state": "open",
                "layer": layer,
                "reason": (
                    f"Breaker state is unreadable and therefore fails closed: "
                    f"{self._state_load_error}"
                ),
                "consecutive_failures": 0,
                "fail_closed": True,
            }
        layer_state = self._get_layer_state(layer)
        current_state = str(layer_state.get("state", "closed"))
        now = time.time()

        if current_state == "open":
            opened_at = layer_state.get("opened_at")
            if opened_at is not None:
                cooldown = float(self._get_layer_config(layer).get("cooldown_seconds", 300))
                if now - float(opened_at) >= cooldown:
                    layer_state["state"] = "half_open"
                    layer_state["half_open_probe_sent"] = False
                    self._save_state()
                    current_state = "half_open"

        if current_state == "open":
            return {
                "allowed": False,
                "state": "open",
                "layer": layer,
                "reason": f"Breaker is open for layer '{layer}'",
                "consecutive_failures": int(layer_state.get("consecutive_failures", 0)),
            }

        if current_state == "half_open":
            probe_sent = bool(layer_state.get("half_open_probe_sent", False))
            if probe_sent:
                return {
                    "allowed": False,
                    "state": "half_open",
                    "layer": layer,
                    "reason": f"Half-open probe already sent for layer '{layer}'",
                    "consecutive_failures": int(layer_state.get("consecutive_failures", 0)),
                }
            layer_state["half_open_probe_sent"] = True
            self._save_state()
            return {
                "allowed": True,
                "state": "half_open",
                "layer": layer,
                "reason": "Half-open probe allowed",
                "consecutive_failures": int(layer_state.get("consecutive_failures", 0)),
            }

        return {
            "allowed": True,
            "state": "closed",
            "layer": layer,
            "reason": "Breaker is closed",
            "consecutive_failures": int(layer_state.get("consecutive_failures", 0)),
        }

    def record_failure(self, layer: str, reason: str) -> dict[str, object]:
        """记录失败(ExternalCounter),可能触发 breaker open"""
        self._require_healthy_state()
        layer_state = self._get_layer_state(layer)
        max_failures = int(self._get_layer_config(layer).get("max_consecutive_failures", 3))
        current = int(layer_state.get("consecutive_failures", 0))
        current += 1
        layer_state["consecutive_failures"] = current
        layer_state["last_failure_time"] = time.time()
        layer_state["last_failure_reason"] = reason

        if current >= max_failures:
            layer_state["state"] = "open"
            layer_state["opened_at"] = time.time()
            layer_state["half_open_probe_sent"] = False
            self._save_state()
            self._write_escalation(layer, reason)
            return {
                "triggered": True,
                "state": "open",
                "layer": layer,
                "consecutive_failures": current,
                "max_failures": max_failures,
                "reason": reason,
            }

        self._save_state()
        return {
            "triggered": False,
            "state": str(layer_state.get("state", "closed")),
            "layer": layer,
            "consecutive_failures": current,
            "max_failures": max_failures,
            "reason": reason,
        }

    def record_success(self, layer: str) -> dict[str, object]:
        """记录成功,重置计数器(HalfOpenProbe 恢复)"""
        self._require_healthy_state()
        layer_state = self._get_layer_state(layer)
        layer_state["consecutive_failures"] = 0
        layer_state["state"] = "closed"
        layer_state["opened_at"] = None
        layer_state["half_open_probe_sent"] = False
        self._save_state()
        return {
            "state": "closed",
            "layer": layer,
            "consecutive_failures": 0,
        }


def self_test() -> int:
    """自测:注入连续失败 → breaker 应 open → 可观测状态变化"""
    import tempfile

    tmpdir = Path(tempfile.mkdtemp(prefix="cb-self-test-"))
    config_path = tmpdir / "config.json"
    state_file = tmpdir / "state.json"
    escalation_sink = tmpdir / "escalation.jsonl"

    config = {
        "layers": {
            "verifier": {
                "max_consecutive_failures": 3,
                "cooldown_seconds": 1,
                "escalation_sink_path": str(escalation_sink),
            }
        }
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False))

    breaker = CircuitBreaker(
        config_path=config_path,
        state_file=state_file,
        escalation_sink=escalation_sink,
    )

    failures: list[str] = []

    check_before = breaker.check("verifier")
    if not check_before["allowed"]:
        failures.append("FAIL: breaker should be closed initially")

    for i in range(3):
        result = breaker.record_failure("verifier", f"simulated failure {i+1}")
        if i < 2 and result["triggered"]:
            failures.append(f"FAIL: breaker triggered too early at failure {i+1}")

    final_result = breaker.record_failure("verifier", "simulated failure 4")
    if not final_result["triggered"]:
        failures.append("FAIL: breaker should have triggered after 3 failures")

    check_after = breaker.check("verifier")
    if check_after["allowed"]:
        failures.append("FAIL: breaker should be open after triggering")

    if not escalation_sink.exists():
        failures.append("FAIL: escalation sink file should exist")
    else:
        lines = escalation_sink.read_text().strip().split("\n")
        if len(lines) == 0:
            failures.append("FAIL: escalation sink should have at least one entry")

    state_data = json.loads(state_file.read_text())
    verifier_state = state_data.get("layers", {}).get("verifier", {})
    if verifier_state.get("state") != "open":
        failures.append(f"FAIL: state file should show 'open', got '{verifier_state.get('state')}'")
    if verifier_state.get("consecutive_failures", 0) < 3:
        failures.append(f"FAIL: consecutive_failures should be >= 3, got {verifier_state.get('consecutive_failures')}")

    breaker.record_success("verifier")
    check_recovery = breaker.check("verifier")
    if not check_recovery["allowed"]:
        failures.append("FAIL: breaker should be closed after record_success")

    corrupt_state = tmpdir / "corrupt-state.json"
    corrupt_state.write_text("{not-json", encoding="utf-8")
    corrupt_breaker = CircuitBreaker(
        config_path=config_path,
        state_file=corrupt_state,
        escalation_sink=escalation_sink,
    )
    corrupt_check = corrupt_breaker.check("verifier")
    if corrupt_check["allowed"] or corrupt_check.get("state") != "open":
        failures.append("FAIL: corrupt breaker state must fail closed")

    import shutil
    shutil.rmtree(tmpdir)

    if failures:
        for f in failures:
            print(f"  {f}")
        print(f"\nSelf-test FAILED ({len(failures)} assertion(s))")
        return 1

    print("Self-test PASSED: all assertions hold")
    print("  - ExternalCounter: consecutive failures counted correctly")
    print("  - HardGate: breaker open blocks check()")
    print("  - EscalationSink: escalation queue file written")
    print("  - HalfOpenProbe: record_success resets to closed")
    print("  - Corrupt state: unreadable state fails closed")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Circuit breaker for virtual-intelligent-dev-team.")
    parser.add_argument("--check", help="Check breaker state for a layer.")
    parser.add_argument("--record-failure", help="Record a failure for a layer.")
    parser.add_argument("--record-success", help="Record a success for a layer.")
    parser.add_argument("--reason", help="Failure reason for --record-failure.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Config file path.")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE), help="State file path.")
    parser.add_argument("--escalation-sink", default=str(DEFAULT_ESCALATION_SINK), help="Escalation sink path.")
    parser.add_argument("--self-test", action="store_true", help="Run self-test.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.self_test:
        raise SystemExit(self_test())

    breaker = CircuitBreaker(
        config_path=Path(args.config),
        state_file=Path(args.state_file),
        escalation_sink=Path(args.escalation_sink),
    )

    result: dict[str, object]
    if args.check:
        result = breaker.check(args.check)
    elif args.record_failure:
        result = breaker.record_failure(args.record_failure, args.reason or "unspecified")
    elif args.record_success:
        result = breaker.record_success(args.record_success)
    else:
        result = {"ok": False, "error": "No action specified. Use --check/--record-failure/--record-success/--self-test."}

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))

    if isinstance(result, dict) and not result.get("allowed", True):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
