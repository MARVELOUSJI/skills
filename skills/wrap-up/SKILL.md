---
name: wrap-up
description: >
  在某个 feature 或小功能开发暂停时，把当前目录固化成可恢复的状态。
  做两件事：（1）整理目录文件 — 列出每个文件的作用、清理风险、推荐清理程度，
  让用户决定保留/删除/合并，最终目录只剩主脚本 + utils/；（2）生成持久化交接文档 —
  CLAUDE.md 索引层 + .claude/rules/（硬约束）+ docs/knowledge/（背景与进度），
  并建 AGENTS.md 软链接到 CLAUDE.md。这样未来再次进入该目录开 Claude/Codex CLI 时，
  agent 能自动加载这些文档恢复 context，不用从零回顾。
  Triggers: "wrap up"、"收尾"、"feature 收尾"、"打包这个目录"、"归档这个 feature"、
  "这块开发先停下来记录一下"、"写交接文档"（针对当前目录）。
  NOT for: 仅生成会话间的临时摘要贴下次会话用（→ handoff）；
  也不审计已有 context 系统的健康度（→ context-audit）；
  也不初始化全新的空白项目（→ init-project）。
user_invocable: true
---

# Wrap-Up

收尾一个 feature / 子项目，让明天的你（或别的 agent）能 1 分钟接上手。

## When to Use

- 一个小功能、子目录、figure 渲染脚本写得差不多了，开发暂停一段时间。
- 目录里堆了一堆 `*_v2.py`、`debug_xxx.py`、`tmp.txt`，主入口是哪个都看不出来。
- 担心几周后回来这块代码完全忘了，想留一份"未来的我能直接续上"的状态。

不要在以下场景用：
- 只想生成一份贴到下次会话开头的摘要（用 `handoff`）。
- 只想检查现有 CLAUDE.md / rules / knowledge 是否健康（用 `context-audit`，read-only）。
- 全新空目录想初始化 Claude Code / Codex 项目上下文（用 `init-project`）。

## Execution

工作流分三个阶段，用户在 Phase 1 必须明确确认才动手清理。

### Phase 0 — 边界判断与现状识别

1. **判断目录是否值得 wrap-up**：
   - 用 `find . -maxdepth 2 -type f | head -20` 看有没有源码文件。
   - 文件 < 3 个、或全是空目录 → 告知用户"这个目录看起来不需要 wrap-up"，停止。
2. **检测已有 context 系统**：
   - `ls CLAUDE.md AGENTS.md .claude/rules docs/knowledge 2>/dev/null`
   - 已存在 → 告诉用户"检测到已有 context 系统，将进入 update 模式（合并而非覆盖）"。
3. **报告找到了什么**：用一段话告诉用户当前目录的扫描结果（文件数、是否 git 仓库、是否已 wrap-up），让用户对当前状态心里有数。

### Phase 1 — 文件整理（必须用户确认后才动手）

#### 1.1 扫描目录

```bash
find . -type f \
  -not -path './.git/*' \
  -not -path './node_modules/*' \
  -not -path './__pycache__/*' \
  -not -path './.venv/*' \
  -not -path './outputs/*' \
  -not -path './render_outputs*/*' \
  -not -name '.DS_Store' \
  | sort
```

按项目类型补充排除项（Python 项目排除 `*.pyc`，前端项目排除 `dist/`、`build/` 等）。

#### 1.2 输出评估表（这是用户阅读的核心产出）

对每个文件输出一行 Markdown 表格，**四列固定**：

| 文件路径（相对） | 文件作用 | 清理风险 | 推荐清理程度 |

填表的依据：
- **文件作用**：先 `head -30 <file>` 读开头判断角色（主脚本？工具函数？测试？文档？调试脚本？参数备份？），再扫读代码（不超过 200 行/文件）确认。
- **清理风险**：用以下检查给出"低 / 中 / 高"评估：
  - `grep -rn "<filename without extension>" . --include='*.py' --include='*.md' | grep -v "<filename>:"` — 查谁在引用它。
  - `grep -rn "from <module>\|import <module>" .` — 看是否有 import。
  - `git log --oneline --follow -- <file> 2>/dev/null | head -5`（如果是 git 仓库）— 看最近还在不在被改。
  - 风险写明具体理由，不要光写"低"，要写"低 — 已 grep，仅 main.py 早期版本引用，main 已改为新接口"。
- **推荐清理程度**：从 `保留` / `移到 utils/` / `重命名为 X` / `删除` / `归档到 docs/` / `用户决定` 中选。

举例（仅示意，agent 应该按真实文件填）：

