# Circuit Breaker Protocol

脚本层 circuit breaker,在 LLM context 之外执行,LLM 无法绕过。

## 四要素

1. **ExternalCounter** — 脚本侧计数器,记录连续失败次数,状态持久化到 `.vidt/harness/breaker-state.json`
2. **HardGate** — 达到阈值后 hard exit(退出码 1),LLM 无法绕过
3. **EscalationSink** — breaker open 时写入 `.vidt/harness/escalation-queue.jsonl`
4. **HalfOpenProbe** — cooldown 后允许一个试探请求,成功才恢复 closed

## 状态机

```text
closed --(连续失败达到阈值)--> open
open --(cooldown 过后)--> half_open
half_open --(探针成功)--> closed
half_open --(探针失败)--> open
```

## 配置

配置文件:`references/circuit-breaker-config.json`

每层配置:
- `max_consecutive_failures`: 连续失败次数阈值
- `cooldown_seconds`: open 到 half_open 的冷却时间
- `escalation_sink_path`: escalation 队列文件路径

## 信号源

breaker 的失败信号来自可观测的脚本层事件:

- file handoff 文件校验失败(P0-1 的 `verify_action.py --check file-handoff` 返回 `allowed: false`)
- Verifier verdict 为 `fail` 或 `spec_violation`
- 路由返回空 lead_agent 或 confidence 为 0

信号源必须是 1.0 层确定性事实(脚本可断言),不是 LLM 主观判断。

## CLI 接口

```bash
# 检查 breaker 状态
python scripts/circuit_breaker.py --check verifier

# 记录失败
python scripts/circuit_breaker.py --record-failure verifier --reason "file handoff missing"

# 记录成功(重置计数器)
python scripts/circuit_breaker.py --record-success verifier

# 自测
python scripts/circuit_breaker.py --self-test
```

## 可观测性

breaker 状态转移必须可 assert:

- 计数器变化:`consecutive_failures` 递增
- breaker flag 翻转:`state` 从 `closed` 到 `open`
- metric 写入:escalation 队列文件有新条目
- 状态文件:`.vidt/harness/breaker-state.json` 可读取

## 与 verify_action.py 的集成

`verify_action.py` 在执行 check 前先检查对应层的 breaker 状态:

- breaker open → 返回 `allowed: false`,不执行 check
- breaker closed/half_open → 正常执行 check

集成方式:verify_action.py 调用 `circuit_breaker.py --check <layer>`,根据返回的 `allowed` 字段决定是否继续。

## 不做什么

- 不把 breaker 放在 LLM context 内(同一 context 内的 breaker 是 wishful thinking)
- 不用 breaker 替代 Verifier(breaker 只管"是否允许继续",Verifier 管"产出是否合格")
- 不在 soft 模式下假装真 bulkhead(breaker 是诚实的第一步,不是完整隔离)
