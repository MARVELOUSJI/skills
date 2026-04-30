# rules/*.md 模板

`.claude/rules/` 放**不会过期的硬约束**：运行命令、目录约定、风格规范、禁止事项。

判断"是不是 rule"的快速测试：
- 这条信息**改了代码也不用更新**吗？→ 是 → rule
- 改进度 / 改决策 / 改 TODO 都需要同步更新？→ knowledge，不是 rule

下面给三种最常见的 rule 文件骨架。按项目实际情况选择性创建。

---

## runtime.md — 运行环境与命令

`.claude/rules/runtime.md`：所有跟"怎么把代码跑起来"相关的硬约束。

```markdown
# Runtime Rules

## Environment

- Python 版本：3.11
- 虚拟环境：`<env_path>` 或 conda env `<env_name>`
- 激活：`source <env_path>/bin/activate` 或 `conda activate <env_name>`
- 依赖文件：`requirements.txt` / `pyproject.toml`

## Run Commands

主入口：

```bash
python <main_script> [args]
```

常用 invocation（按使用频率排序）：

```bash
# 默认配置跑
python <main_script>

# 调试模式
python <main_script> --debug

# 远程执行（如适用）
rca exec -n <node> -d <remote_dir> "conda run -n <env> python <main_script>"
```

## Output Conventions

- 输出目录：`<output_dir>/`
- 命名约定：`outputs_<scene>_<variant>/`（如有）
- gitignored：是 / 否
- 远程同步规则：是否在 mutagen ignore 列表

## Hard Don'ts

- 不要在本地直接 `python` 跑（如果项目是远程执行模式）
- 不要修改 `<read_only_dirs>` 下的文件
- 不要硬编码绝对路径
```

---

## style.md — 代码风格与命名

`.claude/rules/style.md`：跟代码风格、命名规则、文件组织相关的硬约束。

```markdown
# Style Rules

## Naming

- Python 函数 / 变量：snake_case
- 类：PascalCase
- 文件：snake_case.py
- <项目特有约定>

## File Organization

- 主逻辑写在 `<main_script>`
- 工具函数放 `utils/`，按主题拆文件（`utils/math.py`、`utils/io.py`）
- 测试就近放在被测文件旁，命名 `test_<被测文件>.py`

## Code Style

- 字符串：双引号优先
- import 顺序：stdlib → 第三方 → 本地
- 行宽：<上限，例如 100>
- 注释：解释 WHY，不解释 WHAT
- 单文件超过 <阈值，例如 500 行> 考虑拆分

## Logging / Print

- 调试用 print 跑完要清掉，正式 logging 用 `<logging_method>`
- print 临时用，不要 commit 到主分支
```

---

## dont.md — 禁止操作

`.claude/rules/dont.md`（按需，简单项目可以并入 runtime.md）：

```markdown
# Don't List

## Never modify

- `raw/` — 原始数据，丢失无法恢复
- `<bkup_files>` — 用户的参数备份
- `<third_party_dirs>` — 第三方代码

## Never delete

- 任何 `outputs_*/` 下的渲染产物（可能已用于论文）
- `requirements*.txt` / `pyproject.toml` — 依赖声明

## Never commit

- 凭证、token、API key（参见 `.gitignore` 是否覆盖）
- 大文件（>50MB）
```

---

## 写 rule 的注意事项

1. **每条 rule 给理由**：写"为什么"，不要光写"必须 X"。理由让 agent 在边界情况下能判断。
2. **简短具体**：rules 是 always-on 加载的，篇幅不要膨胀，每条规则 1-3 行说清楚。
3. **不要重复 knowledge**：rule 不写"目前用到 X 库"（这是 knowledge），写"使用任何新依赖前先问用户"（这是 rule）。
4. **rule 之间不要冲突**：多个 rule 文件描述同一件事的不同方面是 OK 的，但不能矛盾。

## 不要为了凑文件而拆分

如果项目很简单，所有 rule 内容塞在一个 `runtime.md` 里就够，**不需要**强行拆 style / dont 文件。模板提供选项，不提供配额。
