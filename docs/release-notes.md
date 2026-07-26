# Release Notes

本文件维护 `virtual-intelligent-dev-team` 的版本历史、字段迁移指南和未实现的计划项。
`SKILL.md` 只保留最新一版的 changelog 链接,完整记录在此。

## v6.0.19 (2026-07-26)

- `route_request` 把已解析的主仓 `state-root` 传给 process plan 构建器，worktree 与
  迭代命令不再通过 shell 二次推断路径。
- 增加带空格主仓与 linked worktree 的路由级回归锁，确保 decision log 和后续命令
  共享同一个状态根真源。

## v6.0.18 (2026-07-26)

- Durable `.vidt` 状态与 decision log 统一解析到主仓 state-root。
- 收窄 worktree / change-localization 的否定和只读边界。
- 验证 fixture 改用自动清理的系统临时目录，仓库级发现跳过隐藏状态目录。

## v6.0.17 (2026-07-25)

- 收窄 worktree 关键词初筛表，移除「两个任务」「独立分支」「边开发边」「分开改」
  等在日常开发 prompt 里高频误触发的泛词，保留「同时推进」「互不干扰」「交替推进」
  「不影响主线」等语义明确的并行隔离信号；补 eval #232 锁定项目管理语境不应触发
  worktree 的负向契约。

## v6.0.16 (2026-07-25)

- 修复 eval #229/#230/#231 在 `--blind` 模式下断言不可达或字段路径错的问题：
  `micro_practices.items.reference` 改为 `micro_practices.names`（read_nested 不支持
  list 投影）；`process_plan first commands contain` 改为完整命令串匹配；
  `track_debt.py` 默认证据路径由 `.vidt/handoff` 改为 `.vidt/evidence`。
- 放宽 `project-knowledge-pyramid` 激活条件到 `capture-project-knowledge` bundle，
  使 onboarding 类请求也能激活知识金字塔协议；eval #230 断言同步匹配实际路由。
- `change-localization-protocol.md` 的激活条件描述与收紧后的代码对齐。

## v6.0.15 (2026-07-25)

- worktree 判断改为两层配合：`routing-rules.json` 扩充并行/隔离语义词做关键词初筛，
  `SKILL.md` workflow 新增 step 10.5 由 LLM 运行时复核 `needs_worktree` 信号（误判
  可降级、漏判可建议）；worktree plan entry 标注 `needs_worktree` 为初筛结果。

## v6.0.14 (2026-07-25)

- 15 个 `.skill-*` 状态目录统一收拢到 `.vidt/` 单一根并去掉 `skill-` 前缀
  （harness/iterations/handoff/evidence/metrics/beta/product 等），减少项目初始
  散落目录数量。同步脚本默认值、`parent.name` 结构性校验、各 beta/post-release
  脚本的 `repo_root` 反推（改为遍历 `.vidt` 自适应定位）、eval 断言路径、`.gitignore`
  与 `export_public_skills` 排除规则；磁盘运行时状态一次性迁移至 `.vidt/`。

## v6.0.13 (2026-07-24)

- 新增 `worktree-state-placement-protocol.md`，区分 state-root（主仓）与
  execution-root（worktree），给出 16 个状态目录的归属表与 `git rev-parse` 自举
  state-root 的路径约定。worktree plan entry 注入状态目录步骤与 `STATE_ROOT` 命令；
  `change-localization` 与 `project-knowledge-pyramid` 补 Worktree Behavior 节。
  补 eval #231 覆盖 state-root 注入断言。

## v6.0.12 (2026-07-24)

- 新增 `change-localization-protocol.md`（token 预算递进五步收敛到精确改动点，
  关键词检索步骤强制走脚本不调用 LLM）与 `project-knowledge-pyramid-protocol.md`
  （面向目标代码库的三级知识地图 + SHA 漂移检测）。两个协议接入 audit-fix-deliver /
  root-cause-remediate / plan-first-build 工作流包，在 `route_request` 注册激活分支
  并补 eval #229 #230 覆盖。

## v6.0.11 (2026-07-24)

- `anti-entropy-governance` 新增数据通道红线（外部数据源必须走专用脚本通道、禁止
  通用 fetch）；`iteration-protocol` 增加错误分级与阶段化自修复预算矩阵；
  `pre-development-planning` 要求触发类交互必须携带具体引用依据。

