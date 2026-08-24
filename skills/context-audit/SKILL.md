---
name: context-audit
description: "Audit project context management (AGENTS.md/CLAUDE.md, rules, knowledge) for Claude Code and Codex compatibility and progressive-disclosure hygiene. Checks direct and indexed knowledge reachability, stale or conflicting references, guide parity, index leakage, and bloated rules that should move to on-demand knowledge. Triggers: 'audit context', 'check context', 'context hygiene', 'context audit', '检查 context', '审计上下文', 'knowledge 覆盖检查', '规则瘦身', '清理过时上下文', 'Codex 上下文检查'. NOT for: code review, documentation updates caused only by one recent code change (use sync-docs), or judging the scientific correctness of knowledge content."
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
- After a sizable change — verify that new facts reached every guide, rule, knowledge, README, or config example that depends on them
- When always-loaded rules have grown into tutorials, changelogs, or long reference indexes

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

1. **Grep rule files first** for the full path or unambiguous filename.
2. If not found, inspect knowledge index files such as `*-index.md`. A leaf is indirectly covered only when its index is itself reachable from a rule.
3. Record the complete route from rule to index to leaf.
4. Mark files as:
   - **Directly covered**: referenced from a rule
   - **Indirectly covered**: referenced from a rule-linked knowledge index
   - **Orphaned**: not reachable from any rule, even transitively
   - **Deprecated**: contains `[DEPRECATED]` and identifies a replacement or retirement reason

For each path reference found in rules, guides, or knowledge indexes:

1. Verify the target exists.
2. Ignore obvious placeholder examples such as `foo.md`, `xxx.md`, `<filename>.md`, or paths inside syntax-template examples.
3. Mark real references as:
   - **Valid**: target exists
   - **Stale**: target does not exist
   - **Conflict candidate**: old and replacement names, commands, or architecture descriptions coexist

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

Knowledge files: N total
  - M directly covered
  - K indirectly covered
  - X orphaned
  - Y deprecated
Rule files: N total
Stale references: N
Conflict candidates: N

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

| Rule File | Direct Knowledge | Indexed Knowledge |
|-----------|------------------|-------------------|
| rl-training.md | reward.md | rl-index.md → config.md, verl.md |

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

### Phase 6: Rule Slimming

Run this phase when always-loaded rules are bloated. Classify content by why an agent needs it:

1. **Whole-file migration**: move a pure tutorial, command cookbook, reference manual, or dated history from `.claude/rules/` to `docs/knowledge/`. Keep only a short pointer in an appropriate rule or guide.
2. **In-file split**: for mixed rules, keep stable imperatives and project invariants in the rule; move procedures, diagnostic stories, measured values, run tags, and reference tables into a sibling knowledge file.
3. **Index extraction**: move a long flat list of knowledge files into a dedicated `*-index.md`; the rule keeps one pointer to that index.

Use these routing rules:

| Content | Destination |
|---------|-------------|
| Stable hard constraint whose violation causes incorrect or unsafe work | `.claude/rules/` |
| Current project identity or always-needed command | canonical project guide |
| How-to, troubleshooting, dated evidence, measured values, run history | `docs/knowledge/` |
| Long list of knowledge files | `docs/knowledge/*-index.md` |
| Superseded material retained for history | `[DEPRECATED]` knowledge file with replacement |

Do not recommend deletion merely because a file is old. Recommend delete or archive only when it is unreachable, superseded, and no longer useful as provenance. Rank cleanup candidates as:

1. Conflicting old/new instructions
2. Stale references
3. Duplicated always-loaded instructions
4. Tutorial or changelog content inside rules
5. Deprecated or orphaned knowledge

For every candidate, report the exact source path, destination or replacement, reason, and expected always-loaded line reduction.

### Phase 7: Change Impact Matrix (optional forward audit)

Phases 1–6 inspect the current context system. Use this phase when the user provides a change summary or the audit follows a sizable implementation, refactor, migration, or bug fix.

Collect new facts from, in order:

1. User-supplied change summary
2. Relevant `git log` and `git diff`
3. Conversation context, confirmed against files before reporting

A new fact is anything that would mislead the next agent if documentation remained stale: dependency swaps, renamed flags, new environment variables, deprecated modules, new invariants, or directory changes.

Map each fact to expected locations:

| Fact type | Expected locations |
|-----------|--------------------|
| Runtime, framework, or storage change | guide tech section, relevant rule, setup docs |
| New environment variable or config key | runbook, `.env.example`, guide if always needed |
| New hard constraint | rule |
| New procedure or diagnostic recipe | knowledge plus reachable reference |
| Deprecated feature or file | deprecation marker, replacement note, old rule reference removed |
| Renamed command, module, or path | every guide, rule, knowledge, and README occurrence |

For each expected location, report:

- **Updated**: contains the new state
- **Missing**: still lacks the new fact
- **Conflict**: old and new states coexist; prioritize this above a simple miss

Include cross-project impact only when a concrete dependent project is discoverable. This phase remains read-only.

## Constraints

- **Read-only** — never modify files. This is an audit tool, not an auto-fixer.
- **Project-agnostic** — works with any project that has `AGENTS.md` and/or `CLAUDE.md`, `docs/knowledge/`, and `.claude/rules/`. Apart from recognized `*-index.md` files, do not assume project-specific names.
- **Follow the user's language** — respond in whichever language the user uses.
- **Deprecated files are not failures** — files with `[DEPRECATED]` markers and a clear replacement or retirement reason may remain unreferenced. Report them for visibility.
- **Threshold, not perfection** — the guide compliance check uses a threshold (<=3 direct refs). A summary table mapping rules to knowledge domains is architecture description, not index leakage.
- **Cross-agent redundancy can be valid** — if Codex cannot automatically load a Claude-specific rule, a compact route in `AGENTS.md` or the shared canonical guide is compatibility metadata, not necessarily duplication.
