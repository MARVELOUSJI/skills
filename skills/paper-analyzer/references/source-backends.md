# Source and Reading Backends

Read this file only when source acquisition, NotebookLM, privacy, or version conflicts require operational detail.

## Source Preference

Prefer sources in this order:

1. The exact local PDF or version supplied by the user.
2. Official publisher/proceedings full text or arXiv PDF/HTML.
3. Official supplementary material or project repository.
4. Author-hosted manuscript.
5. Metadata and secondary descriptions for discovery only.

Record the version or date when multiple versions exist. Do not silently combine numbers from different versions.

## Direct Reading

- Extract text for search and structure.
- Render and inspect pages when equations, multi-column layout, plots, diagrams, or tables matter.
- Verify captions, footnotes, legends, axes, units, and appendix references visually.
- Preserve precise page/table/figure/section locators.

## NotebookLM-Assisted Reading

NotebookLM is optional and requires the `notebooklm` CLI plus a valid Google login.

Check authentication:

```bash
notebooklm auth check --test
```

Select an existing notebook and inspect its sources:

```bash
notebooklm use <notebook-id>
notebooklm source list
```

When adding a public arXiv paper, prefer full HTML and fall back to the PDF:

```bash
notebooklm source add "https://arxiv.org/html/<ID>"
notebooklm source add "https://arxiv.org/pdf/<ID>"
```

If authentication fails, continue with Direct reading unless the user explicitly requires NotebookLM. If no notebook is specified, ask before creating one. Ask for explicit permission before uploading a private, proprietary, or unpublished local source.

NotebookLM answers are retrieval aids. Re-open every headline claim and number in the original paper before treating it as verified.

## Dual Verification

Use Direct and NotebookLM-assisted reading together when:

- the user explicitly requests a cross-check;
- a central claim depends on a complex table or appendix;
- source retrieval gives inconsistent answers;
- the decision is high impact.

When readings conflict, the exact original-paper passage, table, or figure controls. Report unresolved conflicts rather than averaging or guessing.
