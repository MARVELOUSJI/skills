# MARVELOUSJI/skills

Personal Claude Code & Codex skills monorepo.

## Structure

```
skills/
└── <skill-name>/
    ├── SKILL.md       # 主描述文件 (Claude Code 扫描的入口)
    └── ...            # 支持文件 (scripts, templates, docs)
```

每个 `skills/<name>/` 子目录 = 一个独立的 skill。

## 如何激活 (在任一机器上)

这个仓库本身不直接被 Claude Code 读取。激活是通过 symlink:

```
~/.claude/skills/<name>    → ~/workspace/skills/skills/<name>
~/.agents/skills/<name>    → ~/workspace/skills/skills/<name>
```

Symlink 由 `~/dotfiles/scripts/setup-skills.sh` 创建 (见 [MARVELOUSJI/dotfiles](https://github.com/MARVELOUSJI/dotfiles))。

## 添加新 skill

1. `mkdir skills/<new-name>` + 写 `SKILL.md` + 其他文件
2. `git add -A && git commit -m "feat: add <new-name> skill" && git push`
3. `~/dotfiles/scripts/setup-skills.sh` — 建 symlink 激活
4. 下次 Claude Code 会话即可使用

## 致谢

部分 skills cherry-picked 自 [jiahao-shao1/sjh-skills](https://github.com/jiahao-shao1/sjh-skills) (MIT)。