| 文件路径（相对） | 文件作用 | 清理风险 | 推荐清理程度 |
|---|---|---|---|
| `render.py` | 主渲染入口 | - | **保留**（建议重命名为 `main.py` 或在 CLAUDE.md 标注） |
| `render-bkup.py` | 早期参数备份 | 中 — 用户的 CLAUDE.md 提到 *-bkup.py 是参数备份脚本 | 保留（按项目惯例） |
| `helper_v1.py` | 早期工具函数 | 低 — 已 grep 确认无 import | **删除** |
| `utils_math.py` | 数学工具 | 中 — 多处使用 | **移到 `utils/math.py`** |
| `debug_camera.py` | 调试脚本 | 低 — 注释写明"临时" | **删除** |
| `notes.txt` | 临时笔记 | 低 | 用户决定（删除 / 转入 `docs/knowledge/`） |

#### 1.3 给推荐方案

表格之后输出一段总结，说人话：

> **推荐方案**：删除 helper_v1.py、debug_camera.py；把 utils_math.py 移到新建的 utils/math.py；render.py 保留为主入口；notes.txt 转入 docs/knowledge/notes.md。完成后主目录只剩 render.py 和 utils/。

#### 1.4 等用户决策

用户可以：
- 全盘采用 → "按推荐方案执行"
- 自定义 → "保留 helper_v1.py 不删、debug_camera.py 删、其他按推荐"
- 让 agent 解释 → "为什么 render-bkup.py 你建议保留？"

**不要在这一步催促用户。** 收尾文档的核心价值就是用户深思熟虑后的决策被记录下来。

#### 1.5 安全网（执行清理前必做）

- **如果是 git 仓库**：`git status --porcelain`。有 dirty changes → 强烈建议用户先 commit；用户拒绝 commit 又坚持要清理 → **agent 必须 abort，不能强行执行**。理由：清理操作会移动/删除文件，未保存的工作可能丢失，这种风险远大于让用户多敲一个 commit。
- **如果不是 git 仓库**：询问"要不要先建一个 backup tarball？" 用户同意则：
  ```bash
  tar -czf .wrap-up-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
    --exclude=.git --exclude=node_modules --exclude=__pycache__ .
  ```

#### 1.6 Dry-run batch

把所有计划动作汇总成一个清单给用户最后过目：

```
将执行：
1. mkdir -p utils
2. git mv utils_math.py utils/math.py        # 或 mv 如果非 git
3. mkdir -p docs/knowledge
4. mv notes.txt docs/knowledge/notes.md
5. rm helper_v1.py debug_camera.py
```

确认后再执行（建议用 git mv 而不是 mv，保留 history）。

### Phase 2 — 交接文档生成

#### 2.1 目标产物结构

```
<当前目录>/
├── CLAUDE.md                     # 索引层：引用 rules + knowledge + 简短结构说明
├── AGENTS.md → CLAUDE.md         # 软链接（OpenAI Codex CLI 约定，跨 agent 兼容）
├── .claude/
│   └── rules/                    # 硬约束：命令、风格、禁止事项
│       ├── runtime.md
│       └── style.md              # 可选，按需建
└── docs/
    └── knowledge/                # 状态与背景：会随时间变化的事实
        ├── background.md
        ├── progress.md
        ├── decisions.md
        └── todo.md
```

#### 2.2 rules/ vs knowledge/ 写作规范

**判断规则**：这条信息会随时间过期吗？

- **不会过期** → 放 `rules/`：怎么运行、命令格式、风格约定、禁止事项、目录命名规则。
- **会过期** → 放 `knowledge/`：当前进度、未完成 list、决策原因、踩过的坑、上下游联系人。

```
rules/    — "怎么做事的规范"   — 改了代码不需要改 rule
knowledge — "现在的状态与历史" — 进度变了就要更新
```

**例子对比**：

| 内容 | 类别 | 文件 |
|---|---|---|
| "运行 main.py 必须先 source venv && conda activate papervis" | rule | `rules/runtime.md` |
| "目前完成了 Bar-Chart 的配色，柱形宽度还没敲定" | knowledge | `knowledge/progress.md` |
| "输出目录命名约定是 outputs_<scene>_<variant>" | rule | `rules/runtime.md` |
| "尝试过用 seaborn 但布局不灵活，改回 matplotlib" | knowledge | `knowledge/decisions.md` |
| "下次要做 PCC 模型对比的子图" | knowledge | `knowledge/todo.md` |
| "禁止修改 raw/ 下原始数据" | rule | `rules/runtime.md` |

模板见 `references/rules-templates.md` 和 `references/knowledge-templates.md`。

#### 2.3 信息来源

按这个顺序填充内容，缺了主动问用户：

