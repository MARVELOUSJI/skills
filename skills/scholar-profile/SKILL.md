---
name: scholar-profile
description: >
  快速、严格无幻觉地"认识一个学者"：查网上公开资料，产出四段式画像
  （①人物经历(按时间顺序，含个人主页/CV 链接) ②人际关系 ③研究领域与代表工作
  ④评价/级别类比），并把这个人并入一张全局可交互拖动的人物关系图，自动与图中已有学者连边。
  Triggers: "认识一下这个学者"、"介绍下 XX 教授/老师"、"这个人是谁（学术圈）"、
  "他/她的师承 / 导师是谁 / 徒子徒孙"、"学术人脉 / 合作者关系"、"他是什么级别的学者"、
  "帮我画学者关系图"、"scholar profile"、"who is professor <name>"、
  "academic genealogy / family tree of <researcher>"、"how big a deal is <researcher>".
  NOT for: 读/筛/摘要论文本身或 Scholar Inbox 每日推送（→ scholar-agent）；
  仅把某个网页抓成 markdown（→ web-fetcher）；写文献综述/技术综述；
  非学术人物的人物传记。
user_invocable: true
---

# Scholar Profile

帮用户**快速且可信地**认识一个学者，并维护一张**全局**人物关系图。

调用方式：`/scholar-profile <姓名> [机构/方向以消歧]`，例如
`/scholar-profile Yann LeCun` 或 `/scholar-profile 李飞飞 Stanford`。

## 这个 skill 的灵魂：零幻觉

用户最看重的一点——**介绍里每一句结论都必须有公开资料支撑，链接贴在该结论后面**。
没有来源宁可不写，或显式标注为未证实。详细的取证与引用红线见
`references/citation-rules.md`，**Phase 1 开始前先读它**。一句没有来源的"事实"
比少写十句话伤害大得多：用户用这个 skill 是为了建立可信认知，编造会直接摧毁它的价值。

数据与产物全部在仓库外 `~/.config/scholar-profile/`（首次运行脚本自动建）：

| 路径 | 作用 |
|---|---|
| `graph.json` | 全局关系图唯一数据真相（节点/边都带 `sources`） |
| `viewer.html` | 由脚本从 graph.json 重生成的单文件交互图 |
| `profiles/<slug>.md` | 每个学者的四段式画像报告（人物经历/人际关系/研究领域/评价） |

脚本（仅标准库，无新依赖）：
`python3 <skill-dir>/scripts/graph_store.py <subcommand>`。
子命令：`upsert-node` / `add-edge` / `detect-connections` / `render-viewer` / `list-nodes`。
`graph_store.py --help` 或读脚本顶部 docstring 看参数。

---

## Phase 0 — 锁定到正确的人

重名在学术圈很常见，搞错人会让整份报告作废，所以先消歧再调研。

1. 用 `WebSearch` 搜 `<姓名> <机构/方向> google scholar`，并尝试定位其
   Google Scholar profile（`scholar.google.com/citations?user=...`）。
2. **多个可信候选**（不同机构/方向/引用量级）→ 用 `AskUserQuestion` 列出候选
   （每项：姓名 / 机构 / 方向 / 大致引用量级 / Scholar 链接），让用户选定，**不要自己猜**。
3. 只有一个明确候选 → 简短复述"我锁定的是 X（机构 Y，方向 Z），开始调研"，继续。
4. `python3 .../graph_store.py list-nodes` 看此人是否已在全局图里：
   - 已存在 → 这次是**补充/刷新**，沿用其 node id，新增来源合并进去。

## Phase 1 — 先取证，后行文

**不要边搜边写散文。** 先建一张"证据表"，每行 = 一个待写结论 + 来源 URL + 原文摘录。
没有摘录支撑的行不许进入报告。证据表格式见 `references/citation-rules.md`。

取证渠道与抓取手法（含 Google Scholar 反爬、CN 代理 7897 经 env 不硬编码、
不可达时如何优雅降级）见 `references/source-playbook.md`。优先级：

- **人物经历 + 个人主页/CV**（第一段要用）：找其**个人主页**与公开 **CV**（学校/
  实验室页、Google Scholar 简介、LinkedIn、Wikipedia 生平段），梳理按时间顺序的关键
  节点（求学→学位→历任职位→转职/创立机构→重大荣誉时点）。找不到主页/CV 就明确标注，
  不编造。每个时间点带来源。
- **研究领域/代表作/引用/h-index** → 以其 **Google Scholar profile** 为主线
  （JS 页面，走 `web-fetcher` skill 或 Jina，别直接 WebFetch 硬抓）；
  辅以 DBLP、Semantic Scholar、个人主页 publications 页。
