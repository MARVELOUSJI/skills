# Source Playbook — 各来源站点抓取手法与代理

目标：高效拿到**可引用**的一手/可信资料，喂给证据表（见 citation-rules.md）。

## 渠道地图

| 想要的信息 | 首选来源 | 站点 |
|---|---|---|
| 研究方向 / 代表作 / 引用 / h-index / 共同作者 | **Google Scholar profile** | scholar.google.com/citations?user=… |
| 发表列表（结构化、稳定） | DBLP、Semantic Scholar | dblp.org、semanticscholar.org |
| 博士导师 / 学术家谱 | Mathematics Genealogy Project、Academic Family Tree | mathgenealogy.org、academictree.org |
| 生平 / 奖项 / 师承叙述 | Wikipedia、本人主页/CV | en.wikipedia.org、个人主页 |
| 重大奖项官方认定 | 官方获奖页 | amturing.acm.org、mathunion.org（Fields）、各学会 Fellow 名录 |
| 课题组学生（徒子徒孙） | 课题组主页 / "Group"/"Alumni" 页 | 实验室官网 |

## 抓取手法（关键：Google Scholar 是 JS + 反爬）

- **不要**用内置 `WebFetch` 硬抓 Google Scholar / 复杂 JS 页：拿不到正文且易触发验证。
- **优先调用 `web-fetcher` skill**（同仓库）：它对 JS/登录墙页面有 OpenCLI / Jina Reader
  路由，并复用浏览器登录态。把目标 URL 交给它取 markdown。
- 一般静态页（Wikipedia、DBLP、官方获奖页、多数高校主页）：`WebFetch` 或
  `WebSearch` → 命中后 `WebFetch` 即可。
- `WebSearch` 先行定位：`"<name>" <affiliation> google scholar`、
  `"<name>" PhD advisor`、`"<name>" mathematics genealogy`、
  `"<name>" lab students alumni`。

## 代理（受限网络 / Clash Verge）

在部分受限网络环境下，Google / 部分外站需走代理。

- 代理靠**环境变量**（用户的 cc/cct 别名已 inline-export `http_proxy`/`https_proxy`/
  `all_proxy`，端口 **7897**）。脚本/命令里**绝不**硬编码代理 URL 或端口。
- `web-fetcher` 经 curl/httpx 自动继承这些 env。
- 服务不可达时**优雅降级**：换 DBLP/Semantic Scholar/Wikipedia 等可达来源；
  在报告里如实说明"Google Scholar 当前不可达，引用/h-index 数据缺失"，
  **不要**凭印象编造数字（违反零幻觉）。

## 取数注意

- Google Scholar 的"Cited by / h-index"会随时间变 → 报告里务必写**快照日期**。
- 区分同名学者：核对机构、研究方向、代表作是否与 Phase 0 锁定的人一致；不一致就不是同一人。
- 师承关系优先采信：本人 CV/主页 > Math Genealogy > Wikipedia > 访谈 > 二手汇编。
  二手说法之间冲突时，在报告中并列说明分歧并各自给来源，而非武断下结论。
- 抓不到页面正文时，**不要**根据搜索结果摘要猜测页面内容当作引用——只引用你确实读到的文字。
