---
name: context-audit
description: "Audit project context management (AGENTS.md/CLAUDE.md, rules, knowledge) for Claude Code and Codex compatibility. Checks that knowledge files are reachable from rules, rule references are valid, AGENTS.md exposes the same project guide as CLAUDE.md for Codex, and guide files avoid knowledge index leakage. Triggers: 'audit context', 'check context', 'context hygiene', 'context audit', '检查 context', '审计上下文', 'knowledge 覆盖检查', 'Codex 上下文检查'. NOT for: code review, rule content correctness, or knowledge content quality."
user_invocable: true
---

# Context Audit

Audits the project's cross-agent context management system (AGENTS.md / CLAUDE.md / rules / knowledge) against the **progressive disclosure** architecture:

```
AGENTS.md (Codex entry) -> usually a symlink to CLAUDE.md
CLAUDE.md (Claude Code entry) — describes architecture, no detailed index
  └─ Rules (.claude/rules/) — referenced by the guide, inline `> 详见` refs to knowledge
       └─ Knowledge (docs/knowledge/) — on-demand deep experience
```

## When to Use

- After adding new knowledge files — verify they're indexed from a rule
- After refactoring rules — verify no references broke
- After migrating a project to Codex — verify `AGENTS.md` exists and points at the same guide
- Periodic hygiene check — catch drift over time
- After onboarding a new domain — verify the new rule covers its knowledge files

## Execution

### Phase 1: Discovery

Scan the project to find all context files:

```bash
# Knowledge files
find docs/knowledge/ -name "*.md" -type f 2>/dev/null | sort

# Rule files
find .claude/rules/ -name "*.md" -type f 2>/dev/null | sort

# Project guide files
ls AGENTS.md CLAUDE.md 2>/dev/null
```

If `docs/knowledge/` or `.claude/rules/` doesn't exist, report and skip the corresponding checks.

### Phase 2: Cross-Reference Audit

For each knowledge file found in Phase 1:

1. **Grep all rule files** for references to that knowledge file (match `docs/knowledge/<filename>`)
2. Record which rule(s) reference it and at which line
3. Mark files as:
   - **Covered**: referenced from at least one rule
   - **Orphaned**: not referenced from any rule (action needed)
   - **Deprecated**: contains `[DEPRECATED]` marker (info only, no action needed)

For each reference found in rule files:

1. **Verify target exists**: check the referenced knowledge file actually exists on disk
2. Mark references as:
   - **Valid**: target file exists
   - **Stale**: target file doesn't exist (action needed)

### Phase 3: Project Guide Compatibility

Check that project guide files work for both Claude Code and Codex:

1. **Entrypoint presence**:
   - `CLAUDE.md` present → Claude Code can load the project guide
   - `AGENTS.md` present → Codex can load the project guide
   - Best case: `AGENTS.md` is a symlink to `CLAUDE.md`
2. **Entrypoint drift**:
   - If `AGENTS.md` is a regular file, compare whether it contains the same `.claude/rules/` references as `CLAUDE.md`
   - Flag missing or stale references in either guide
3. **Rule import/reference validity**:
   - Grep guide files for `@.claude/rules/<file>.md` and `.claude/rules/<file>.md`
   - Verify each referenced rule exists
4. **Index leakage**:
   - Count direct knowledge references in the canonical guide (`CLAUDE.md`, or `AGENTS.md` if no CLAUDE.md) using `docs/knowledge/`
   - Flag if the guide contains more than **3 direct knowledge file references** (suggests index leakage — the detailed index belongs in rules, not the guide)
5. **Architecture description**:
   - Look for keywords indicating the architecture is described (e.g., "渐进式披露", "progressive disclosure", "rules", "详见", "AGENTS.md")

Exception: a summary table mapping rule files to knowledge domains is acceptable (it's architecture description, not a detailed index).

### Phase 4: Report

Output a structured report:

```
==========================================
  CONTEXT AUDIT REPORT
  <project-name> | YYYY-MM-DD
==========================================

## Coverage Summary

Knowledge files: N total (M covered, X orphaned, Y deprecated)
Rule files: N total
Stale references: N

## Orphaned Knowledge Files (not indexed from any rule)

| File | Suggested Rule | Reason |
|------|---------------|--------|
| docs/knowledge/foo.md | rl-training.md | topic overlaps with RL training |

## Stale References (pointing to non-existent files)

| Rule File | Line | Reference | Status |
|-----------|------|-----------|--------|
| .claude/rules/bar.md | 42 | docs/knowledge/removed.md | file not found |

## Project Guide Compatibility

- AGENTS.md: [PRESENT symlink -> CLAUDE.md / PRESENT regular file / MISSING]
- CLAUDE.md: [PRESENT / MISSING]
- Guide drift: [PASS / WARN — AGENTS.md missing refs found in CLAUDE.md]
- Rule references: [PASS / WARN — stale rule reference detected]
- Architecture description: [FOUND / MISSING]
- Direct knowledge refs: N (threshold: <=3)
- Status: [PASS / WARN — index leakage detected]

## Coverage Map

| Rule File | Knowledge Files Referenced |
|-----------|--------------------------|
| rl-training.md | reward, config, verl-integration, ... |
| cluster-ops.md | container-unify, mutagen-sync, ... |

## Deprecated Files

| File | Deprecation Notice |
|------|--------------------|
| docs/knowledge/experiments.md | migrated to experiment-registry |

==========================================
```

### Phase 5: Fix Suggestions (optional)

If orphaned files are found, suggest concrete edits:

- Identify the most relevant rule file based on topic overlap
- Suggest the specific section where a `> 详见` reference should be added
- Provide the exact line to add (copy-pasteable)

**Do NOT auto-apply fixes.** Present suggestions and let the user decide.

## Constraints

- **Read-only** — never modify files. This is an audit tool, not an auto-fixer.
- **Project-agnostic** — works with any project that has `AGENTS.md` and/or `CLAUDE.md`, `docs/knowledge/`, and `.claude/rules/`. Does not assume specific file names.
- **Follow the user's language** — respond in whichever language the user uses.
- **Deprecated files are not failures** — files with `[DEPRECATED]` markers are expected to exist without rule references. Report them for visibility but don't flag as errors.
- **Threshold, not perfection** — the guide compliance check uses a threshold (<=3 direct refs). A summary table mapping rules to knowledge domains is architecture description, not index leakage.
