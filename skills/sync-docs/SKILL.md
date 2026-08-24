---
name: sync-docs
description: "Check whether recent code changes require documentation or agent-context updates, removals, or rule slimming. Triggered when user says 'sync docs', '文档同步', '检查文档', '同步 AGENTS/CLAUDE', or asks whether Codex/Claude project context is stale after implementation work. NOT for: a repository-wide context architecture and reachability audit without a recent change window (use context-audit)."
---

Inspect the relevant recent change window (`git diff`, the current branch, or up to the last five commits), extract the facts that changed, then report which documentation locations must be updated, pruned, or checked for conflicts. Do not assume `HEAD~5` exists or that every recent commit is relevant.

Checklist items (detect only directories and systems that actually exist):

1. **Changed facts** — List the concrete new state: renamed paths, dependencies, configuration keys, commands, invariants, behavior, or removed features. Verify against source files rather than inferring from filenames alone.
2. **Knowledge base** — Does `docs/knowledge/` need a new learning, an update to an existing entry, or a `[DEPRECATED]` marker with a replacement?
3. **Experiment registry** — Are new experiments registered, and did canonical results or status change?
4. **Project instructions** — Do `AGENTS.md` and `CLAUDE.md` expose the same project guide? If `CLAUDE.md` exists and `AGENTS.md` is missing, flag Codex context as stale. If both exist and `AGENTS.md` is not a symlink to `CLAUDE.md`, compare their `.claude/rules/` references for drift.
5. **Rules vs knowledge** — Route content by stability:
   - Stable, imperative, repeatedly needed constraint → `.claude/rules/`
   - How-to, troubleshooting, dated evidence, measured values, run tags → `docs/knowledge/`
   - Keep a rule to its trigger, hard constraint, exact stable values, and a short knowledge pointer
6. **Rule hygiene** — Flag rules that became dated changelogs, duplicate the canonical guide, retain superseded instructions, or contain procedural/reference detail that should move to knowledge. Sync is bidirectional: prune or migrate stale material as well as adding new text.
7. **Conflict scan** — Search documentation for the old and new names or values. Old and new states coexisting is higher priority than a missing update.
8. **README and setup docs** — Do installation steps, commands, directory structure, examples, and configuration templates match the code?
9. **Strategy docs** *(only if `docs/strategy/` exists)* — Do vision, roadmap, or paper outline reflect the change? Flag stale strategy docs only when the code change is strategically relevant; commit count alone is supporting evidence, not proof.

Output a concise change-impact checklist:

- Changed fact
- Expected documentation locations
- Status: `up to date`, `needs update`, `conflict`, or `not applicable`
- Evidence path and line when available
- Exact recommended edit, migration, or removal

Report only; do not modify documentation. If the user wants a full coverage graph, orphan scan, guide leakage check, or repository-wide slimming plan, hand off to `context-audit` rather than duplicating it here.
