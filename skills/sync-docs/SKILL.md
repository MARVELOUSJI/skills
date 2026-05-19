---
name: sync-docs
description: Check whether documentation and agent context need updating after code changes. Triggered when user says "sync docs", "文档同步", "检查文档", "同步 AGENTS/CLAUDE", or asks whether Codex/Claude project context is stale.
---

Check recent code changes (`git diff HEAD~5 --name-only`), scan the project's documentation system, and report what needs updating.

Checklist items (detect based on directories that actually exist in the project):

1. **Knowledge base** — Does `docs/knowledge/` have new learnings to record?
2. **Experiment registry** — Are new experiments registered in the registry?
3. **Project instructions** — Do `AGENTS.md` and `CLAUDE.md` expose the same project guide? If `CLAUDE.md` exists and `AGENTS.md` is missing, flag Codex context as stale. If both exist and `AGENTS.md` is not a symlink to `CLAUDE.md`, compare their `.claude/rules/` references for drift.
4. **Rules** — Are there new hard constraints to codify in `.claude/rules/`? Are rule references from `AGENTS.md` / `CLAUDE.md` still valid?
5. **README** — Does the project README match the current code structure?
6. **Strategy docs** *(only if `docs/strategy/` exists)* — Do vision, roadmap, or paper-outline reflect recent changes? Compare `git log` activity against strategy doc last-modified dates. Flag docs that haven't been updated in 5+ commits of relevant code changes. Pair with `/project-review` for full strategic analysis.

Output a checklist marking each item as "needs update" or "up to date". Report only — do NOT auto-modify.