1. **当前对话历史**：本次会话讨论过什么、做了什么决定。
2. **git log**：`git log --oneline -20` 拿最近的提交主题。
3. **代码注释和文档字符串**：`head -50 <main_script>`。
4. **现有 README / readme.txt** 如果有。
5. **直接问用户**：以上都没覆盖到的关键信息（比如"这个项目最终目标是什么？"、"什么时候算完成？"）。

不要瞎编。问用户的成本远低于一份错的交接文档。

#### 2.4 CLAUDE.md 模板

完整模板见 `references/claude-md-template.md`。核心结构：

```markdown
# <directory-name>

> 由 wrap-up skill 生成于 <YYYY-MM-DD>。再次进入此目录时，按本文档恢复 context。

## 主入口
`<main_script>` — <一句话说明它做什么>

## 怎么运行
<最常用的一两条命令>

## 目录结构
- `<main_script>` — 主逻辑
- `utils/` — 功能函数
- `<output dirs>` — 输出（标注是否 gitignored）

## Rules（运行约束 — always-on）
- [运行环境与命令](.claude/rules/runtime.md)
- [代码风格](.claude/rules/style.md)

## Knowledge（项目背景 — on-demand）
- [项目背景与目标](docs/knowledge/background.md)
- [当前进度](docs/knowledge/progress.md)
- [关键决策](docs/knowledge/decisions.md)
- [TODO](docs/knowledge/todo.md)

## 上下文恢复提示
你（agent）读到这里时，先扫一遍 Rules，然后按当前任务从 Knowledge 里挑相关章节读。
不要无脑全读 — knowledge/ 是 on-demand。
```

#### 2.5 AGENTS.md 软链接

```bash
if [ ! -e AGENTS.md ]; then
  ln -s CLAUDE.md AGENTS.md
fi
```

理由：OpenAI Codex CLI（以及越来越多其他 agent CLI）默认读 AGENTS.md。一个软链接覆盖所有约定，不重复维护两份内容。若 `AGENTS.md` 已存在，不要强制覆盖；先检查它是否已经指向 `CLAUDE.md`，如果是独立文件则向用户报告可能存在双入口 drift。

#### 2.6 父目录 CLAUDE.md 的处理

如果当前目录有父目录 `CLAUDE.md` / `AGENTS.md`（比如 `~/workspace/visualization/CLAUDE.md` 和对应 `AGENTS.md`），**不要修改父目录文件**。Claude Code 通过父目录 `CLAUDE.md` 读取项目级规则；Codex 通过父目录 `AGENTS.md` 读取项目级规则。新建的子目录 `CLAUDE.md` / `AGENTS.md` 是补充而非替代。

可选：在子目录 `CLAUDE.md` 顶部加一句"父目录项目 guide（CLAUDE.md / AGENTS.md，如有）提供项目级规则，本文件提供本子目录的运行细节"，让 agent 知道两者关系。

### Phase 3 — 收尾提示

skill 跑完后，告诉用户：

> 已完成。下次进这个目录开 Claude Code / Codex CLI，会分别通过 CLAUDE.md / AGENTS.md 加载这份 guide。
> 你可以直接说"我们继续上次的工作"、"看 progress 然后继续 todo 里的第一项"。
> 如果你之后要审计 context 系统的健康度，运行 `/context-audit`，它会同时检查 AGENTS.md / CLAUDE.md 入口。

## Safety Constraints

写进 SKILL.md 显式约束 agent 行为：

1. **Phase 1 不能跳过用户决策直接清理**。哪怕用户说"按你的推荐来"，也要把推荐方案完整列出后等"OK"再动手。
2. **dirty git 仓库 + 用户拒绝 commit → 必须 abort 文件操作**。可以继续 Phase 2（写文档不影响 working tree），但不能 rm/mv。
3. **永远 git mv 优先于 mv**（git 仓库下），保留 history。
4. **永远不删除以下文件类型**，除非用户显式点名：
   - `.env*`、`*credentials*`、`*secret*` — 凭证
   - `*-bkup.py`、`*.bak` — 用户的备份
   - `requirements*.txt`、`pyproject.toml`、`package.json` — 依赖声明
   - `LICENSE`、`COPYING` — 法律文件
5. **Idempotent**：再次跑 wrap-up 时，已有的 CLAUDE.md / rules / knowledge 走 update（合并新内容、不覆盖用户后续手改），不 overwrite。
6. **不要修改父目录的 CLAUDE.md / AGENTS.md**。

## 何时升级到独立 rule 文件

如果 wrap-up 跑完后用户反复手改某种内容（比如总在 `rules/runtime.md` 顶部加 conda env 名），下次跑可以把这种 pattern 自动化。这种迭代不是 wrap-up 本身的范畴，但你可以提示用户："你这次手改了 X 模式，下次我可以自动加上"。
