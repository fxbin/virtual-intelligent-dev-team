# Contract Lock Protocol

> **用途**:前后端 Lead 在 WorkOrder 前必须共同签署 `contract-spec`,防止接口漂移
> **核心约束**:WorkOrder 涉及前后端协作时,contract-spec 文件必须存在且双方签署,否则 hard fail
> **与 P1-5 的关系**:P1-5 contract lock 门禁,解决"前后端接口对不齐"的根因问题

---

## 一、触发条件

当 WorkOrder 满足以下任一条件时,必须执行 contract lock:

- Lead 是前端角色(World-Class Product Architect / Technical Trinity),且任务涉及 API 调用
- Lead 是后端角色(API Contract Sentinel / Java Virtuoso / Data Pipeline Guardian),且任务涉及前端消费的接口
- WorkOrder 的 `input_artifacts` 或 `output_artifacts` 包含 API 端点、schema 或接口定义
- workflow_bundle 是 `plan-first-build` 或 `product-spec-deliver` 且涉及跨端协作

不涉及前后端协作的 WorkOrder(如纯后端重构、纯前端样式调整)可跳过 contract lock。

---

## 二、Contract Spec Schema

`contract-spec` 是前后端共同签署的契约文件,存储在 `.vidt/harness/contract-spec.json`。

```json
{
  "schema_version": "contract-spec/v1",
  "spec_id": "<唯一标识,如 contract-spec-<uuid>>",
  "endpoint": "<API 端点,如 /api/v1/users>",
  "method": "<HTTP 方法,如 GET/POST/PUT/DELETE>",
  "request_schema": {
    "fields": [
      {
        "name": "<字段名>",
        "type": "<类型,如 string/integer/boolean/array/object>",
        "required": true,
        "description": "<字段说明>"
      }
    ]
  },
  "response_schema": {
    "success": {
      "fields": []
    },
    "error": {
      "fields": []
    }
  },
  "error_codes": [
    {
      "code": "<错误码,如 400/404/500>",
      "meaning": "<错误含义>",
      "retryable": false
    }
  ],
  "version": "<语义化版本号,如 1.0.0>",
  "signatures": {
    "frontend_lead": {
      "agent": "<前端 Lead 角色名>",
      "signed_at": "<ISO 8601 时间戳>",
      "accepted": true
    },
    "backend_lead": {
      "agent": "<后端 Lead 角色名>",
      "signed_at": "<ISO 8601 时间戳>",
      "accepted": true
    }
  }
}
```

### 字段约束

| 字段 | 必填 | 约束 |
|------|------|------|
| schema_version | 是 | 固定为 `contract-spec/v1` |
| spec_id | 是 | 全局唯一 |
| endpoint | 是 | 符合 RESTful 路径规范 |
| method | 是 | 枚举值:GET/POST/PUT/PATCH/DELETE |
| request_schema | 是 | 至少包含 1 个 field(可为空数组表示无请求体) |
| response_schema | 是 | 必须包含 success 和 error |
| error_codes | 是 | 至少包含 1 个错误码 |
| version | 是 | 语义化版本号 |
| signatures | 是 | 必须包含 frontend_lead 和 backend_lead,且 accepted 均为 true |

---

## 三、签署流程

```text
1. 后端 Lead 起草 contract-spec(基于 WorkOrder 的接口需求)
2. 前端 Lead 审阅 contract-spec(确认字段、类型、错误码满足前端需求)
3. 前端 Lead 签署(signatures.frontend_lead.accepted = true)
4. 后端 Lead 签署(signatures.backend_lead.accepted = true)
5. 双方签署后,contract-spec 文件锁定,不可单方面修改
6. 如需修改,必须双方重新签署(版本号递增)
```

### 签署顺序

后端先起草 → 前端审阅签署 → 后端确认签署。这确保前端的需求在起草阶段就被考虑,而不是事后发现接口不匹配。

---

## 四、Verifier Gate

contract lock 是 Verifier 的第一道 gate(`acceptance_gates[0]`)。

### 检查逻辑

1. **存在性检查**:contract-spec 文件必须存在
2. **签署完整性检查**:signatures 必须包含 frontend_lead 和 backend_lead
3. **签署有效性检查**:双方的 accepted 必须均为 true
4. **内容一致性检查**:若文件分别声明 `fields.frontend` 与 `fields.backend`,字段名和类型必须完全一致；若使用标准 `contract-spec/v1`,必须提供共享的 `request_schema` 与 `response_schema`
5. **版本一致性检查**:Team Engine 调用方还必须比较 contract-spec 的 version 与 WorkOrder 引用版本；独立 `verify_action.py --check contract-lock` 只验证传入文件自身及双方内容一致性

### 检查结果

| 条件 | verdict | 行为 |
|------|---------|------|
| contract-spec 文件不存在 | fail | hard fail,Worker 不得开始实现 |
| signatures 缺失任一方 | fail | hard fail,要求补签 |
| 任一方 accepted=false | fail | hard fail,要求重新协商 |
| 双方签名通过但字段名/类型不一致 | fail | hard fail,先统一内容再重新签署 |
| 版本不一致 | fail | hard fail,要求重新签署 |
| 全部通过 | pass | Worker 可开始实现 |

---

## 五、与现有协议的关系

| 现有协议 | contract lock 的补充 |
|----------|---------------------|
| Team Engine Lite | contract-spec 是 WorkOrder 的前置产物,Verifier 第一道 gate |
| Worker/Verifier Cycle | Verifier 在 `verifying` 阶段首先检查契约符合度 |
| spec-violation check | contract-spec 是 spec-violation 的验收基准之一 |
| YAGNI 门禁 | contract lock 在 YAGNI 之前执行(先锁契约,再检查过度抽象) |
| circuit breaker | contract lock fail 计入 delivery 层 breaker 的 failure count |

---

## 六、降级路径

当无法执行 contract lock 时(如单端任务、紧急修复):

- Lead 可在 WorkOrder 中标注 `contract_lock_skipped: true` 并给出理由
- Verifier 验收时将 `contract_lock_skipped` 记录为 known-shortcut(进入 debt ledger)
- 后续如任务扩展为跨端协作,必须补签 contract-spec

---

## 七、与 Hook 注入的关系(P1-19)

- contract-spec 通过 hook 注入到 Worker 的上下文
- Worker 不需要手动查找契约文件
- hook_directives 中的 spec_files 包含 contract-spec 路径

---

## 八、不做什么

| 排除项 | 理由 |
|--------|------|
| 不强制所有 WorkOrder 都签 contract-spec | 单端任务无需跨端契约,强制会增加无意义开销 |
| 不允许单方面修改 contract-spec | 单方面修改是接口漂移的根源 |
| 不把 contract-spec 放在 LLM context 内持久化 | contract-spec 是 read-only namespace,存储在文件中,通过 hook 注入 |
| 不在 contract-spec 中定义实现细节 | 契约只定义接口,不定义实现 |
