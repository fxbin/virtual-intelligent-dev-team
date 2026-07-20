# Release Notes

本文件维护 `virtual-intelligent-dev-team` 的版本历史、字段迁移指南和未实现的计划项。
`SKILL.md` 只保留最新一版的 changelog 链接,完整记录在此。

## v6.0.5 (2026-07-20)

HTML Deck 按 GitHub Pages 发布边界拆分为稳定入口、独立样式与交互脚本；发布门禁
校验必需资源并阻止历史 PPTX 产物回流，公开目录只保留当前演示实现，历史版本由
Git 追溯。

## v6.0.4 (2026-07-19)

HTML Deck 完成整体视觉与叙事重构：以任务调度、证据档案和闭环管线建立
主题原生视觉语法，替换旧版紫蓝渐变与等权卡片结构；新增 overview wall、
点击进入演示、Esc 返回总览和自适应 16:9 舞台。11 页内容重新编排为责任链、
六层闭环、专家调度、workflow atlas、fail-closed runtime、14 状态机与系统覆盖面，
演示页不再暴露页码和制作元信息，PPTX 仍保持不生产边界。

## v6.0.3 (2026-07-19)

公开说明与 HTML Deck 已按运行时真源重新对齐：核心架构统一为六层闭环、
一个 Team Engine Lite 交付子图和可选 Stage Council overlay；Team Engine
状态机、12 个 workflow bundles、runtime 能力链、fail-closed handoff 与
Response Pack 证据边界同步更新。HTML Deck 成为唯一演示文稿，移除重复的
PPTX 二进制文件及其专用生成脚本。

## v6.0.2 (2026-07-18)

复检收口版本。运行时 tier 现在同时受请求 eligibility 与完整能力链约束；
breaker、Verifier、file handoff、Team Engine drill 和 stress gate 改为
fail-closed。Response Pack、benchmark runner/check、`spec_violation`、workflow
bundle、路由示例和版本元数据合同已同步，发布证据必须来自可执行门禁。

`v6.0.1` 中“无破坏性 schema 变更”的声明不再作为发布依据；新增字段已经在
sidecar schema、生成器、渲染器、eval 和回归测试中统一登记。

## v6.0.1 (2026-07-16)

Hotfix release based on roundtable-forge 复检结论（v6.0.0 不回滚，分 commit 修复 8 个 P0 风险）。所有改动向后兼容，无破坏性 schema 变更。

**修复清单（6 commits）**：

1. **ns-001 markdown 字段名错误 + rg 外部依赖**
   - `run_stress_scenarios.py` 修复 `fs.get('match')` → `fs.get('validated')`
   - 新增 `search_callers` 函数：rg 优先 + Python re fallback，CLI 新增 `--require-rg` / `--fallback-grep` / `--no-fallback-grep`
   - `generate_trace_summary` 输出新增 `search_engine` 字段（`rg` / `python-re` / `none`）

2. **ns-002 select_runtime_tier + probe_host_capabilities + runtime smoke test**
   - `route_request.py` 新增 `probe_host_capabilities()`（两层设计：环境变量声明优先 + 自动探测 fallback）
   - 新增 `runtime_smoke_test()` — tier 选择后最小化验证，失败降级到 `soft_orchestration_only`
   - 新增 `select_runtime_tier()` — 基于 host 实际能力动态选择 tier，替代硬编码 `runtime_claim`
   - `build_real_subagent_runtime_plan` 返回值新增 `runtime_evidence` / `runtime_downgraded_from` / `runtime_downgrade_reason` / `tier_selection_function` 字段

3. **ns-003 字段命名统一 + ABSTRACTION_PATTERN 配置驱动 + 语义混淆修复**
   - `observability-protocol.md` §6.2 `slo_target` → `slo_target_seconds`（单位：秒）
   - 新增 `scripts/abstraction_keywords.yaml` — ABSTRACTION_PATTERN 唯一 source of truth，按 `core` / `extended` 分档，支持 `--lang` 参数
   - `emit_telemetry.py` 新增 `load_abstraction_keywords()` + `build_abstraction_pattern()`，硬编码正则改为配置驱动
   - `run_stress_scenarios.py` status 枚举简化：`{passed, vulnerability, false-positive, trace-incomplete, error}` → `{passed, failed, correctly_not_caught}`
   - 新增 `scenario_outcome` 顶层字段（`all_scenarios_passed` / `semantic_warning` / `semantic_error`）+ 与 status 一致性检查

