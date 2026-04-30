# wrap-up

> 在 feature 或子项目开发暂停时，把当前目录固化成可恢复的状态：整理文件 + 生成持久化交接文档。

## 何时用

一个小功能、子目录、figure 渲染脚本写得差不多了，开发暂停一段时间。目录里堆了一堆调试代码、版本文件，主入口看不出来。担心几周后回来完全忘了。

## 怎么触发

在当前要收尾的目录里，对 Claude Code 说：

```
wrap up
```

或

```
收尾这个 feature
打包这个目录
这块开发先停下来记录一下
```

## 它会做什么

**Phase 1 — 文件整理**

列出当前目录所有文件的评估表（路径 / 作用 / 清理风险 / 推荐清理程度），给一份完整推荐清理方案，然后**等你拍板**。你可以照搬、自定义、或让 agent 解释推荐理由。确认后才会执行清理（git 仓库优先 `git mv` 保留 history，非 git 仓库可选先建 tarball 备份）。

清理目标：主目录只剩一个主脚本 + `utils/` 子目录。

**Phase 2 — 交接文档生成**

按三层 context 架构产出：

```
当前目录/
├── CLAUDE.md                 # 索引层
├── AGENTS.md → CLAUDE.md     # 软链接（兼容 Codex CLI 等）
├── .claude/rules/            # 硬约束：命令、风格、禁止事项
└── docs/knowledge/           # 状态与背景：进度、决策、TODO、踩坑
```

下次进这个目录开 Claude / Codex CLI，AGENTS.md / CLAUDE.md 会被自动加载，agent 自动恢复 context。

## 与其他 skill 的边界

- **不替代 `handoff`**：handoff 输出会话间临时摘要（贴下次会话开头），wrap-up 输出持久化文档。
- **不替代 `context-audit`**：context-audit read-only 审计已有 context 系统，wrap-up 主动建立 context 系统。两者可串联用：wrap-up 完成后跑一次 context-audit 验证健康度。
- **不替代 `init-project`**：init-project 初始化全新空白项目的 Claude Code 配置，wrap-up 针对已开发一段时间的子目录收尾。

## 安全约束

- Phase 1 不会跳过用户确认直接清理。
- 检测到 git 仓库 dirty 且用户拒绝 commit → agent 主动 abort 文件操作（避免覆盖未保存工作）。
- 永不主动删除 `.env*`、凭证、依赖声明、`*-bkup.py` 备份脚本、LICENSE 等敏感文件。
- 已经 wrap-up 过的目录走 update 模式（合并），不 overwrite 你的手改。
- 不会修改父目录的 CLAUDE.md。

## 目录结构

```
wrap-up/
├── SKILL.md                              # skill 主定义（agent 读这个）
├── README.md                             # 本文件（人读）
└── references/
    ├── claude-md-template.md             # CLAUDE.md 模板
    ├── rules-templates.md                # rules/*.md 模板
    ├── knowledge-templates.md            # knowledge/*.md 模板
    └── cleanup-heuristics.md             # 文件分类启发式
```
