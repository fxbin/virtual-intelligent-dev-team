# Workspace Journal 协议

> **来源**:Trellis / Kelsey / Harrison R5 共识
> **用途**:事件流持久化(append-only + 因果链 + replay),替代纯状态快照
> **核心区别**:journal 是 event sourcing(事件流),不是 state snapshot(状态快照)
> **与 P1-10 的关系**:P1-10 原 durable progress ledger 升级为 journal 模式

---

## 一、Journal Schema

每条 journal entry 是一个 append-only 事件:

```json
{
  "timestamp": "<ISO 8601>",
  "agent": "<角色名,如 Lead/Worker/Verifier>",
  "action": "<动作,如 route/implement/verify/ship>",
  "reason": "<动作理由>",
  "spec_ref": "<引用的 spec 条目,如 routing-rules.json#java-virtuoso>",
  "prev_hash": "<上一条 entry 的 hash,形成因果链>",
  "layer": "<所属层,如 planning/routing/delivery/iteration/release>",
  "state_snapshot": "<动作后的 state 快照(可选)>"
}
```

### 字段说明

| 字段 | 必填 | 含义 |
|------|------|------|
| timestamp | 是 | 事件发生时间(UTC) |
| agent | 是 | 执行动作的角色 |
| action | 是 | 动作类型 |
| reason | 是 | 为什么执行这个动作 |
| spec_ref | 否 | 引用的 spec 条目(可追溯) |
| prev_hash | 是 | 上一条 entry 的 SHA-256 hash(因果链) |
| layer | 否 | 所属闭环或子图(planning / routing / delivery / iteration / release / drill / verifier) |
| state_snapshot | 否 | 动作后的 state 快照(用于快速恢复) |

### 因果链

- 第一条 entry 的 `prev_hash` = `"genesis"`(创世条目)
- 后续每条 entry 的 `prev_hash` = 上一条 entry 的 hash
- hash 计算方式:`SHA-256(timestamp + agent + action + reason + spec_ref + prev_hash)`
- 因果链保证 journal 不可篡改(修改任何 entry 会导致后续 hash 不匹配)

---

## 二、Namespace 分类(Harrison)

| Namespace | 类型 | 含义 | 示例 |
|-----------|------|------|------|
| read-write | journal 累积变形 | 随事件流演化的状态 | 当前 route decision、当前 cycle count |
| read-only | spec 不变形 | 不可变的规范 | routing-rules.json、completion-evidence.schema.json |

### read-write namespace

- 存储在 journal 中,通过 replay 重建
- 每次 agent 操作都会追加新 entry
- compaction 后旧 entry 可归档,但不可修改

### read-only namespace

- 存储在 spec 文件中(routing-rules.json 等)
- 只通过 `update_spec.py`(P0-17)更新,有 git 版本化
- journal 中的 `spec_ref` 字段引用 read-only namespace 的条目

---

## 三、Journal 追加流程

```python
def append_journal(journal_path, agent, action, reason, spec_ref=None, layer=None):
    """追加一条 journal entry"""
    entries = load_journal(journal_path)
    prev_hash = entries[-1]["hash"] if entries else "genesis"
    entry = {
        "timestamp": now_iso(),
        "agent": agent,
        "action": action,
        "reason": reason,
        "spec_ref": spec_ref or "",
        "prev_hash": prev_hash,
        "layer": layer or "",
    }
    entry["hash"] = compute_hash(entry)
    entries.append(entry)
    save_journal(journal_path, entries)
    return entry
```

---

## 四、Journal Replay 流程

```python
def replay_journal(journal_path, target_timestamp=None):
    """从 journal 重建任意时间点的状态"""
    entries = load_journal(journal_path)
    state = {}
    for entry in entries:
        if target_timestamp and entry["timestamp"] > target_timestamp:
            break
        apply_entry_to_state(state, entry)
    return state
```

### Replay 用途

- **故障恢复**:pod 重启后,从 journal replay 重建状态(Karpathy 的"pod 重启内存清空"问题)
- **因果追溯**:回答"上一次为什么走 Sentinel 而不是 Trinity"(Kelsey)
- **审计**:检查任意时间点的决策是否符合规范

---

## 五、与现有 memory model 的关系

| 现有 memory tier | journal 中的对应 |
|-----------------|----------------|
| Round Memory | journal 中 `action=implement` 的 entry |
| Self Feedback | journal 中 `action=reflect` 的 entry |
| Open Loops | journal 中 `action=open_loop` / `action=close_loop` 的 entry |
| Distilled Patterns | journal 中 `action=distill` 的 entry |
| Project Memory Lite | journal 的 compaction 后快照 |

### Compaction

- journal 达到一定条目数(如 1000)后触发 compaction
- compaction 保留每个 agent 的最新状态 + 所有 `spec_ref` 条目
- compaction 后的 journal 只包含 compaction 快照 + 后续新 entry
- compaction 前的 journal 归档到 `.vidt/harness/journal-archive/`

---

## 六、与 State Schema 的关系(P1-7)

- journal 是事件流,event sourcing
- state schema(`state-schema-spec.md`)是状态快照
- state 可从 journal replay 重建
- state schema 中的 `shared` 字段对应 journal 的 compaction 快照

---

## 七、与 Hook 注入的关系(P1-19)

- journal 是 hook 注入的 memory store
- hook 注入时从 journal replay 获取当前 state
- hook 注入的 spec 条目通过 `spec_ref` 字段可追溯
