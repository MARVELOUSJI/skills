# Project Guide Section-by-Section Fill Guide

In Phase 2, process each `<!-- init-project: 待填充 -->` placeholder in `CLAUDE.md`. The generated `AGENTS.md -> CLAUDE.md` symlink lets Codex read the same project guide. Per-section flow:

```
Read codebase (auto) → Generate draft (auto) → confirm with the available user-input mechanism → update CLAUDE.md
```

User can reply "skip" to skip any section and keep the placeholder.

---

## Section: Project Overview

### Auto-exploration

```
Read: README.md, pyproject.toml, package.json, Cargo.toml, go.mod
Extract: project name, description, main dependencies
```

### User Confirmation

```
Here's a draft project overview:

---
{draft content}
---

Does this look accurate? Press Enter to confirm, type edits, or reply "skip" to skip.
```

### Draft Template

```markdown
**{project_name}** is a {type} that {one-line goal}.

Core approach: {technical method}.

## Workflow

1. {step 1}
2. {step 2}
3. ...
```

---

## Section: Models / Key Dependencies

### Auto-exploration

```
Scan: imports for model libraries (transformers, openai, anthropic, google.generativeai)
Detect: API key references in .env, config files
Read: model config files (yaml, json)
```

### User Confirmation

```
Here's a draft of key models/dependencies:

---
{draft: detected models, APIs, and external services}
---

Anything to add or change? Press Enter to confirm / type edits / "skip" to skip.
```

### Draft Template

```markdown
- **Model A** (size) — primary use case
- **External API** — what it's used for
```

---

## Section: Directory Structure

### Auto-exploration

```
Run ls to see top-level directories
Read each subdirectory's README.md or __init__.py docstring
Identify: core modules, third-party deps, scripts, tests, docs
```

### User Confirmation

```
Here's a draft directory structure:

---
{draft: modules listed by directory and function}
---

Anything missing or to adjust? Press Enter to confirm / type edits / "skip" to skip.
```

### Draft Template

Organize by category:

```markdown
### Core Modules

#### `module_a/` — Description
- Submodule details
- See: `module_a/README.md`

### Third-Party Dependencies

#### `third_party/xxx`
- Purpose

### Other Directories

#### `scripts/` — Run scripts
#### `tests/` — Unit tests
#### `docs/` — Documentation
```

---

## Section: Dev Workflow

### Auto-exploration

```
Detect: .github/workflows/, Makefile, Justfile, scripts/, Dockerfile
Detect: CI/CD presence, pre-commit hooks
```

### User Confirmation

```
Detected the following dev tools: {tool list}

The project guide already includes the default brainstorming→plans→dev→verify flow.
Does your project have additional workflow stages? (e.g., deployment, release, data processing)

Press Enter to skip / type additions.
```

---

## Section: Dev Guide

### Auto-exploration

```
Detect: venv/conda environment, .env files, Dockerfile, Makefile
Detect: test framework (pytest/jest/go test), lint tools (ruff/eslint)
Read: pyproject.toml or package.json scripts section
```

### User Confirmation

```
Here's a draft dev guide:

---
### Environment Setup

{detected setup steps}

### Unit Tests

{detected test commands}

### {other detected dev tools}
---

Anything to add or change?
```

---

## Section: Always Do (Project-Specific Items)

### Auto-exploration

```
Read: existing rule files under .claude/rules/
Detect: lint config (pyproject.toml [tool.ruff], .eslintrc)
Scan: multi-module configs that need consistency
```

### User Confirmation

```
The project guide already includes 3 generic Always Do rules:
- Read related files before modifying code
- Run related unit tests after modifications
- Follow the same module's code style

What **cross-module consistency requirements** does your project have? For example:
- Certain parameters must stay in sync across modules
- API calls must include retry logic
- Specific framework conventions must be followed

Press Enter to skip / type additional items.
```

---

## Section: Ask First

### Auto-exploration

```
Scan: core interface definitions (abstract classes, protocols, signatures)
Scan: config files (yaml, toml, json)
Scan: third_party/ dependencies
```

### User Confirmation

```
Already includes 1 generic Ask First rule:
- Adding new Python dependencies

Which **files or directories require confirmation before modifying** in your project? For example:
- Core config files
- Public interfaces/protocol definitions
- Database schemas
- CI/CD configuration

Press Enter to skip / type additional items.
```

---

## Section: Never Do

### Auto-exploration

```
Detect: third_party/ directory
Detect: .env, credentials, and other sensitive files
Scan: immutable interface contracts
```

### User Confirmation

```
Already includes 2 generic Never Do rules:
- Hardcode API keys, paths, or endpoints
- Directly modify code under third_party/

What **absolute don't-touch conventions** does your project have? For example:
- Immutable function signatures
- External config that must not be guessed
- Legacy code that must not be touched

Press Enter to skip / type additional items.
```

---

## Section: Context Loading (Routing Table)

### Auto-exploration

```
List: all .md files in .claude/rules/
For each rule, scan the opening summary and scope
Map: each rule → 1–3 task-domain keywords
```

### User Confirmation

```
CLAUDE.md has a compact Context Loading routing table. Here is a draft mapping
from task domains to `.claude/rules/*.md` files:

| Task domain | Read first |
|---|---|
{auto-generated rows: domain → rule path}

Claude Code and Codex must not assume `.claude/rules/` is already expanded into
their context. Confirm or edit the domain labels, or reply "skip" to keep the
table empty.
```

### Draft Template

```markdown
| Task domain | Read first |
|---|---|
| Training / reward / config | `.claude/rules/training.md` |
| Evaluation / benchmark protocol | `.claude/rules/testing.md` |
| Cluster operations / remote execution | `.claude/rules/cluster-ops.md` |
| Paper figures / writing | `.claude/rules/paper-figures.md` |
```

Keep this table compact and list rule files only. Detailed procedures and
knowledge-file indexes remain in rules or `docs/knowledge/` and are loaded
on demand.

---

## Section: Progressive Disclosure Setup

### Auto-exploration

```
List: all .md files in docs/knowledge/
List: all .md files in .claude/rules/
Map: which knowledge files are already referenced by which rules
```

### Processing

For each knowledge file in `docs/knowledge/`, ensure the corresponding rule file in `.claude/rules/` contains an inline reference:

```markdown
# In .claude/rules/some-domain.md
> Detailed debugging experience: `docs/knowledge/some-domain.md`
```

If a knowledge file has no matching rule, either:
1. Create a minimal rule file that references it, or
2. Add the reference to the closest existing rule

### User Confirmation

```
Found the following knowledge files and their rule references:

| Knowledge File | Referenced By |
|---------------|--------------|
{auto-generated mappings}

Any knowledge files that need a new rule file? Any additional inline references to add to existing rules?
```

---

## After Completion

Once all sections are processed, output a summary:

```
## Project Guide Fill Complete

| Section | Status |
|---------|--------|
| Project overview | ✓ Filled |
| Directory structure | ✓ Filled |
| Dev workflow | ⊘ Skipped |
| ...     | ... |

Next step: review CLAUDE.md content and confirm AGENTS.md still points at it, then git add + commit.
```
