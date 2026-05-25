---
name: dotfile-sync
description: Synchronize the user's portable Claude Code, Codex, zsh, dotfiles, and personal skills configuration into the MARVELOUSJI/dotfiles and MARVELOUSJI/skills GitHub repositories. Use only when the user explicitly invokes "dotfile-sync", "同步配置", "同步 dotfiles", "同步本机 Claude/Codex/zsh/skills 配置", "检查本机配置和远端仓库是否需要更新", or asks to sync local config changes for migration to a new Mac. Always audit first, separate portable repo state from machine-local runtime state, ask before modifying config templates from live runtime config, and ask before pushing. NOT for project documentation sync, code repo cleanup, Mac app uninstall, broad system cleanup, or blindly committing all dirty files.
user_invocable: true
---

# Dotfile Sync

Use this skill to help the user keep portable configuration in sync across two personal source-of-truth repositories:

| Repo | Local default | Purpose |
|---|---|---|
| `MARVELOUSJI/dotfiles` | `~/workspace/dotfiles` | Claude Code, Codex, zsh, tmux, starship, yazi, Ghostty/CMUX config, bootstrap scripts, shared agent docs |
| `MARVELOUSJI/skills` | `~/workspace/skills` | Personal skill source directories under `skills/<name>/` |

The goal is migration safety: after moving to a new Mac, the user should be able to clone these repos and restore the portable setup without accidentally publishing local runtime state, secrets, caches, or WIP changes.

## Core Principles

- Start with a read-only audit. Report what changed and what is excluded before editing, staging, committing, or pushing.
- Treat repo sources as authoritative. Edit `~/workspace/dotfiles/...` and `~/workspace/skills/skills/<name>/...`, not symlink copies under `~/.claude`, `~/.codex`, or `~/.agents`.
- Separate portable config from machine-local runtime state. Do not copy live files into the repo just because they differ.
- Ask before changing `codex/.codex/config.toml.example` from live `~/.codex/config.toml`. Each time, ask whether any detected portable setting should be promoted into the template.
- Never use `git add -A` for this workflow. Stage only approved paths after classifying dirty changes.
- Ask before pushing to remote. If the user only approved local preparation, stop after validation and show the exact pending commit/push plan.

## What Belongs In Scope

Use the current repo structure to decide whether a change belongs in `dotfiles`, `skills`, or neither.

Typical `dotfiles` scope:

- Claude Code global prompt and settings templates: `claude/.claude/CLAUDE.md`, `claude/.claude/settings.json`
- Codex global prompt and safe templates: `codex/.codex/AGENTS.md`, `codex/.codex/config.toml.example`, `codex/.codex/codex-notify.sh`
- Shell and terminal config: `zsh/.zshrc.shared`, `zsh/.terminal-keys.txt`, `tmux/.tmux.conf`, `starship/.config/starship.toml`, `yazi/.config/yazi/keymap.toml`, `ghostty/.config/ghostty/config`
- Shared agent workflow docs under `docs/`
- Bootstrap and install scripts: `install.sh`, `dot-sync.sh`, `scripts/bootstrap.sh`, `scripts/setup-skills.sh`, `scripts/install-skills.sh`, `scripts/install-skill-deps.sh`
- README or project guide updates when the synced structure or setup steps changed

Typical `skills` scope:

- Personal skill directories under `skills/<name>/`
- Skill `SKILL.md`, `README.md`, `references/`, `scripts/`, `assets/`, and `evals/`
- Repository guide changes in `CLAUDE.md` / `AGENTS.md` when skill conventions change

## What Must Stay Out

Never sync these unless the user explicitly asks for a sanitized template and you have removed sensitive/runtime fields:

- Real `~/.codex/config.toml`, `~/.codex/auth.json`, sessions, logs, plugin caches, goals databases, memory files, project trust state, or local approval state
- Real Claude Code auth/session files, local machine state, prompt history, caches, or project trust state
- Secrets, API keys, cookies, SSH keys, tokens, `.env` contents, browser sessions, or private credentials
- `.DS_Store`, temporary files, build outputs, downloaded archives, caches, generated logs, and editor backup files
- Unrelated dirty changes discovered during the audit

If the user asks to "sync everything", still classify findings and exclude runtime/private state by default.

## Codex Config Template Rule

The portable template is `~/workspace/dotfiles/codex/.codex/config.toml.example`. The live runtime config is usually `~/.codex/config.toml`.

When the user asks to sync Codex config:

1. Read both files if available.
2. Summarize meaningful differences without printing secrets.
3. Classify each difference as:
   - **Portable candidate**: stable preference that could help on a new Mac, such as model defaults, service tier preference, safe UI behavior, or feature flags the user wants documented.
   - **Runtime/local**: auth provider details, project trust state, local paths, plugin cache paths, session data, machine-specific approval settings, or anything that could expose private state.
   - **Unclear**: ask the user.
4. Ask explicitly: "要不要把这些 portable settings 写入 `codex/.codex/config.toml.example`？默认不写。"
5. Only edit the template after the user confirms the specific settings to include.