- **人际关系（重点）**：
  - 导师（上跳 1 跳）：博士/博后导师。来源优先 Mathematics Genealogy Project、
    个人主页/CV、毕业论文致谢、Wikipedia、可信访谈。
  - 学生（下跳 2 跳）：直接博士生 + 这些学生各自的博士生（徒孙）。来源优先
    其课题组主页/Academic Family Tree (academictree.org)/学生个人主页。
  - 知名直接合作者：高频共同作者中**学术知名**者（来源：Scholar 共同作者栏、合作论文）。
  - 深度边界与"徒子徒孙"展开规则见 `references/relationship-taxonomy.md`，**先读**。
- **评价/级别**：硬指标（总引用、h-index、重大奖项 Turing/Fields/Nevanlinna/
  IEEE/ACM Fellow、讲席教席、院士、顶会 keynote/test-of-time）——逐条带来源。

每个关系人，记录：姓名、与本人关系类型、关系说明、**来源 URL**。这些会喂给关系图。

## Phase 2 — 写画像 `profiles/<slug>.md`（四段式）

**语言规则**：大段描述性正文一律用**中文**；英文专有名词与技术术语保留原文
（人名、机构名、论文标题、`h-index`、`Turing Award`、`advisor/student/collaborator`
这类不必硬译）。目标是中文读者读着顺，不是把所有英文都翻译掉。

结构固定如下（缺来源的句子按 citation-rules 的规则标注，不许裸奔）：

```markdown
# <姓名>（<机构>）— 学者画像

> 生成于 <YYYY-MM-DD>。本报告每条结论后给出来源链接；
> 标 〔未找到可靠来源〕 的为暂未查到严格出处的内容，请谨慎对待；
> 标 〔类比·主观〕 的为帮助理解的类比，非事实陈述。

## 一、人物经历（按时间顺序）

> 个人主页：[链接](URL)（确实找不到 → 写"未找到公开个人主页" 并标 〔未找到可靠来源〕）
> 个人 CV：[链接](URL)（确实找不到 → 写"未找到公开 CV" 并标 〔未找到可靠来源〕）

按时间**正序**列出关键节点（求学/学位/任职/转职/创立机构/重大荣誉时点等），每条带来源：

- **<年份或时段>**：<经历，一句话>。[来源](URL)
- **<年份或时段>**：<经历>。[来源](URL)
- …（时间不确定的条目放在能确定的之后，并标 〔未找到可靠来源〕）

## 二、人际关系（重点）

### 关系速览（不打开网页也一眼看懂）

先给一棵纯文字缩进树，导师在上、本人居中、学生在下，让用户不依赖关系图也能秒懂：

```
        〔导师 ↑1〕 <导师姓名>（<机构>）
                     │  博士后/博士，<一句关系>
   ┌─────────────────┴─────────────────┐
              ▶ <本人姓名>（<机构>）◀
   └───────────┬───────────────┬───────┘
        〔学生 ↓1〕 <学生A>      <学生B>
                     └ 〔徒孙 ↓2〕 <学生A 的学生>
        〔知名合作者〕 <合作者X> · <合作者Y>
```

（按真实情况画；没有的层就略去。这棵树只是导览，**每个人的关系细节与来源在下方逐条列出**。）

### 师承（导师，上溯 1 代）
- **博士/博后导师**：<姓名>（<机构>），<关系说明>。[来源](URL)

### 学生与徒孙（下溯 2 代）
- **直接博士生**：<姓名>（现职），<亮点>。[来源](URL)
  - **其学生（徒孙）**：<姓名>……[来源](URL)

### 知名合作者
- <姓名>（<机构>）— <合作内容/代表合作论文>。[来源](URL)

> 关系图：本人及上述关系已并入全局可拖动关系图，**打开文末的 `viewer.html` 查看**
> （不要让用户去读 `graph.json`——那是数据存储，给程序用的）。

## 三、研究领域与代表工作（以 Google Scholar 为主线）

- **主要方向**：……[来源](Scholar/主页 URL)
- **总引用 / h-index**：……（截至 <日期>，数字会变，注明快照日）[来源](Scholar URL)
- **代表作**（按被引/影响选 3–6）：
  1. 《Title》, venue year — 被引 N。一句话贡献。[来源](URL)

## 四、评价：他是什么级别的人物

- 硬指标定位：<奖项/院士/讲席/引用量级>。[来源](URL)
- 领域内地位：<一句，带来源>。[来源](URL)
- **跨领域类比（帮助你建立直觉）**：〔类比·主观〕"在 X 领域大致相当于 Y 之于 Z"
  —— 说明类比依据（如同级奖项/奠基性贡献），但强调这是直觉类比非等价事实。

## 资料来源汇总
- [来源1](URL) — 用途
- ...
```

