# Paper Analyzer

[English](README.md) | 中文

> 用“三遍阅读 + 用户主线 + 证据审计”深读单篇论文：先建立全貌，再理解 Motivation、Task/Setting、Method 和 Experiments，最后判断 Contribution/Novelty 是否被证据支持。

## 功能

- **三遍阅读**：快速建图 → 结构化理解 → 证据审计
- **用户导向主线**：Motivation → Task/Setting → Method → Experiments → Contribution/Novelty
- **实验—主张矩阵**：逐项说明每个主要实验想验证什么、如何验证、实际支持到什么程度
- **三层新颖性**：区分作者声称、论文内部证明和外部文献核验
- **证据定位**：关键数字和能力声明关联页码、章节、表格或图片
- **简洁输出**：结论优先，正文易懂，完整数字与定位放到证据附录
- **灵活读取**：支持本地 PDF、全文链接、arXiv 和可选 NotebookLM

## 安装

```bash
npx skills add jiahao-shao1/sjh-skills --skill paper-analyzer
```

## 可选依赖

直接读取模式只需要 agent 可用的 PDF、文件和网页工具。NotebookLM 模式额外需要：

- [notebooklm-py](https://github.com/teng-lin/notebooklm-py)：`pipx install "notebooklm-py[browser]"`
- 有效的 NotebookLM Google 登录：`notebooklm login`

## 使用

```text
分析这篇论文：2603.14821
这篇论文的 motivation、setting 和 method 分别是什么？
逐项解释每个实验想验证什么，结果是否真的支持结论
这篇论文声称的 novelty 到底成立吗？
深读 ./papers/example.pdf，并核对关键数字
用 NotebookLM 交叉核验这篇论文
```

## 工作流

1. **确定深度与来源**：默认标准深读；复现或审稿请求会加强审计。
2. **第一遍——快速建图**：识别论文类型、研究问题、核心主张和关键图表。
3. **第二遍——结构化理解**：依次分析 Motivation、Task/Setting、Method 和 Experiments。
4. **第三遍——证据审计**：检查主张是否有直接证据、是否存在替代解释，以及泛化和复现边界。
5. **贡献与新颖性**：分别报告作者声称、论文内部证据和外部相关工作核验。

因果链（现象→设置→归因→解法）、taxonomy、研究框架映射和跨论文连接均为按需模块，不再替代主工作流。

## 默认输出

开头用六句以内说明：Motivation、Task、Method、核心结果、Contribution/Novelty 和主要局限。随后按需展开 Setting Card、实验—主张矩阵、批判检查和证据附录。

## 读取模式

- **直接读取（默认）**：读取原始 PDF 或全文链接。
- **NotebookLM 辅助**：适合用户明确要求或需要持续问答的场景；重要结论仍回到原文核验。
- **双重核验**：用于关键结论、复杂表格/附录或明确的交叉检查。

摘要或元数据页面不足以支持确定性的深度分析。缺少全文时会明确标注“未核验”，不会强行下结论。

## 何时用 vs. Scholar Agent

| 任务 | 使用 |
|---|---|
| 发现、筛选或收藏论文 | scholar-agent |
| 深度分析一篇特定论文 | paper-analyzer |
| 逐项解释实验与证据 | paper-analyzer |
| 仅添加论文到 NotebookLM | scholar-agent |
| 多篇论文的广泛综述 | scholar-agent 或文献调研流程 |

## 方法参考

- [S. Keshav — How to Read a Paper](https://systems.cs.columbia.edu/ds2-class/papers/keshav-paper.pdf)
- [PLOS — Ten Simple Rules for Reading a Scientific Paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008032)
- [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist)

## 许可证

MIT
