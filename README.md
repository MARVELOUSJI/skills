# MARVELOUSJI/skills

Personal [Claude Code](https://claude.com/claude-code) & [Codex](https://github.com/openai/codex) skills monorepo.

## What is a skill?

A **skill** is a reusable unit of agent capability — a folder containing instructions (`SKILL.md`), plus optional support files (scripts, references, templates). Claude Code / Codex loads the `SKILL.md`, uses its `description` to pattern-match user intent, and invokes the skill when triggers match.

Reference: Anthropic's [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) for canonical skill authoring patterns.

## Repo structure

```
skills/
└── <skill-name>/
    ├── SKILL.md              # required — YAML frontmatter (name, description, user_invocable?) + body
    ├── README.md             # optional — human-oriented overview / install steps
    ├── README.zh-CN.md       # optional — Chinese translation
    ├── scripts/              # optional — helper scripts the skill invokes (bash/python)
    ├── references/           # optional — large reference docs loaded on-demand
    ├── evals/                # optional — trigger_eval.json for testing description precision
    └── <other files>         # skill-specific (templates, code, configs)
```

**Naming**: lowercase kebab-case. No spaces. Keep under 24 chars ideally.

## How skills get activated

This repo is the **source of truth**. Activation = symlink to agent read paths, done by `~/dotfiles/scripts/setup-skills.sh`:

```
~/workspace/skills/skills/<name>/                      ← source (this repo)
        │ setup-skills.sh
        ▼
~/.claude/skills/<name>         ← Claude Code reads here
~/.agents/skills/<name>         ← Codex / other agents read here
```

Both are symlinks to the same source. **One edit, two agents see it.**

### To activate on a fresh machine

```bash
git clone https://github.com/MARVELOUSJI/skills.git ~/workspace/skills
~/dotfiles/scripts/setup-skills.sh
```

(The parent `MARVELOUSJI/dotfiles` `bootstrap.sh` does this automatically.)

## Current skills (12)

**Cherry-picked from [jiahao-shao1/sjh-skills](https://github.com/jiahao-shao1/sjh-skills)** (MIT), adapted for MARVELOUSJI's research workflow in a proxy-constrained network environment + CMUX terminal + Clash Verge proxy (port 7897).

| Skill | Use-case | Notable external deps |
|---|---|---|
| **cmux** | Multi-pane / multi-agent terminal orchestration inside CMUX | `cmux` CLI (bundled with CMUX.app) |
| **codex-review** | Iterative cross-model review: Claude sends plan/diff to OpenAI Codex for critique (max 5 rounds) | `codex` CLI (npm), proxy for OpenAI API |
| **context-audit** | Audit project's 3-layer context architecture (CLAUDE.md / rules / knowledge) for progressive-disclosure health | none (pure Claude logic) |
| **daily-summary** | Aggregate Claude sessions + git commits (optionally Notion) into daily timeline report | none (Notion is optional) |
| **handoff** | Structured conversation handoff summary for next session | none |
| **init-project** | Scaffold new project with Claude Code best-practices (CLAUDE.md, rules/, knowledge/) | none |
| **paper-analyzer** | Deep critical analysis of specific academic papers via NotebookLM | `notebooklm-py` (pipx), `playwright` + chromium |
| **project-review** | Strategic review — 5-dimension snapshot from vision/roadmap/decisions/meetings docs | none |
| **remote-cluster-agent** | Remote GPU cluster operations via persistent SSH + Go daemon (rca CLI) | Go 1.21+, mutagen, rca (built from this skill), SSH cluster access |
| **scholar-agent** | Scholar Inbox daily digest + filtering + deep-read integration with NotebookLM | `notebooklm-py`, `@playwright/cli` (npm), Scholar Inbox session cookie |
| **sync-docs** | Check if docs need updating after recent code changes | none |
| **web-fetcher** | Fetch any URL as clean markdown; routes login-required platforms through OpenCLI, generic through Jina Reader | `@jackwener/opencli` (npm) + Chrome extension, Clash Verge proxy for Jina |

All external deps are installed by `~/dotfiles/scripts/install-skill-deps.sh`. Manual interactive logins (Google/NotebookLM, Scholar Inbox cookie, OpenCLI Chrome extension load, rca cluster config) documented in that script's output.

## Adding a new skill

### 1. Scaffold

```bash
cd ~/workspace/skills/skills
mkdir my-new-skill
cd my-new-skill
```

Write `SKILL.md`:

```markdown
---
name: my-new-skill
description: "<one paragraph — include triggers Claude should match on, what NOT to trigger for, example user utterances>"
user_invocable: true    # optional, if you want `/my-new-skill` slash command
---

# My New Skill

<body — what to do when triggered; steps, options, outputs>
```

**Follow `skill-creator` (already in this monorepo via Claude Code) conventions.** Key points:
- `description` must enumerate **trigger phrases** in both English and Chinese where relevant
- Include **NOT for** clauses to prevent false triggers
- Body is instructions for the agent — not human docs (put human docs in separate `README.md`)
- Keep body under ~500 lines; put overflow in `references/*.md` and reference them on-demand

### 2. Activate

```bash
~/dotfiles/scripts/setup-skills.sh   # auto-picks up new dir, creates symlinks
```

Confirm: `ls -la ~/.claude/skills/my-new-skill` → should be symlink.

### 3. If skill has external deps

Append install commands to `~/dotfiles/scripts/install-skill-deps.sh`. Never rely on undocumented manual setup — the goal is "fresh Mac + `bootstrap.sh` = everything works".

### 4. Test

Open a new Claude Code session in this repo (or any project). Try a trigger phrase from your SKILL.md `description`. If Claude invokes the skill, it works.

If accuracy of trigger matching matters, write `evals/trigger_eval.json` (see author's original sjh-skills for examples).

### 5. Commit

```bash
cd ~/workspace/skills
git add -A
git commit -m "feat: add my-new-skill"
git push
```

## Modifying an existing skill

**Edit the file in this repo**, not the symlink:

```bash
cd ~/workspace/skills/skills/<name>
$EDITOR SKILL.md
git commit -am "fix: <what you changed>"
git push
```

(Technically editing `~/.claude/skills/<name>/SKILL.md` also works since it's a symlink — but it's clearer to edit at the source location so git context is obvious.)

## Design principles

### Conservative triggers

Skill `description` should err towards **NOT triggering**. A skill that auto-fires on marginal matches pollutes context; a skill that occasionally needs explicit `/invoke` costs a few seconds of user keystrokes. Prefer the latter.

### Proxy-aware by default

Proxy-constrained network / Clash Verge context (port 7897): any skill that hits foreign services (Google, OpenAI, Jina Reader) should either (a) work through pre-set `http_proxy` env vars, or (b) detect unreachable service and fail gracefully with "check your proxy" message. Hardcoding `http://127.0.0.1:7890` (wrong port) or anywhere is forbidden — refer to existing skills' patterns.

### No hardcoded user paths

No `/Users/<name>/` or `/Users/<name>/` in any skill file. Use `$HOME` / `~` when generating paths at runtime. See cmux skill (fixed during cherry-pick from sjh-skills — all 7890 → 7897 proxy fixes are in commit history).

### No secrets in repo

API keys, session cookies, credentials → outside the repo (`~/.env` in dotfiles, `~/.scholar-inbox/` etc). Skills read them from env/files at runtime.

### Upstream attribution

Skills cherry-picked from sjh-skills preserve upstream README / LICENSE references. When fixing upstream bugs (e.g., `@anthropic-ai/playwright-cli` → `@playwright/cli` in scholar-agent), commit with clear "fix:" message referencing upstream.

## Behavior boundaries for future agents editing this repo

### Always

- Write `SKILL.md` frontmatter with precise `description` (triggers + NOT for clauses)
- Test new skill manually before committing (activate via setup-skills.sh, try trigger)
- Co-evolve dotfiles' `install-skill-deps.sh` when adding skills with new CLI / package deps

### Ask first

- Removing / renaming a skill (breaks symlinks until re-stow, affects user's active triggers)
- Changing `setup-skills.sh` linking logic (lives in `~/dotfiles/scripts/`, affects all skills)
- Committing large binary files (>1MB) — prefer `references/` markdown over binary assets

### Never

- Hardcode personal paths (`$HOME` / `~` instead)
- Commit API keys / tokens / cookies (use `~/.env` outside repo)
- Assume specific user OS or Python / Node version (scripts should check `command -v`)
- Publish this repo content inappropriately — MARVELOUSJI/skills is **private**; assume content may include proprietary prompts, strategy templates, etc.

## Credits

- Cherry-picks from [jiahao-shao1/sjh-skills](https://github.com/jiahao-shao1/sjh-skills) (MIT) — originally adapted by Jiahao Shao
- Companion repo: [MARVELOUSJI/dotfiles](https://github.com/MARVELOUSJI/dotfiles) — environment + activation scripts
