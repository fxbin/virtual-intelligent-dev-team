# Spec Evolution Protocol

## 核心理念

从"静态规则引擎"升级为"自演化系统"。

当前 Verifier 验证"WorkOrder 完成度"(主观判断),扩展为同时验证"规范符合度"(可 diff/grep/断言的客观事实)。当 Verifier 发现规范未覆盖的新 edge case 时,触发 `update_spec.py` 将经验抽取并 Pull Up 到 spec 文件。

## Spec 分类

| 类型 | 说明 | 示例 | 可变性 |
|------|------|------|--------|
| `read-only` | 不可变规范,定义核心契约 | schema 文件、agent 角色定义 | 不可演化 |
| `read-write` | 可演化规范,记录路由规则和约束 | `routing-rules.json`、guardrails | 可通过 update_spec 演化 |

## 触发条件

`update_spec.py` 在以下情况触发:

1. **Verifier 发现 spec_violation 但规范未覆盖**:Worker 产出违反了隐含规范但 `routing-rules.json` 中没有对应条目 → 新增规则
2. **路由误判**:请求被路由到错误的 Lead Agent(如"前端性能优化"被路由到 Java Virtuoso) → 新增 priority_routing_rules 或调整 agent_rules
3. **重复踩坑**:同一类失败模式在 3 次以上 cycle 中出现 → 将经验抽取为 spec 条目

## 安全网

无安全网的重构比不重构更危险。spec 更新必须满足:

1. **Git 版本化**:每次 spec 更新走 git commit,可 review、可回滚
2. **check 守护**:更新后必须跑 `quick_validate` 确认不破坏现有契约
3. **增量更新**:一次只更新一条规则,不做批量重构
4. **可追溯**:spec 更新记录包含 `{trigger_case, rule_added, commit_hash, timestamp}`

## update_spec.py 接口

```bash
python scripts/update_spec.py \
  --trigger-case "<描述触发场景>" \
  --spec-file routing-rules.json \
  --rule-type priority_routing_rules \
  --rule '{"agent": "World-Class Product Architect", "any_keywords": ["前端性能优化"], "exclude_if_any_keywords": []}' \
  --reason "前端性能优化被误路由到 Java Virtuoso,新增规则排除" \
  --dry-run
```

参数说明:

- `--trigger-case`:触发场景描述(必填)
- `--spec-file`:目标 spec 文件(默认 routing-rules.json)
- `--rule-type`:规则类型(priority_routing_rules / assistant_routing_rules / agent_rules / process_skill_rules)
- `--rule`:JSON 格式的规则内容
- `--reason`:更新理由
- `--dry-run`:只输出 diff,不实际写入

## Verifier 验收对象变更

Verifier 的验收从单一维度扩展为双维度:

| 维度 | 验收对象 | verdict | 性质 |
|------|----------|---------|------|
| WorkOrder 完成度 | Worker 产出是否满足 WorkOrder 验收标准 | pass / fail / hold | 主观判断 |
| 规范符合度 | Worker 产出是否符合 routing-rules.json 规范 | spec_violation(违规时) | 客观事实 |

spec_violation 的 RemediationPatch 必须引用具体规范条目:`"违反 spec X,参见 routing-rules.json#Y"`。

## 与 Hook 自动注入的关系

spec 通过 hook 自动注入到 Worker 上下文。在当前阶段,Worker 需要手动读取 routing-rules.json 相关条目,hook 落地后由其自动完成。

## 第一个失败测试

验证 spec 自更新是否生效的测试:

1. 给定新 edge case(如"前端性能优化"被误路由到 Java Virtuoso)
2. 触发 `update_spec.py`
3. 断言:`routing-rules.json` 含新规则
4. 断言:后续相同请求被正确路由到 World-Class Product Architect
