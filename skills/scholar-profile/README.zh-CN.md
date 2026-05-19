# scholar-profile（学者画像 + 全局人物关系图）

**快速、零幻觉**地认识一个学者，并把他并入一张**全局可交互拖动**的人物关系图。

调用：`/scholar-profile <姓名> [机构/方向消歧]`
例：`/scholar-profile Yann LeCun`、`/scholar-profile 李飞飞 Stanford`。

## 产出

四段式画像（`~/.config/scholar-profile/profiles/<slug>.md`）：

1. **人物经历**：按时间顺序的关键节点，并附个人主页 / 公开 CV 链接（没有则标注）。
2. **人际关系（重点）**：导师（上溯 1 代）、学生及徒孙（下溯 2 代）、知名直接合作者，
   每条关系都带来源链接。
3. **研究领域与代表工作**：以 Google Scholar 为主线（方向、代表作、引用、h-index），
   逐条引用。
4. **评价**：用奖项/引用/讲席等硬指标说级别，并给一个**显式标注为"类比·主观"**的
   跨领域类比帮你建立直觉。

同时此人被并入全局图 `~/.config/scholar-profile/viewer.html` —— 单文件 HTML，
**零外部依赖**（无 CDN，离线 / 墙内 / file:// 双击都能用），浏览器打开即可拖动节点、
平移、缩放、点节点/连线查看来源链接。每问一个新人，只要与图中已有人存在**有来源**的
关系，就自动连边（师承自动规范化、去重）。

## 零幻觉契约

每句结论后紧跟来源链接；查不到可靠出处的内容保留但标 `〔未找到可靠来源〕`；
类比/推断标 `〔类比·主观〕`/`〔推断〕`。关系图只有在有来源时才画实边，
未证实的猜测显示为灰点线"未证实"候选，绝不当事实。

## 存储

所有状态在**仓库外** `~/.config/scholar-profile/`（`graph.json` 数据真相、
`viewer.html` 重生成的查看器、`profiles/*.md` 报告）。仓库不存任何个人数据。

## 依赖

无新增外部依赖。`scripts/graph_store.py` 仅用标准库，生成的关系图查看器也**零库依赖**。
Google Scholar 等 JS 页面抓取复用同仓库 `web-fetcher` skill；代理走环境变量
（端口 7897），不硬编码。大段描述性正文用中文，英文专有名词/术语保留。

## 不适用

读/摘要论文或 Scholar Inbox 每日推送（→ `scholar-agent`）；仅把单个网页转 markdown
（→ `web-fetcher`）；写文献综述；非学术人物传记。

## 维护提示

- 在 repo 源位置编辑：`~/workspace/skills/skills/scholar-profile/`，勿改 `~/.claude/skills/` 软链接。
- 改完 `~/workspace/dotfiles/scripts/setup-skills.sh` 已会自动建软链接；提交 `feat: add scholar-profile`。
- 脚本用法见 `scripts/graph_store.py --help` 或其顶部 docstring。
