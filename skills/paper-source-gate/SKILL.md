---
name: paper-source-gate
description: "Guard Chrome/PDF paper analysis against source or task drift; use when a user supplies an arXiv PDF/current tab or a long paper-reading task switches contexts. Companion check for paper-analyzer: records the paper's identity once and verifies the final delivery still concerns that source. Triggers: 'analyze this tab/PDF', 'this arXiv paper', 'make sure it is the right paper', '分析当前这个 PDF', '这篇 arXiv', '确认读的是这篇论文', '别串到别的论文'. NOT for: paper discovery or filtering (use scholar-agent), the analysis itself (use paper-analyzer), or judging whether a paper's claims are correct."
argument-hint: "[paper URL or local PDF path]"
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash
---

# Paper source-identity gate

## When to use

Use for browser-driven or local-PDF paper analysis, especially when the user names a paper/URL/arXiv ID, requests `paper-analyzer`, or the task spans multiple context/tool steps. Do not use it to establish that a paper's claims are correct; it only verifies that the final delivery concerns the requested source.

## Inputs and context to gather

1. Record the user's requested URL/arXiv ID, title if supplied, desired language, and requested analysis angle.
2. From the selected tab or local PDF, record the authoritative URL, title, version, date, page count, local path, and SHA-256 when practical.
3. Create a small checkpoint/constraints note with those identity fields and the evidence-output directory.

## Procedure

1. Confirm the selected tab/PDF identity before extracting evidence. If any supplied identifier conflicts, ask or stop before analysis.
2. Extract text into a paper-specific output directory. If Poppler is unavailable, use Ghostscript (check `command -v gs` first):
   ```sh
   gs -q -dNOPAUSE -dBATCH -sDEVICE=txtwrite -sOutputFile=work/<paper>/page-%02d.txt <selected.pdf>
   ```
3. Keep every claim, page/table/figure reference, citation, and draft conclusion tied to that checkpointed identity.
4. Before final delivery, compare all of: selected URL, arXiv ID, title, version, page count, SHA-256 (if recorded), checkpoint, evidence paths, and final citations.
5. If any field refers to a different paper, stop. State the mismatch and return to the authoritative source; do not submit a mixed or substituted analysis.
6. Separate paper-grounded facts from domain-transfer interpretations (for example, robot/embodied-AI interview lessons).

## Efficiency plan

- Capture the identity card once and reuse it across the task.
- Prefer extracted text/tables; render only pages needed to resolve ambiguity.
- Do not return full base64 image payloads from visual inspection.
- Stop early on a mismatch instead of continuing evidence collection for a different source.

## Pitfalls and fixes

- Final draft names a different title/arXiv ID/page count -> source drift; run the full final comparison and restart from the recorded source.
- Evidence is extracted but no requested analysis is delivered -> finish the claim-to-evidence answer; extraction alone is not completion.
- PDF tools are missing -> use Ghostscript `txtwrite`; treat Fontconfig cache warnings separately from extraction success.

## Verification checklist

- [ ] Final title/URL/arXiv ID/version match the user's request.
- [ ] Final citations and evidence paths point only to the selected paper.
- [ ] Page count and SHA-256 match the recorded identity when available.
- [ ] Requested language and analysis angle are addressed.
- [ ] Transfer inferences are labeled as inferences, not paper results.