Do not treat live runtime drift as evidence that the template should change.

## Workflow

### Phase 1: Read-Only Audit

Inspect both repos and their remotes before deciding what to touch.

Useful commands:

```bash
git -C ~/workspace/dotfiles status --short --branch
git -C ~/workspace/dotfiles remote -v
git -C ~/workspace/dotfiles diff --stat
git -C ~/workspace/dotfiles diff --name-only

git -C ~/workspace/skills status --short --branch
git -C ~/workspace/skills remote -v
git -C ~/workspace/skills diff --stat
git -C ~/workspace/skills diff --name-only
```

If network access is needed and allowed, fetch before comparing remote state:

```bash
git -C ~/workspace/dotfiles fetch --prune origin
git -C ~/workspace/skills fetch --prune origin
```

Check symlink parity when skills or global prompts are involved:

```bash
readlink ~/.codex/AGENTS.md
readlink ~/.claude/CLAUDE.md
find -L ~/.agents/skills -maxdepth 2 -name SKILL.md -print
find -L ~/.claude/skills -maxdepth 2 -name SKILL.md -print
```

### Phase 2: Classify Changes

Produce three buckets:

- **Sync candidates**: portable, intentional changes that belong in `dotfiles` or `skills`.
- **Needs decision**: plausible candidates that may be too broad, sensitive, or runtime-derived.
- **Exclude**: unrelated dirty files, runtime state, caches, secrets, generated files, or ambiguous matches.

For each item, include the repo, path, evidence, and proposed action. If there are dirty files unrelated to the user's request, call them out and leave them alone.

### Phase 3: Update Source Repos

Only after the user has approved the plan, make scoped edits in the source repos.

Examples:

- Add a new skill under `~/workspace/skills/skills/<name>/`
- Update `~/workspace/dotfiles/scripts/install-skill-deps.sh` if a skill introduces external dependencies
- Update `~/workspace/dotfiles/README.md` and `README.zh-CN.md` if setup instructions or synced domains changed
- Update global prompts only when behavior should apply to every Claude Code / Codex session

Do not stage or commit unrelated dirty files.

### Phase 4: Verify

Run the smallest meaningful validation for the touched files.

Common checks:

```bash
git -C ~/workspace/dotfiles diff --check
git -C ~/workspace/skills diff --check
python3 -m json.tool ~/workspace/skills/skills/<name>/evals/evals.json
bash -n ~/workspace/dotfiles/scripts/<script>.sh
~/workspace/dotfiles/scripts/setup-skills.sh
readlink ~/.agents/skills/<name>
readlink ~/.claude/skills/<name>
```

If a command would mutate many symlinks, install tools, or contact the network, explain the effect first and ask if the user has not already approved that class of action.

### Phase 5: Present Sync Plan Before Remote Push

Before committing or pushing, show:

- Files to stage, grouped by repo
- Files explicitly excluded
- Validation already run and results
- Proposed commit message(s)
- Whether each repo is ahead/behind remote
- Exact push target, usually `origin main`

Ask for confirmation before pushing. If the user says "只本地更新", do not push.

### Phase 6: Commit And Push After Confirmation

After the user confirms, commit only approved paths.

Good patterns:

```bash
git -C ~/workspace/skills add skills/<name>/SKILL.md skills/<name>/evals/evals.json
git -C ~/workspace/skills commit -m "feat: add <name> skill"
git -C ~/workspace/skills push origin main

git -C ~/workspace/dotfiles add <approved-paths>
git -C ~/workspace/dotfiles commit -m "chore: sync portable config"
git -C ~/workspace/dotfiles push origin main
```

Avoid `git add -A`. Re-run `git status --short --branch` after push and report whether the local branch matches remote.

## Report Templates

### Read-Only Audit

```markdown
# Dotfile Sync Audit

## Scope
- Requested:
- Repos checked:
- Remote state:

## Sync Candidates
| Repo | Path | Evidence | Proposed action |

## Needs Decision
| Repo/source | Item | Why it needs your decision | Default |

## Excluded
| Repo/source | Path/item | Reason |

## Codex Config Template Question
- Detected portable candidates:
- Runtime/local differences:
- Question: 要不要把哪些 portable settings 写入 `codex/.codex/config.toml.example`？默认不写。

## Next Step
- Waiting for confirmation before edits/stage/commit/push.
```

### Final Result

```markdown
# Dotfile Sync Result

## Changed
| Repo | Path | Summary |

## Validation
| Command | Result |

## Not Touched
| Path/item | Reason |

## Remote
- Dotfiles:
- Skills:

## Remaining Decisions
- ...
```

## Adjacent Skills

- Use `sync-docs` for checking whether project documentation and agent context are stale after code changes.
- Use `context-audit` for project-level `AGENTS.md` / `CLAUDE.md` / `.claude/rules` / `docs/knowledge` hygiene.
- Use `mac-app-uninstaller` for uninstalling or cleaning up macOS apps.

Do not let this skill become a general cleanup or project documentation skill; it is specifically for portable personal configuration sync.