## v6.0.10 (2026-07-23)

- Pages workflow 升级到 `actions/upload-pages-artifact@v4`，继续直接上传 `./docs`
  静态目录并交给 `deploy-pages@v4` 部署。
- 删除不会进入 artifact、且当前 custom Actions 流程不需要的 `.nojekyll`；发布门禁、
  文档说明和回归测试同步收紧到真实部署边界。
- `docs/assets/site.css` 与 `docs/assets/site.js` 继续作为五个公开页面唯一的共享运行资源。

## v6.0.9 (2026-07-23)

- 公开文档站整体重写为统一的技术编辑风格，五个正式页面共享静态 CSS / JS、
  响应式导航、键盘焦点、reduced-motion 与无 CDN 运行边界。
- 退役 `deck.html` 及其专用样式和交互脚本；原有架构、状态机、workflow 与角色
  信息已归并进概览、架构、工程化、角色和能力矩阵页面，不保留旧入口兼容层。
- 在 skill 内新增 GitHub Pages workflow；subtree 发布到独立仓库后可直接上传
  `./docs` 并通过 GitHub Actions 部署，发布脚本同步校验静态站资源和退役资产。
- 文档索引、本地预览说明、公开入口、版本同步脚本与回归测试对齐新的站点边界。

## v6.0.8 (2026-07-22)

- 治理事件只读写 `.vidt/metrics/decision-log.jsonl`，删除旧日志迁移脚本、容忍分支、
  可配置旧路径与对应文档入口；不会删除任何 operator 已有数据文件。
- Frontend hook 不再声明不存在的 `language-profiles.yaml#typescript`；路由构建 hook
  前会校验 spec 文件存在性与语言 profile 可解析性，悬空引用 fail-closed。
- 健康检查明确允许首次部署尚未生成 decision log，并新增首次部署、悬空 profile、
  兼容链残留和 Frontend hook 的回归覆盖。
- Git 工作流护栏保留 porcelain 状态列的前导空格，并将删除项纳入暂存清单，避免
  首条未暂存改动误阻断 G0 或 G1/G2 对删除内容失明。

## v6.0.7 (2026-07-22)

- 发布 workflow 固定 Python 3.11，并在执行 `validate_virtual_team.py` 前从
  `requirements.txt` 安装 `jsonschema` 与 `PyYAML`，消除本地隐式依赖造成的 CI 假绿。
- negative eval 统一同时携带 `negative: true` 与 `negative` category，使分类汇总、
  `negative_cases` 清单和仓库 validator 使用同一口径。
- 增加发布步骤顺序与 negative taxonomy 一致性回归锁，阻止依赖安装或统计字段再次漂移。

## v6.0.6 (2026-07-22)

复检收口版本。`check_harness_health.py` 现在会实际读取 Agent Catalog，并核对
`workflow-bundles.md` 中 12 个稳定 bundle ID；任一真源缺失、不可读或重复都会
fail-closed。清理已退出角色 `Frontend Virtuoso` 的 hook / contract 残留，将前端
spec 注入归并到 `World-Class Product Architect`；修复 eval 到 SKILL.md 的失效锚点，
通过 fixture adapter 隔离 blind audit 的 `.vidt/` 状态并保持 JSON stdout 纯净；
补齐 reference 与 smoke-test 索引、公共 Python 依赖说明，并删除一次性
`deletion_pass.py` 阶段工具。

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

- **跨 session 状态持久化**：`real-subagent-runtime-protocol.md` 中 multi-session tier 的 session 状态快照与恢复目前依赖外部 agent backend，Memory Keeper 角色未来接管 `.vidt/metrics/session-state.jsonl` 的写入与校验
- **telemetry 采样策略记忆**：当前 `emit_telemetry.py` 的 `sampling_rate` 由调用方传入，Memory Keeper 未来负责基于历史 drift 分布自动建议采样率
- **stress scenario 历史基线**：当前 `run_stress_scenarios.py` 每次运行覆盖前次结果，Memory Keeper 未来负责维护 `evals/stress-scenarios/baselines/` 历史快照，支持回归对比

Memory Keeper 角色定义见 [references/real-subagent-runtime-protocol.md](../references/real-subagent-runtime-protocol.md) §Subagent Roles。
