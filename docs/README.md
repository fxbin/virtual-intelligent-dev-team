# Virtual Intelligent Dev Team Docs

`docs/` 同时承担公开站点和维护者文档，但两者职责不同：

- 五个 HTML 页面面向浏览者，构成 GitHub Pages 静态站。
- Markdown 文档面向使用者与维护者，解释操作方式、设计理念和版本变化。
- 运行时规则仍以 `../SKILL.md` 和 `../references/` 为真源。

## 公开站点

| 页面 | 主要内容 |
| --- | --- |
| [index.html](index.html) | 定位、核心闭环、最短上手路径 |
| [architecture.html](architecture.html) | 六层 Closure、Team Engine Lite、runtime 与 12 个 Workflow Bundles |
| [engineering.html](engineering.html) | Harness、标准交接对象、反熵治理与完成证据 |
| [agents.html](agents.html) | 8 个专家角色、路由边界与两个 Stage Council |
| [matrix.html](matrix.html) | 14 维能力对比、适用边界与取舍 |

所有页面共享：

- `assets/site.css`：视觉 tokens、布局、组件、响应式与可访问性样式
- `assets/site.js`：移动端导航、复制按钮和轻量页面状态

站点不使用构建工具、CDN、远程字体或前端框架。`deck.html` 及其专用资源已经退役；演示内容已归并进五个正式页面，不保留兼容入口。

## GitHub Pages 部署

本 skill 会通过仓库级发布 workflow 以 subtree 形式发布到独立仓库
`fxbin/virtual-intelligent-dev-team`。subtree 发布后，
`.github/workflows/pages.yml` 位于目标仓库根目录，并把 `./docs` 上传为 Pages artifact。
该流程不执行 Jekyll 构建，因此不需要 `.nojekyll`。

预期公开地址：

- <https://fxbin.github.io/virtual-intelligent-dev-team/>

注意：GitHub 的 `blob/.../docs/index.html` 页面只显示 HTML 源码，不会渲染站点；必须访问 Pages 地址。第一次启用时，目标仓库的 **Settings → Pages → Source** 需要允许 **GitHub Actions**。workflow 成功运行前，不应宣称线上站点已部署。

## 本地预览

从独立 skill 仓库根目录运行：

```bash
python -m http.server 8000
```

访问 <http://localhost:8000/docs/>。

从 `skill-hub` 仓库根目录运行同一命令时，访问：

<http://localhost:8000/virtual-intelligent-dev-team/docs/>

不要直接用 `file://` 作为最终验收方式；本地 HTTP 能更接近 Pages 的路径与资源加载行为。

## 推荐阅读顺序

第一次使用：

1. [../README.md](../README.md)
2. [usage-guide.md](usage-guide.md)
3. [index.html](index.html)

理解设计与维护：

1. [design-philosophy.md](design-philosophy.md)
2. [architecture.html](architecture.html)
3. [engineering.html](engineering.html)
4. [../SKILL.md](../SKILL.md)

版本变化：

- [release-notes.md](release-notes.md)

## 文档更新规则

- 行为、路由或协议变化先改真源，再同步公开 HTML 和回归覆盖。
- 五个页面的公共视觉或交互只在 `assets/site.css` / `assets/site.js` 修改。
- 删除或重命名公开页面时，同步发布脚本、站内导航、README 与测试。
- 不把 `SKILL.md` 扩写成手册；详细解释留在 `references/` 或 `docs/`。
- 每次修改本 skill 都必须更新 `VERSION` 并通过 `quick_validate`。

## 运行时真源

- `../SKILL.md`
- `../references/playbook-index.md`
- `../references/agent-catalog.md`
- `../references/workflow-bundles.md`
- `../references/team-engine-lite-protocol.md`
- `../references/*.schema.json`

公开站点负责解释和导航，不替代上述运行时契约。
