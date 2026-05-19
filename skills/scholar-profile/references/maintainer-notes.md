# Maintainer Notes — 经验与坑（给维护者，非运行时加载）

## 2026-05-19：不要在本环境跑 skill-creator 的描述自动优化（`run_loop`）

**问题**：定稿时跑了 skill-creator 的 `scripts.run_loop`（description 自动优化）。
它的机制是对每条 trigger eval query 反复 `claude -p`（每次=一次独立 Claude 调用，
计入用户账号用量）。20 条 query × 3 次 × 多轮 ≈ 单次跑 200~300 次 `claude -p`，
且失败后又重跑了一次。集中在很短时间内的突发调用直接把用户的 5 小时用量打满。

**更糟的是零产出**：在本环境里测试夹具每轮都 `recall=0%`
（`claude -p` 子进程根本没成功触发本 skill，所有 query 全 `rate=0/3`），
最后还在 `improve_description` 处 `claude -p exited 1` 崩溃。即烧了大量额度、
产出为零。

**结论 / 怎么做**：
- **不要**用 `run_loop` / `run_eval` 对本 skill 做描述自动优化——本环境跑不通，
  纯烧额度。
- 要调触发词，**手工小改** `SKILL.md` 的 `description`（零额外模型消耗）。
  当前手写描述已符合 repo 规范：中英文 trigger + `NOT for:` 互斥
  （scholar-agent / web-fetcher）+ 示例话术，够用。
- 任何"对每个用例反复起 Claude 子进程"的批量评测工具（run_loop、大规模
  benchmark 重跑），跑前先估算 `调用次数 × 是否真有产出`，失败一次就别盲目重试。

**Lesson**：批量 `claude -p` / 多子代理评测会以**用户账号用量**计费且突发性强；
失败模式（recall=0% 全 0/3）出现时立即停，不复跑。

## 关于 Google Scholar 抓取（实测）

`scholar.google.com` 对 WebFetch / Jina / defuddle / markdown.new 基本全程 403
（反爬 "automated queries"）。`source-playbook.md` 已要求直接降级到
Wikipedia / DBLP / Semantic Scholar / 个人主页，并如实标注指标缺口，**不编造数字**。
这是预期行为，不是 bug。Scholar profile 的 `citations?user=<ID>` URL 通常仍能从
搜索结果片段拿到——务必填进节点的 `scholar_url`（viewer 节点面板要用）。
