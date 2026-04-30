# knowledge/*.md 模板

`docs/knowledge/` 放**会随时间变化的事实和历史**：项目背景、当前进度、决策原因、TODO、踩过的坑。

判断"是不是 knowledge"的快速测试：
- 这条信息半年后**可能不再准确**？（"目前完成 70%"、"用 v2 接口"、"X 还没决定"）→ knowledge
- 永远不变的命令 / 命名规则 / 禁令？→ rule，不是 knowledge

下面给五种典型 knowledge 文件骨架。按项目实际情况选择性创建（最少要 background.md + progress.md + todo.md）。

---

## background.md — 项目背景与目标

`docs/knowledge/background.md`：

```markdown
# Background

## What is this

<一段话描述这个目录/feature 是做什么的，用大白话>

## Why does this exist

<为什么需要它？解决什么问题？为谁服务？>

## Context within the larger project

- 上游：<谁/什么提供输入？数据从哪来？>
- 下游：<谁/什么消费输出？产物给谁？>
- 相关 sibling 目录：<同级其他子项目，如有>

## Success criteria

<怎么算"完成"？做到什么程度可以收工？>
```

---

## progress.md — 当前进度

`docs/knowledge/progress.md`：

```markdown
# Progress

> 状态快照，最后更新于 <YYYY-MM-DD>。

## Where we are right now

<一两句话描述当前状态：能跑通什么？卡在哪？大概完成了百分之几？>

## What works

- <功能 A 跑通了，输出 X>
- <模块 B 完成了 Y>

## What's broken / unstable

- <Z 在某种情况下会 crash，待修>
- <参数 W 还没调好>

## Recent activity (last few sessions)

- YYYY-MM-DD: <做了什么>
- YYYY-MM-DD: <做了什么>

> 这部分会过时，下次 wrap-up 时更新。
```

---

## todo.md — 未完成事项

`docs/knowledge/todo.md`：

```markdown
# TODO

## Next steps (按优先级)

1. <最重要 / 最先做的事>
2. <第二项>
3. <第三项>

## Known blockers

- <被什么阻塞？等谁的回复？等什么数据？>

## Nice to have (低优)

- <可有可无的优化>
- <未来可以试试的方向>

## Open questions

- <还没想清楚的问题，需要思考或问人>
```

---

## decisions.md — 关键决策与原因

`docs/knowledge/decisions.md`：

```markdown
# Decisions

记录已做出的关键设计抉择 + **为什么** —— 让未来的你（或别的 agent）能理解上下文，避免推翻已决议的事。

## YYYY-MM-DD: <决策标题>

**Context**: <当时的情况是什么？>
**Options considered**: <考虑过哪些方案？>
**Decision**: <选了哪个>
**Reason**: <为什么选它，不选其他>
**Tradeoffs accepted**: <已知的代价是什么>

---

## YYYY-MM-DD: <下一个决策>

...
```

---

## pitfalls.md — 踩过的非平凡坑

`docs/knowledge/pitfalls.md`（按需）：

```markdown
# Pitfalls

> 调试中发现的非显然问题。看到这些情况时知道是怎么回事，省得重新踩一遍坑。

## YYYY-MM-DD: <现象简述>

**Problem**: <表面现象是什么>
**Root cause**: <实际原因>
**Solution**: <怎么绕过 / 修复的>
**Lesson**: <下次遇到类似情况怎么辨别>
**Files involved**: `<file1>`, `<file2>`

---

## YYYY-MM-DD: <下一个坑>

...
```

---

## 写 knowledge 的注意事项

1. **绝对日期**：永远写 `2026-04-30`，不写"上周"、"最近"、"昨天"——半年后回来这些相对时间都失效。
2. **写"为什么"比"做了什么"重要**：git log 已经记录了 what，knowledge 要记 why。
3. **不要重复 rules**：knowledge 里不要复述命令格式、风格规范（那是 rules）。
4. **结构化 > 长篇散文**：bullet list、表格、明确的小节。便于 agent 按需检索。
5. **过时不删，标注 deprecated**：旧的 decision 还有历史价值，但要明确标 `[DEPRECATED 2026-04-30: 改用方案 B]`。

## 拆分原则

- 项目极小：所有 knowledge 内容塞 `background.md` 一个文件 + `todo.md` 也行。
- 项目中等：上面列的 background / progress / todo / decisions 四个文件比较舒服。
- 项目大、决策多：把 decisions 按主题拆成 `decisions/<topic>.md`。

按需，不强制。