4. **ns-004 补充 routing/drill 5 个压测场景**
   - 新增 5 个场景 JSON：`routing-tier-selection-boundary` / `routing-soft-fallback-downgrade` / `routing-circuit-breaker-escalation` / `drill-multi-session-lifecycle` / `drill-soft-orchestration-degradation`
   - `run_stress_scenarios.py` 新增 `run_routing_tier_selection` 函数 + `routing_tier_selection` method 路由分支
   - self_test 覆盖 12 个场景

5. **ns-005 quick_validate 字段名一致性检查 + DRIFT_CRITICAL_THRESHOLD 提取 + abstraction_keywords.yaml schema 校验**
   - 新增 `scripts/observability_config.py` — 可观测性常量唯一 source of truth（LAYER_VALUES / DRIFT_CRITICAL_THRESHOLD / SLO_LATENCY_TARGETS 等）
   - `emit_telemetry.py` 改为从 `observability_config` 导入常量
   - `emit_telemetry.py` 新增 `validate_abstraction_keywords_schema()` + `--validate-schema` CLI 入口
   - `quick_validate.py` 新增 `_check_stress_scenario_field_consistency()` — 校验顶层字段完整性 / method 枚举 / scenario_id 与文件名一致性

6. **ns-006 release notes + Memory Keeper 标注 + correctly_not_caught 迁移指南**
   - 本节（Release Notes v6.0.1）
   - §Memory Keeper 计划中 标注后续工作
   - §correctly_not_caught 迁移指南

## correctly_not_caught 迁移指南

v6.0.1 将 `run_stress_scenarios.py` 的 `status` 枚举从 5 值简化为 3 值。下游消费者（benchmark / report / dashboard）需按下表映射：

| v6.0.0 status | v6.0.1 status | 说明 |
|---|---|---|
| `passed` | `passed` | 不变 |
| `vulnerability` | `failed` | 漏洞即失败，语义更直接 |
| `false-positive` | `correctly_not_caught` | 误报 = 系统正确地没有捕获（原 `false-positive` 语义混淆） |
| `trace-incomplete` | `failed` | trace 不完整即失败，错误细节见 `error` 字段 |
| `error` | `failed` | 执行错误即失败，错误细节见 `error` 字段 |

**向后兼容**：
- `scenario_outcome` 顶层字段为 v6.0.1 新增，v6.0.0 消费者忽略此字段不受影响
- `expected.caught=false` 语义不变：系统未捕获 + 期望未捕获 = `correctly_not_caught`；系统未捕获 + 期望捕获 = `failed`
- 旧报告解析器遇到 `correctly_not_caught` 应视为 `false-positive` 的等价替换

**破坏性变更**：无。所有 v6.0.0 字段在 v6.0.1 中保留或语义等价映射。

## Memory Keeper 计划中

以下能力在 v6.0.1 标注为「Memory Keeper 计划中」，尚未在当前版本实现，留作后续迭代：

- **跨 session 状态持久化**：`real-subagent-runtime-protocol.md` 中 multi-session tier 的 session 状态快照与恢复目前依赖外部 agent backend，Memory Keeper 角色未来接管 `.skill-metrics/session-state.jsonl` 的写入与校验
- **telemetry 采样策略记忆**：当前 `emit_telemetry.py` 的 `sampling_rate` 由调用方传入，Memory Keeper 未来负责基于历史 drift 分布自动建议采样率
- **stress scenario 历史基线**：当前 `run_stress_scenarios.py` 每次运行覆盖前次结果，Memory Keeper 未来负责维护 `evals/stress-scenarios/baselines/` 历史快照，支持回归对比

Memory Keeper 角色定义见 [references/real-subagent-runtime-protocol.md](../references/real-subagent-runtime-protocol.md) §Subagent Roles。
