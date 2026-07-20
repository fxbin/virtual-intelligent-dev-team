# Virtual Intelligent Dev Team Docs

这组文档面向两类读者：

- 想快速上手的使用者
- 想理解内部设计与维护边界的维护者

如果你不知道先看哪篇，可以直接按下面这条最短路径走：

1. 先看 [../README.md](../README.md)
2. 再看 [usage-guide.md](usage-guide.md)
3. 最后按需看 [design-philosophy.md](design-philosophy.md)

如果你想先看可视化总览，直接打开 [deck.html](deck.html)：入口是 11 页总览墙，可点击任意页面进入演示，使用方向键翻页、Esc 返回总览、F 切换全屏。HTML Deck 是唯一演示文稿真源，仓库不再维护独立 PPTX。

## 推荐阅读顺序

如果你是第一次接触这个项目：

1. [../README.md](../README.md)
2. [usage-guide.md](usage-guide.md)

如果你想继续理解设计逻辑：

1. [design-philosophy.md](design-philosophy.md)
2. [../SKILL.md](../SKILL.md)

## 你会在这里看到什么

- `README.md`
  - 更像项目首页，帮助你快速判断“这是不是我要的东西”
- `usage-guide.md`
  - 更像上手说明，帮助你快速跑通第一次使用
- `design-philosophy.md`
  - 更像设计说明，帮助你理解为什么项目会这样组织

## 文档分工

- `usage-guide.md`
  - 讲怎么实际使用这个项目，包括手动模式、小切片交付、`/auto`、resume、completion evidence、release、beta 等典型路径
- `design-philosophy.md`
  - 讲为什么这个项目要这样设计，以及边界在哪里
- `release-notes.md`
  - 讲每个版本的变更摘要、字段迁移指南（如 `correctly_not_caught` 枚举迁移）和未实现的计划项

## 真源在哪里

运行时真源主要在这些文件：

- `../SKILL.md`
- `../references/playbook-index.md`
- `../references/tooling-command-index.md`
- `../references/*.schema.json`

`docs/` 更偏向项目入口、维护者说明与设计解释，不替代运行时真源。
