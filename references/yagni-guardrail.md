# YAGNI Guardrail

检测 Worker 产出中未被请求的抽象,防止过度构建。

## 核心原则

agent 的默认失败模式不是"做得不够"是"做得太多"。Worker 在实现 WorkOrder 时容易引入未被请求的抽象层,增加维护成本和认知负担。

## 检测清单

以下模式在 Worker 产出的 diff 中出现时标记为可疑:

1. **只有一个实现的 interface** — 新增 interface 但全仓库仅有一个 implements/extends
2. **只有一个产品的 factory** — 新增 Factory 类但只生产一种产品
3. **永远不变的值的 config** — 新增配置类但所有字段都是常量
4. **未被请求的 middleware** — WorkOrder 未要求中间件但新增了 middleware 层
5. **未被请求的抽象层** — WorkOrder 未要求分层但新增了 adapter/proxy/wrapper

## 不可简化红线

以下代码即使看起来"可简化"也不触发 YAGNI 检测:

- **信任边界校验** — 跨服务/跨进程的输入校验
- **防数据丢失** — 事务、备份、幂等性保证
- **安全** — 鉴权、授权、加密、脱敏
- **可访问性** — a11y 标注、键盘导航、屏幕阅读器支持

## 应用范围

- 只在 Worker 角色应用,不覆盖架构师/契约/审计角色
- 架构师角色允许适度前瞻性抽象
- 契约角色需要定义接口契约
- 审计角色需要检查现有抽象的合规性

## 检测方式

`verify_action.py --check yagni --diff-file <path>` 扫描 Worker 产出的 diff:

- 扫描新增的 interface/abstract/Factory/middleware 模式
- 命中 → warning(不 hard fail)
- 红线模式(安全/数据丢失/可访问性)不触发
- 先 warning 模式运行,收集误判案例后再调阈值

## 与 Verifier 的关系

YAGNI 检测结果作为 Verifier 的参考输入:

- 命中 YAGNI 模式 → Verifier verdict = fail,RemediationPatch = "删除未被请求的 X"
- 红线模式不触发 → Verifier 不降级 verdict
