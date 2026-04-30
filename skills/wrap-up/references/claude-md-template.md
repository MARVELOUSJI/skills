# CLAUDE.md 模板

子目录的 CLAUDE.md 是**索引层**：让 agent 一眼看到主入口、运行方式、再按需点开 rules / knowledge。**不要**把详细信息直接塞进 CLAUDE.md（那是 rules / knowledge 的事）。

## 模板（agent 按当前项目实际情况填空）

```markdown
# <directory-name>

> 由 wrap-up skill 生成于 <YYYY-MM-DD>。再次进入此目录时，按本文档恢复 context。
> 父目录 CLAUDE.md（如有）提供项目级规则，本文件提供本子目录运行细节。

## 主入口

`<main_script>` — <一句话说明它做什么、产出什么>。

## 怎么运行

```bash
<最常用的一两条命令>
# 例如：
# python main.py --config configs/default.yaml
# 或远程：
# rca exec -n <node> -d <remote_dir> "conda run -n <env> python main.py"
```

## 目录结构

| 路径 | 角色 |
|---|---|
| `<main_script>` | 主逻辑入口 |
| `utils/` | 功能函数（按主题拆文件） |
| `<output_dirs>` | 输出（gitignored / 手动管理） |
| `<data_dirs>` | 输入数据（来源说明） |

## Rules（运行约束 — always-on）

> 这部分是不会过期的硬约束。agent 应在每次任务开始前扫一遍。

- [运行环境与命令](.claude/rules/runtime.md)
- [代码风格与命名](.claude/rules/style.md)
- [禁止操作](.claude/rules/dont.md)（按需）

## Knowledge（项目背景 — on-demand）

> 这部分是会随时间变化的事实和历史。agent 按当前任务挑相关章节读，不要无脑全读。

- [项目背景与目标](docs/knowledge/background.md)
- [当前进度](docs/knowledge/progress.md)
- [关键决策与原因](docs/knowledge/decisions.md)
- [TODO 与已知阻塞](docs/knowledge/todo.md)
- [踩过的非平凡坑](docs/knowledge/pitfalls.md)（按需）

## 上下文恢复提示（给未来的 agent）

进入此目录后：
1. 先扫一遍上面的 Rules（always-on，必读）。
2. 看 `progress.md` 知道目前在哪。
3. 看 `todo.md` 决定下一步做什么。
4. 其他 knowledge 文件按当前任务的相关性按需读。

如果用户说"我们继续上次的工作"——`todo.md` 第一项就是续点。
```

## 填表注意

- **directory-name**：用 `basename "$PWD"`，不要硬编码。
- **main_script**：Phase 1 已经定下来主入口是哪个文件，直接引用。
- **怎么运行**：从 git log 的命令、README、shell history 里找最常用的 invocation；也可以问用户。
- **目录结构**：只列 wrap-up 之后保留的目录，不列已删除的。
- **Rules 链接**：按实际生成的 rule 文件列，不要列不存在的。
- **Knowledge 链接**：同上。

## 父目录 CLAUDE.md 的关系

如果 `find ~/. -maxdepth 5 -name CLAUDE.md` 在父目录找到 CLAUDE.md（典型场景：仓库根有 CLAUDE.md 描述全局规则），子目录 CLAUDE.md 顶部要点出"父目录 CLAUDE.md 提供项目级规则，本文件提供本子目录运行细节"，让 agent 知道两者并存、不冲突。

**不要去修改父目录 CLAUDE.md。**