写完后**自检**：逐句问"这句的来源链接在哪？"。没有 → 要么删，要么标
`〔未找到可靠来源〕`。类比/推断 → 标 `〔类比·主观〕` 或 `〔推断〕`。

## Phase 3 — 并入全局关系图

目标：用户每问一个新人，这个人就进全局图，并与图中已有人**自动连边**（连边必须带来源）。

1. **upsert 本人**：构造节点 JSON 传给脚本。`relations` 三个桶里填 Phase 1 查到的
   关系人（每条带 `source`），这是后续自动连边的关键——别省。

   ```bash
   echo '{
     "name":"Yann LeCun","affiliation":"NYU / Meta AI",
     "scholar_url":"https://scholar.google.com/citations?user=...",
     "profile_md":"profiles/yann-lecun.md",
     "sources":["https://en.wikipedia.org/wiki/Yann_LeCun"],
     "relations":{
       "advisors":[{"name":"Geoffrey Hinton","source":"<URL>","note":"postdoc 1987-88"}],
       "students":[{"name":"...","source":"<URL>"}],
       "collaborators":[{"name":"Yoshua Bengio","source":"<URL>","note":"deep learning"}]
     }
   }' | python3 <skill-dir>/scripts/graph_store.py upsert-node --json -
   ```

   - **务必填 `scholar_url`**：即使 Google Scholar 页面被 403，其 profile 链接
     （`scholar.google.com/citations?user=<ID>`）通常能从搜索结果片段里拿到——
     拿到就填进节点。viewer 点开节点时这个链接可直接点；没填则 viewer 只能退化成
     "Scholar 搜索"兜底链接。
   - **务必填 `profile_md`**：值为 `profiles/<slug>.md`（相对路径）。viewer 里它会
     渲染成可点链接，点击直接在浏览器打开这份画像（viewer.html 与 profiles/ 同目录，
     相对链接才生效，别写绝对路径）。

2. **为知名关系人也建轻节点**：值得在图里出现的导师/徒孙/合作者，各 `upsert-node`
   一次（至少 name + 一个 source；尽量带上能查到的 `scholar_url`；可只写 name 占位，
   后续正式问到该人时再补全 `profile_md` 等）。

3. **自动连边**：对本人及每个新建关系人跑
   `graph_store.py detect-connections --node <id> --apply`。
   - `--apply` 只会自动落**有来源**的实边（脚本设计如此，零幻觉）。
   - 输出里 `inferred:true` 或无 `sources` 的候选（如"同机构"弱关联）**不要**当事实连；
     若你 Phase 1 已查到可靠来源，再用 `add-edge --type ... --source <URL>` 手动连。
   - 绝不用 `--allow-unsourced` 制造无源实边，除非用户明确要一条标记为"未证实"的边。
   - 边类型语义与何时算一条边见 `references/relationship-taxonomy.md`。

4. **重渲染**：`graph_store.py render-viewer`（幂等，保留用户已有数据与手动布局数据）。

## Phase 4 — 收尾（不自动打开浏览器）

给用户三件事：

1. 画像报告路径：`~/.config/scholar-profile/profiles/<slug>.md`（并在对话里贴正文）。
2. 关系图查看器路径：`~/.config/scholar-profile/viewer.html`
   —— 提示："在浏览器打开此文件（零依赖、离线可用）：拖动节点摆位、拖空白处平移、
   滚轮缩放、点节点/连线看来源链接。" **不要让用户去看 `graph.json`**（那是数据存储）。
3. 一句话总结：本人级别 + 与图中哪些已有学者建立了连接（及连接依据来源）。

> 不要产出 `NOTES.md` 之类的英文过程文件——正式画像只有 `profiles/<slug>.md`（中文）
> 与全局图。调研过程不单独落英文文档。

不要替用户打开浏览器（用户明确要求只给路径）。

## 硬约束（写进行为，别违反）

| 约束 | 原因 |
|---|---|
| 每条结论句紧跟来源链接；无源句标 `〔未找到可靠来源〕` | 用户的核心诉求，零幻觉 |
| 类比/推断显式标 `〔类比·主观〕`/`〔推断〕` | 类比有用但不能伪装成事实 |
| 关系图实边必须带 source；无源只作 inferred 候选 | 关系图也要可信，能溯源 |
| 多个同名候选必须让用户确认 | 搞错人整份报告作废 |
| 状态只写 `~/.config/scholar-profile/`，不写进 skills 仓库 | repo 不存个人数据/无硬编码路径 |
| 代理靠 env（7897），不在代码/命令里硬编码 URL/端口 | repo 规则 |
| 不替用户打开浏览器 | 用户明确要求只给路径 |
| 数字类指标注明快照日期 | 引用/h-index 会变，避免过期失真 |
