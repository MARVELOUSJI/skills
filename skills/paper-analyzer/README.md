# Paper Analyzer

English | [中文](README.zh-CN.md)

> Deep-read one paper with a three-pass workflow: build the map, understand Motivation → Task/Setting → Method → Experiments, then audit whether the evidence supports the claimed Contribution/Novelty.

## Features

- **Three-pass reading** — orientation → structured understanding → evidence audit
- **Reader-centered backbone** — Motivation → Task/Setting → Method → Experiments → Contribution/Novelty
- **Mechanism-complete method walkthrough** — Trace the end-to-end data flow and explain each important module's input, internal operation, output, connections, and role
- **Adaptive Method and Training Card** — Cover losses, training stages, data, optimization, and inference only to the depth needed by the paper and reading goal
- **Experiment–claim matrix** — Explain what every main experiment tests, how it tests it, and how much the result supports
- **Figure/Table Ledger** — Explain every main-text figure and table; include appendices for exhaustive or reproduction-focused reads
- **Three novelty levels** — Separate author claims, internally demonstrated contributions, and externally verified novelty
- **Evidence grounding** — Link headline numbers and capability claims to pages, sections, tables, or figures
- **Concise output** — Lead with plain-language conclusions and move full numbers and locators to an evidence appendix
- **Flexible sources** — Local PDFs, full-text URLs, arXiv, and optional NotebookLM

## Install

```bash
npx skills add jiahao-shao1/sjh-skills --skill paper-analyzer
```

## Optional Dependency

Direct reading needs only the agent's PDF, file, and web tools. NotebookLM mode additionally requires:

- [notebooklm-py](https://github.com/teng-lin/notebooklm-py): `pipx install "notebooklm-py[browser]"`
- A valid NotebookLM Google login: `notebooklm login`

## Usage

```text
Analyze paper 2603.14821 in depth
What are this paper's motivation, setting, and method?
Walk me through how every important module in this system actually works
Explain what each experiment tests and whether the result supports the conclusion
Is the claimed novelty actually supported by prior work?
Deep-read ./papers/example.pdf and verify the headline numbers
Cross-check this paper with NotebookLM
```

## Workflow

1. **Set depth and source** — Standard deep read by default; reproduction or review requests receive a stronger audit.
2. **Pass one: build the map** — Identify paper type, research question, headline claim, and key figures/tables.
3. **Pass two: understand** — Analyze Motivation and Task/Setting, then trace the complete method and each important module before examining Experiments.
4. **Pass three: audit** — Check direct evidence, alternative explanations, generalization, and reproducibility.
5. **Contribution and novelty** — Separate author claims, internal evidence, and external prior-work verification.

The causal chain (phenomenon → setup → attribution → solution), taxonomy tagging, research-framework mapping, and cross-paper connections are optional modules rather than the main report structure.

## Default Output

The answer opens with at most six short takeaways: Motivation, Task, Method, core result, Contribution/Novelty, and main limitation. Method length is not fixed: a simple method stays short, while a complex system expands until the reader can trace the full data flow and explain how every important module works. Experiments cover every distinct main-text claim, metric meanings, and the Figure/Table Ledger.

## Reading Modes

- **Direct (default):** Read the original PDF or full-text page.
- **NotebookLM-assisted:** Use when requested or for persistent Q&A; verify important conclusions in the paper itself.
- **Dual verification:** Use for critical claims, complex tables/appendices, or explicit cross-checks.

An abstract or metadata page is insufficient for a definitive deep analysis. When full text is unavailable, the skill marks substantive conclusions as unverified instead of guessing.

## When to Use vs. Scholar Agent

| Task | Use |
|---|---|
| Discover, filter, or collect papers | scholar-agent |
| Deep-read one specific paper | paper-analyzer |
| Explain experiments and evidence one by one | paper-analyzer |
| Only add a paper to NotebookLM | scholar-agent |
| Broad multi-paper literature survey | scholar-agent or a literature-research workflow |

## Method References

- [S. Keshav — How to Read a Paper](https://systems.cs.columbia.edu/ds2-class/papers/keshav-paper.pdf)
- [PLOS — Ten Simple Rules for Reading a Scientific Paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008032)
- [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist)

## License

MIT
