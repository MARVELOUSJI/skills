# Cleanup Heuristics

Phase 1 评估表的判断启发式。**这些是默认建议，不是硬规则** —— 用户的具体上下文永远优先。

## 文件名 pattern → 通常角色

| Pattern | 典型角色 | 默认推荐 |
|---|---|---|
| `main.py`, `run.py`, `app.py`, `cli.py` | 主入口 | **保留**（如果项目有多个入口候选，问用户） |
| `<name>_v1.py`, `<name>_v2.py`, `<name>_old.py` | 早期版本 | **删除**（先 grep 确认无引用） |
| `<name>-bkup.py`, `<name>.bak`, `<name>.backup` | 用户的参数备份 | **保留**（用户惯例，不主动删） |
| `debug_<name>.py`, `test_debug_*.py`, `tmp_*.py` | 临时调试代码 | **删除**（注释里如果写"临时"，更确认） |
| `test_<name>.py`, `<name>_test.py` | 单元测试 | **保留**（移到 tests/ 或就近放） |
| `notes.txt`, `TODO.txt`, `scratch.md` | 临时笔记 | 评估内容：有用 → 转入 `docs/knowledge/`；过期 → **删除** |
| `<name>.ipynb` (.ipynb_checkpoints) | Jupyter 缓存 | **删除**（缓存目录） |
| `*.pyc`, `__pycache__/` | Python 字节码 | **删除**（应该被 gitignore） |
| `.DS_Store` | macOS 元数据 | **删除** |
| `requirements*.txt`, `pyproject.toml`, `package.json` | 依赖声明 | **保留**（永远） |
| `LICENSE`, `COPYING`, `NOTICE` | 法律文件 | **保留**（永远） |
| `.env`, `.env.local`, `*credentials*`, `*secret*` | 凭证 | **保留**（永远不动；如果错误地放在了仓库里，提醒用户但不动手） |
| `README*.md`, `CHANGELOG*.md` | 文档 | **保留**（如果内容过期建议用户更新） |
| `outputs/`, `logs/`, `checkpoints/` | 运行产物 | 通常 gitignored，不在评估表里出现；出现了说明没 gitignore，提醒用户。 |

## 函数 / 模块 → 是否移到 utils/

判断一个文件该不该移到 `utils/`：

- ✅ **应该移**：通用工具函数（数学运算、IO、字符串处理），主脚本以外多处使用，没有副作用，可独立测试。
- ❌ **不该移**：业务逻辑核心（属于主脚本），强耦合于主流程的辅助函数（直接 inline 或留在主脚本），单文件可读完不复杂的项目。

如果项目就一个主脚本 + 一两个 helper 函数，**别强行建 utils/**。空 utils/ 反而增加噪音。

## 风险等级判断

- **低**：grep 确认无引用 + 文件名/注释明确写"临时/调试/废弃" + git log 显示最近未改动。
- **中**：被多处引用，但都是过期版本；或者引用关系不太明朗，需要进一步确认。
- **高**：核心模块、依赖声明、配置文件、用户的参数备份。**不在没用户明确指示下动**。

写风险评估时**给具体证据**，不要光写一个等级：

> ❌ 低
> ✅ 低 — 已 `grep -rn helper_v1` 全仓库，仅 `tests/test_helper.py` 有一处导入但已被注释；git log --follow 显示最后一次 commit 在 3 个月前

## 归档 vs 删除

不确定要不要彻底删除？建议归档：

- 建一个 `archive/` 子目录（添加到 `.gitignore` 或保留 git 但标注用途）
- `git mv old_file.py archive/old_file.py`
- 在 `docs/knowledge/decisions.md` 记一笔："archive/old_file.py 是 X 时期的方案，<日期> 改为 Y，保留以备回溯"

**git 仓库下永远 git mv 优先于 mv** —— 保留文件历史。

## 重命名为 main.py 的判断

- ✅ 当前主入口名字不直观（如 `render_gaussian_circles3_synthetic_volume_paper.py`）
- ✅ 项目本身只有一个主入口，重命名不会和别的文件冲突
- ❌ 项目有多个入口（如 `render.py`、`crop.py` 各自独立），别为了"统一"硬改名
- ❌ 文件名在用户的 README、shell history、其他文档里被频繁引用，改名会让这些引用过期

如果不重命名但名字确实长，**在 CLAUDE.md 顶部明确指出主入口是哪个**就够了。

## 在文件作用列里写什么

不要光写"工具函数"或"主脚本"，要给一句话理由：

| ❌ | ✅ |
|---|---|
| 工具函数 | 数学辅助函数（rotation matrix、quaternion 转换） |
| 主脚本 | 渲染 3DGS 椭球到论文图，主入口 |
| 调试代码 | 早期相机姿态调试，main.py 不再使用 |
| 笔记 | 用户对配色方案的对比记录 |

具体让用户能直接判断要不要保留。
