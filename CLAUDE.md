# MARVELOUSJI/skills — Agent Guide

This file is **auto-loaded** when a Claude Code session opens in this repo, and by Codex through `AGENTS.md -> CLAUDE.md`. Read me before modifying skills or adding new ones.

> Human-oriented overview is in [README.md](README.md). This file is for the agent.

## What this repo is

The **source of truth** for all personal skills. 18 skills currently, including cherry-picks from [jiahao-shao1/sjh-skills](https://github.com/jiahao-shao1/sjh-skills) and locally authored skills, adapted for MARVELOUSJI's workflow (CMUX terminal + proxy-constrained network support through Clash Verge on port 7897).

Companion repo: [MARVELOUSJI/dotfiles](https://github.com/MARVELOUSJI/dotfiles) — environment, tools, activation scripts.

## Architecture

```
~/workspace/skills/skills/<name>/          ← this repo (source of truth)
        │  ~/workspace/dotfiles/scripts/setup-skills.sh creates symlinks:
        ▼
~/.claude/skills/<name>                    ← Claude Code reads here
~/.agents/skills/<name>                    ← Codex / other agents read here
AGENTS.md -> CLAUDE.md                     ← Codex project guide entrypoint for this repo
```

**Edit here, both agents see.** Never edit `~/.claude/skills/<name>/...` as if it were separate — it's a symlink to this repo.

## Skill anatomy

```
skills/<name>/
├── SKILL.md              # required — YAML frontmatter (name, description, user_invocable?) + body
├── README.md             # optional — human overview
├── scripts/              # optional — shell/python helpers
├── references/           # optional — large docs loaded on-demand
└── evals/trigger_eval.json  # optional — test description precision
```

**Naming**: lowercase-kebab-case, ≤ 24 chars.

## SKILL.md frontmatter conventions

```yaml
---
name: <same-as-directory-name>
description: "<include triggers — English + Chinese; 'NOT for' clauses to prevent false triggers; example user utterances>"
user_invocable: true   # optional, enables /<name> slash command
---
```

- `description` is how Claude Code / Codex decide to invoke. Over-specify trigger phrases, under-specify scope.
- Include both English and Chinese trigger patterns when relevant (user operates in Chinese primarily).
- Use `NOT for: ...` clauses to prevent triggering on adjacent intents.

## Workflow: adding a new personal skill

1. **Scaffold**
   ```bash
   cd ~/workspace/skills/skills && mkdir <name> && cd <name>
   # Write SKILL.md + optional README / scripts / references
   ```
2. **Activate**
   ```bash
   ~/workspace/dotfiles/scripts/setup-skills.sh  # auto-picks up new dir, creates symlinks
   ```
3. **External deps** — if the skill needs extra CLIs / Python packages / Go binaries / browser extensions: **append to `~/workspace/dotfiles/scripts/install-skill-deps.sh`**. Never rely on undocumented manual setup. Goal: fresh Mac + `bootstrap.sh` = everything works.
4. **Test** — open a new Claude Code or Codex session (or use `/<name>` if `user_invocable`), try a trigger phrase from `description`.
5. **Commit**
   ```bash
   cd ~/workspace/skills && git add -A && git commit -m "feat: add <name>" && git push
   ```

## Workflow: modifying an existing skill

Edit at this repo's source location:
```bash
cd ~/workspace/skills/skills/<name>
$EDITOR SKILL.md   # or any other file
git commit -am "fix: <what changed>"
git push
```

## Behavior Boundaries

### Always
- Edit at repo source (`~/workspace/skills/skills/<name>/`), never at the `~/.claude/skills/` or `~/.agents/skills/` symlink locations
- Precise `description` in SKILL.md frontmatter (trigger + NOT for)
- Co-evolve `~/workspace/dotfiles/scripts/install-skill-deps.sh` when adding skills with new external deps
- Test trigger before committing — open a new Claude Code or Codex session and try a trigger phrase

### Ask first
- Removing or renaming a skill (breaks existing symlinks, invalidates user's muscle memory on triggers)
- Changing `~/workspace/dotfiles/scripts/setup-skills.sh` linking logic (affects ALL skills here)
- Committing large binaries (>1MB) — prefer `references/*.md` over binary assets
- Bumping or changing external dep versions in `install-skill-deps.sh` (may break other skills sharing the dep)

### Never
- **Hardcode user/machine paths** — no concrete paths such as `/Users/<name>` or `/ssd0/<name>`. Use `$HOME` or `~`. (Context for remote targets: if the skill SSH-executes on cluster, `~` on remote ≠ `~` locally. Be explicit.)
- **Commit secrets** — API keys, tokens, cookies, session states. They live outside this repo (`~/.env` in dotfiles, `~/.scholar-inbox/`, `~/.notebooklm/`, etc.).
- **Hardcode proxy port other than 7897** — user runs Clash Verge on port 7897. Previous upstream bug: author's skills had port 7890 hardcoded in ~10+ places. All fixed during cherry-pick; don't re-introduce.
- **Commit private or proprietary content** — this repository is public-facing. Keep unpublished project details, identity-sensitive information, internal infrastructure, and proprietary prompts out of every tracked file and commit.
- **Assume specific Python / Node version** — scripts should check `command -v` before using tools.
- **Create a new standalone script** when an existing one can be extended — if your new skill's install logic fits `install-skill-deps.sh` scope, append there.

## Proxy awareness (important context)

The user may work in a proxy-constrained network environment. Services like `r.jina.ai`, OpenAI API, and sometimes GitHub raw files may be slow or blocked without Clash Verge proxy (SOCKS5 127.0.0.1:7897).

- User's `cc` / `cct` / `cx` aliases (in `dotfiles/zsh/.zshrc.shared`) inline-export `http_proxy` / `https_proxy` / `all_proxy` before launching agents, so terminal-launched agents inherit proxy env. Codex App may have a different environment; prefer checking env before assuming network access.
- Skills using Python `httpx` / `requests` / `urllib` will inherit those env vars automatically
- Python packages using httpx may need `socksio` extra for SOCKS — example: `pipx inject notebooklm-py socksio` (already baked into `install-skill-deps.sh`)
- `curl` also respects env vars — no extra config
- Don't hardcode proxy URLs in skill code; rely on env

## Testing a skill manually

```bash
# Open a new Claude Code or Codex session, in any project
# Try an English and Chinese trigger from SKILL.md description
# If matched, the agent invokes the skill automatically.
# If not matched, check whether your description phrasing aligns with likely user utterances.

# For scripted skill logic (e.g., skill has scripts/foo.sh):
bash skills/<name>/scripts/foo.sh   # run in this repo
```

## Upstream (sjh-skills) parity

- Still have read-only clone at `~/workspace/sjh-skills/` (author's repo). Future cherry-picks: `cp -r ~/workspace/sjh-skills/skills/<name> ~/workspace/skills/skills/`
- When cherry-picking, scan for non-portable proxy ports and concrete user paths: `grep -rnE "7890|/Users/[^/]+|/ssd[0-9]+/[^/]+" ~/workspace/skills/skills/<name>` — inspect and fix any hits
- Commit message convention for cherry-picks: `feat: cherry-pick <name> from jiahao-shao1/sjh-skills`
- Commit message for upstream bug fixes: `fix(<name>): <what-was-wrong>` (example: `fix(scholar-agent): 修正 playwright-cli npm 包名` for the @anthropic-ai → @playwright/cli rename)

## Currently installed external dep summary

| Skill | External deps |
|---|---|
| paper-analyzer (optional), scholar-agent (shared) | `notebooklm-py` via pipx + Playwright Chromium |
| scholar-agent (additional) | `@playwright/cli` via npm + Scholar Inbox session cookie |
| experiment-registry | `exp-registry` CLI via pipx from the pinned upstream GitHub package |
| web-fetcher | `@jackwener/opencli` via npm + OpenCLI Chrome extension |
| remote-cluster-agent | Go 1.21+, mutagen, compiled `rca` binary at `~/go/bin/rca`, `~/.config/rca/config.toml` with cluster SSH nodes |
| codex-review | `codex` CLI + OpenAI creds |
| cmux | `cmux` CLI (bundled with cmux.app) |
| daily-summary | (optional) Notion integration — currently skipped, auto-degrades gracefully |
| folder-cleanup | Standard filesystem tools; optional Python 3 standard-library inventory helper; no new packages |
| Others (handoff / init-project / context-audit / sync-docs / project-review / dotfile-sync / mac-app-uninstaller) | Pure agent instructions, no external deps |

See `~/workspace/dotfiles/scripts/install-skill-deps.sh` for the canonical install flow.

## References

- Human-oriented overview: [README.md](README.md)
- Companion dotfiles repo: [MARVELOUSJI/dotfiles](https://github.com/MARVELOUSJI/dotfiles) — see its `CLAUDE.md` + `README.md` for environment architecture
- Upstream reference: `~/workspace/sjh-skills/` (read-only clone of jiahao-shao1/sjh-skills)
- Skill authoring best-practices: [anthropics/skills/tree/main/skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator) — already installed as `skill-creator` skill
