---
name: remote-cluster-agent
description: "Remote GPU cluster operations and health inspection via the `rca` CLI — run commands, transfer files, check GPU occupancy. Trigger whenever the task involves remote execution, training, GPU, cluster status, node inspection, or mutagen sync, even if the user doesn't explicitly say 'cluster'. Trigger words — cluster, GPU, rca, training, node, remote execution, sync code, tail log, mutagen, cluster status, which node is free, cluster health, GPU usage, 集群, 节点, 远程执行, 同步代码, 跑训练, 看日志, 集群状态, GPU 占用."
---

# remote-cluster-agent

Local control plane for remote GPU clusters: a Go daemon + `rca` CLI. All commands go through the daemon's Unix socket to a cluster-side Python `agent.py` over persistent SSH, ~0.1s/command latency.

## What to do when triggered

1. **Check if `rca` is installed**: run `which rca`.
   - If `not found` → run the first-time install flow (below), then continue to step 2.
2. **Check daemon status**: run `rca daemon status`.
   - If `daemon request failed` → run `rca daemon start`.
3. **Check node connectivity**: run `rca nodes`.
   - If the target node is dead → `rca connect <node>`. Still dead → re-establish whatever SSH tunneling / VPN / jump host you depend on, then retry.
   - Second round still dead → read `rca daemon logs -f` for error detail.
4. **Project init check** (only when the user's request involves **project-level development** — modifying code, running Python / pytest / training, executing scripts in the cwd. Skip for pure cluster queries like `rca nodes` / `nvidia-smi` / "看下哪个节点空"). See "Project init flow" below for the full procedure.
5. Run the user's command (following the project rule if one exists at `<cwd>/.claude/rules/remote-cluster-agent.md`; read it explicitly before remote development work, especially under Codex where `@...` references are not guaranteed to be expanded automatically).

**Don't write raw `ssh` commands**, always use `rca exec` / `rca batch`.

### Project init flow

**Source of truth**: per-project values (node, dir, conda env, conda init script, mutagen session) live in `~/.config/rca/config.toml` under `[projects.<key>]` and `[nodes.<name>]`. The project rule file at `<cwd>/.claude/rules/remote-cluster-agent.md` is thin — it only encodes the **behavioral rules** and points at the config for actual values.

When the user's request involves project-level development in the current working directory:

1. Check `<cwd>/.claude/rules/remote-cluster-agent.md` with the available file-reading tool.
2. **If it exists** → read the project key from it, then `Read ~/.config/rca/config.toml` to resolve concrete values, and continue with the user's request following the three rules.
3. **If it does not exist** → **pause the user's original request** and tell them: "这个项目还没初始化 remote-cluster-agent 配置，先回答几个问题再继续。" Then:

   **(a) Read existing config.** Open `~/.config/rca/config.toml` to list configured nodes (so you can offer them as options) and to know the chosen node's `dir` / `conda_sh` defaults.

   **(b) Ask the user** (one batch of 5 questions; in Codex ask directly or use `request_user_input` if available, in Claude Code use `AskUserQuestion`):
   1. **Which node?** — options are the keys under `[nodes.*]` from config.toml.
   2. **Remote project directory** (absolute path) — default suggestion: `<chosen-node.dir>/<cwd-basename>` if node has `dir`, else `~/<cwd-basename>`.
   3. **Conda env name on remote** (e.g. `myproject`).
   4. **Mutagen sync session name** — default suggestion: cwd basename. Tell the user `mutagen sync list` shows existing sessions if they're unsure.
   5. **Project-specific ignore paths/globs** — directories or globs that should NOT be synced and that mutagen should leave alone on both sides (typically: training outputs, logs, large datasets, anything written on remote that you want to preserve there). Default `[]`. Common boilerplate (`__pycache__`, `*.pyc`, `.venv`, `*.pt`, `*.pth`, `*.bin`, `*.safetensors`, `*.ckpt`, `.DS_Store`, `*.egg-info`, `node_modules`) is already baked into `mutagen-setup.sh` — don't ask the user to repeat those. Examples to suggest: `outputs/`, `wandb/`, `checkpoints/`, `*.npz`.

   Only ask about `conda_sh` (init script path on the remote) if the chosen node doesn't already have one set in config.toml — then default `~/miniconda3/etc/profile.d/conda.sh` covers most setups; ask the user to confirm or override.

   **(c) Update `~/.config/rca/config.toml`** (use the available file-editing mechanism to surgically modify it; don't rewrite the whole file):
   - Append a new `[projects.<cwd-basename>]` block with `default_node`, `dir`, `conda_env`, `mutagen_session`, `ignores` filled from the answers (write `ignores = []` if the user had nothing).
   - If the chosen node's `conda_sh` is empty in config.toml, fill it in `[nodes.<chosen-node>]` (so it doubles as the default for any future projects on the same node).
   - Verify by reading the file again and confirming the new entries are correctly placed (no stray syntax).

   **(d) Write the thin project rule file:**
   - `Read` `<skill_dir>/templates/project-rule.md.tmpl`.
   - Substitute the **only** placeholder `{{PROJECT_KEY}}` with the cwd basename. (Do **not** embed concrete node/dir/env/session values into this file — those live in config.toml.)
   - Write to `<cwd>/.claude/rules/remote-cluster-agent.md` (create `.claude/rules/` if needed).

   **(e) Update project guide entrypoints for both Claude Code and Codex:**
   - If it doesn't exist → create it with the single line `@.claude/rules/remote-cluster-agent.md`.
   - If it exists and doesn't contain that line → append it (with a leading blank line if the file doesn't end with one).
   - If it already contains that line → leave it untouched (idempotent).
   - Ensure `<cwd>/AGENTS.md` exists for Codex:
     - If missing and `CLAUDE.md` exists → create a relative symlink: `ln -s CLAUDE.md AGENTS.md`.
     - If it is already a symlink to `CLAUDE.md` → leave it untouched.
     - If it is a regular file and doesn't contain `@.claude/rules/remote-cluster-agent.md` → append the same line there too.
     - If it is a symlink to another target → read the target and only update it if it is clearly the project guide; otherwise report the mismatch and ask before editing.
   - Do not overwrite an existing `AGENTS.md`; Codex depends on it as the project entrypoint.

   **(f) Create the mutagen session** if one doesn't already exist for this `mutagen_session` name (`mutagen sync list` to check). If missing, run:

   ```bash
   bash <skill_dir>/mutagen-setup.sh <node-ssh-host> <local_dir> <remote_dir> <session_name> <ignore-1> <ignore-2> ...
   ```

   The 5th+ positional args are the project's `ignores` from config.toml. The script merges them with the hardcoded boilerplate ignore list (`__pycache__`, `*.pyc`, `.venv`, `*.pt`, etc.) and creates the session in `one-way-replica` mode. **Skip this step if the user explicitly says they've already set up mutagen.**

   **(g) Confirm and continue.** One-sentence summary to the user listing the 5 values you wrote (e.g. "已在 config.toml 加 `[projects.my-proj]`：node=train, dir=/home/user/my-proj, conda_env=my-env, mutagen_session=my-proj, ignores=[outputs/, wandb/]"). Then resume the original request, applying the rules using values you just wrote.

**Fields and where they resolve from** (resolution order: project → node → global):

| Field | Where to read |
|-------|---------------|
| `default_node` | `[projects.<key>].default_node` |
| `dir` (remote project dir) | `[projects.<key>].dir` → `[nodes.<node>].dir` → `default_dir` |
| `conda_env` | `[projects.<key>].conda_env` → `[nodes.<node>].conda_env` |
| `conda_sh` | `[nodes.<node>].conda_sh` (no project-level override) |
| `mutagen_session` | `[projects.<key>].mutagen_session` |
| `ignores` | `[projects.<key>].ignores` (project-level only; merged with boilerplate hardcoded in `mutagen-setup.sh`) |

If a field is empty across all levels, ask the user before guessing.

### First-time install (auto, no user action needed beyond SSH info)

When `which rca` returns not found, execute in order:

```bash
cd <skill_dir>
make install              # builds rca into ~/go/bin (requires Go 1.21+)
rca config init           # migrates legacy ~/.config/remote-cluster-agent/*.md, or generates blank template
```

Then **ask the user** for each node's SSH command, and write them into `~/.config/rca/config.toml` under `[nodes.*]`. Example:

```toml
[nodes.train]
ssh = "ssh gpu-train"

[nodes.eval]
ssh = "ssh -p 2222 gpu-eval"
dir = "/home/user/project"
agent_path = "/shared/.agent/agent.py"
```

Optional per-node overrides: `dir` (default working directory) and `agent_path` (where `agent.py` lives on that node). Both fall back to globals if unset.

Finally start and verify:

```bash
rca daemon start
rca daemon status         # confirm running
rca nodes                 # confirm nodes connected
rca agent check           # if agent missing → rca agent deploy
```

> **Project-level rule** (per project, not global): the first time the user uses this skill in a new project directory for actual development, follow the **Project init flow** above to drop a rule file into `<cwd>/.claude/rules/remote-cluster-agent.md`. That file records the project's node, conda env, mutagen session, and remote dir. Future Claude Code sessions see it through `CLAUDE.md`; future Codex sessions see it through `AGENTS.md` (usually a symlink to `CLAUDE.md`). Don't run this for every cwd — only when you're about to run / test / develop project code remotely.

## Common operations

### Single-node exec / heredoc

```bash
rca exec -n train "nvidia-smi"
rca exec -n train -d /home/user/project "git pull"
rca exec -t 600 -n train "python train.py"

# heredoc (bypasses shell escaping, recommended for multi-line or special chars)
rca exec --stdin -n train <<'EOF'
cd /home/user/project
python -c "import json; print(json.dumps({'k':'v \"q\"'}))"
EOF
```

### Multi-node parallel (batch)

```bash
rca batch "nvidia-smi | head -20"
rca batch -n train,eval "df -h /home"
rca batch --json "hostname" | jq -r '.results[] | "\(.node): \(.output)"'
```

### Node status / connection management

```bash
rca nodes                   # current connection state
rca nodes --check           # deep ping (with latency)
rca nodes --health          # latency history (monitor-tracked)
rca connect train           # manually reconnect a dead node
rca disconnect train        # actively close a node's connection
```

### File transfer (cp)

`rca cp` moves files through the agent's JSON-Lines channel (base64-encoded, 50 MB/file limit). Works on any SSH setup — no separate SCP/rsync path needed.

```bash
rca cp train:/home/user/logs/train.log ./
rca cp ./config.yaml train:/home/user/project/config.yaml
rca cp -r train:/home/user/checkpoints/exp07 ./local-copy/
```

For very large files (multi-GB checkpoints), use shared filesystem or object storage — `rca cp` peaks around 2–3 MB/s.

### Streaming / long tasks

```bash
rca exec -s -n train "tail -f /var/log/train.log"
rca exec -s -n train "python train.py"
```

### Mutagen sync flush

`mutagen sync flush` blocks until the local mutagen daemon has propagated all pending changes for that session — use it to close the race between local edits and remote execution (and the reverse).

```bash
mutagen sync flush <session-name>     # flush one session, block until done
mutagen sync flush --all              # flush every session
```

Cost: ~50-100ms when nothing is pending; ~200-500ms after a small file change. Don't flush before pure query commands (`nvidia-smi`, `ps`, `df`, `rca nodes`) — there's no race to close.

If `flush` errors with "session is paused" / "halted" / "in conflict", the underlying sync is broken — fix the session (`mutagen sync resume <name>`, or see `reference/mutagen-troubleshooting.md`) before retrying.

### Cluster health inspection

Triggered when the user says "cluster status", "which node is free", "cluster health", "GPU usage". Use `rca batch` for parallel sampling:

```bash
rca nodes --check
rca batch "nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv"
rca batch "df -h /home | tail -1"
rca batch "uptime && tmux ls 2>/dev/null | wc -l"
```

Summarize into a table and recommend the most idle node. See `reference/cluster-health.md` for detailed probe commands, parse rules, and report format.

## Sync direction (one-way-replica)

Mutagen sync is configured **one-way-replica**: local (alpha) → remote (beta) only. Beta is treated as a strict mirror of alpha. This produces three asymmetries the agent must internalize:

1. **Remote → local does not happen.** A file written / edited / deleted on the cluster does **not** propagate back to local. There is no automatic mechanism that pulls remote changes home.
2. **Remote-only files in non-ignored paths are deleted.** When mutagen reconciles, anything on beta that isn't on alpha (and isn't covered by the ignore list) is treated as "stale" and removed. So if a training script writes `outputs/result.json` on remote and `outputs/` is not in the project's `ignores`, that file disappears on the next sync — silently.
3. **Remote-side edits are reverted.** Editing a file on the cluster will be overwritten by mutagen with the local version on the next reconcile. Always `Edit` / `Write` / delete on local; let mutagen mirror.

**To preserve remote-generated files** (training outputs, checkpoints, wandb logs), put their path/glob in `[projects.<key>].ignores`. Mutagen then leaves both sides untouched and the file persists on remote.

**To read remote files locally**:
- File is written by local first and mirrored to remote (code, configs) → `Read` it locally, no roundtrip.
- File is generated on remote and lives in an ignored path → `rca cp <node>:<remote-path> <local-path>` to fetch, or `rca exec -n <node> "cat ..."` for a quick peek.
- File is generated on remote and lives in a non-ignored path → it doesn't exist anymore (mutagen ate it). Move the path into `ignores` or have the script write somewhere ignored.

If unsure whether a path is ignored, check the live ignore list: `mutagen sync list <session> --long`.

## Reading files vs running commands

`rca exec` is for **executing commands** (starting training, killing processes, checking process state, installing deps) — not reading file contents.

**Decision rule**:
- Want to **read a file the local writes** (code, configs, anything checked in) → `Read("path/...")` locally. Same content on both sides because local is the source of truth.
- Want to **read a file the remote writes** (training outputs, logs in ignored paths) → `rca cp <node>:<remote-path> <local-path>` to fetch first, then `Read`. Or `rca exec -n <node> "cat ..."` for a quick view without persisting locally.
- Want to **run an operation** (ps, nvidia-smi, start/stop training, pip install) → `rca exec`.
- **Just edited a file locally and about to `rca exec` something that reads it** → `mutagen sync flush <session>` first (see "Sync timing" below) to close the local→remote race.

## Sync timing (avoid stale exec)

Mutagen syncs in near-real-time but is **not synchronous**. There's a small window (sub-second to a few seconds) between a local edit and that change being visible on the cluster.

- **Local edit → remote exec**: you `Edit` a `.py`, then immediately `rca exec` the same script. If mutagen hasn't propagated yet, the cluster runs the **old** version.

**Fix**: `mutagen sync flush <session>` blocks until the local→remote propagation finishes, then returns. Use it before any `rca exec` that depends on a file you just edited.

Note: there is **no** "remote → local" race to worry about — under one-way-replica, mutagen never propagates remote changes back, so flush has nothing to do in that direction. To pull remote outputs locally, use `rca cp` (see Sync direction above).

Once a project is initialized via the project init flow, the project rule file at `<cwd>/.claude/rules/remote-cluster-agent.md` records the session name and reminds future agents of this rule through `CLAUDE.md` / `AGENTS.md`. Without an initialized project, follow the same rule manually using whatever session name `mutagen sync list` shows.

**Exempt** (no flush needed): pure queries that don't touch files you just changed — `nvidia-smi`, `ps`, `df`, `uptime`, `tmux ls`, `conda env list`, `rca nodes`.

## SSH connection failures

When `rca nodes --check` shows dead, or `rca exec` reports connect failed:

1. Try `rca connect <node>` once — most transient issues resolve here.
2. Still dead? The SSH transport underneath is broken. `rca` itself doesn't manage tunnels / VPN / jump hosts — re-establish those through your usual workflow (ssh config, tunnel script, corporate VPN, etc.), then retry step 1.
3. Inspect daemon errors with `rca daemon logs -f`.

Report failures grouped by cause — don't just say "all nodes failed". Which nodes recovered? Which need tunnel re-establishment? Which look like SSH config issues?

## Mutagen session health

When the user mentions "skill updated" or "redeploy", check mutagen session config:

```bash
mutagen sync list 2>/dev/null
```

For each session:
1. **Sync mode**: should be `one-way-replica`. If `one-way-safe` or `two-way-resolved`, prompt to rebuild.
2. **Ignore list (boilerplate)**: `.git` should NOT be ignored (v0.4.0+ syncs `.git` to keep cluster-side `git status` clean).
3. **Ignore list (project-specific)**: every entry in `[projects.<key>].ignores` from config.toml must be present in the live session's ignore list. Mismatch → rebuild so remote-generated outputs in those paths don't get deleted.

Rebuild (only after user confirms) — pass project ignores as positional args 5+:
```bash
mutagen sync list <name> --long    # record current params first
mutagen sync terminate <name>
bash <skill_dir>/mutagen-setup.sh <ssh_host> <local_dir> <remote_dir> <session_name> <ignore-1> <ignore-2> ...
```

### Container restart: mutagen fails to reconnect

**Symptom**: `mutagen sync list` shows Beta `Connected: No`; `mutagen sync resume` reports `server magic number incorrect`.

**Root cause**: the cluster container restarted and lost `~/.mutagen/` (container home is ephemeral). Mutagen's agent binary and staging data live in a persistent path (typically mounted storage like `/shared/.mutagen/`).

**Fix**:
```bash
# Recreate the symlink on the cluster node
rca exec -n <node> "ln -sf /shared/.mutagen ~/.mutagen"

# Then resume locally
mutagen sync pause <session-name>
mutagen sync resume <session-name>
```

**Prevention**: have the container init script create this symlink on startup.

See `reference/mutagen-troubleshooting.md` for more failure modes.

## Config

Main config: `~/.config/rca/config.toml` (edit via `rca config edit`).

First-time install flow is in "What to do when triggered → First-time install". Day-to-day, just keep the daemon running (`rca daemon status`).

### Agent deployment / updates

```bash
rca agent check               # show agent version per node
rca agent deploy              # copy local agent.py (only where missing)
rca agent deploy --force      # force overwrite
```

> **Note**: `rca agent deploy` uses direct SSH (bypasses the daemon) and iterates all nodes in `config.toml` serially. Disconnected nodes will block for SSH's default connect timeout (minutes). Workaround — use a temp config with only live nodes:
>
> ```bash
> cp ~/.config/rca/config.toml /tmp/rca_deploy.toml
> # manually delete [nodes.*] sections for dead nodes
> rca --config /tmp/rca_deploy.toml agent deploy --force
> ```

### Auto-start (optional, macOS)

```bash
rca daemon register           # register launchd agent (requires App Management permission)
```

Without this, start the daemon manually with `rca daemon start` whenever you reboot.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `daemon request failed` | `rca daemon start`; if still failing `rca daemon logs -f` |
| Node status=dead | `rca connect <node>`; if still dead, re-establish SSH tunneling |
| tunnel down | Reconnect through your usual workflow (ssh config, VPN, tunnel script) |
| agent missing | `rca agent deploy` |
| Command special chars | Use `rca exec --stdin <<'EOF' ... EOF` |
| daemon crash | `rca daemon start` (launchd auto-restarts if registered) |

## Safety boundaries

- Read shared storage restrictions from your config and follow them strictly — files on shared paths often belong to other teams, there's typically no recycle bin, and deletion can destroy days of someone else's work.
- If the cluster has no public internet, use internal PyPI mirrors — don't attempt external URLs (GitHub, PyPI.org, etc.).
- Don't auto-push to `master`/`main` — avoid shipping unreviewed code to teammates.
- **`pkill -f` must use the bracket trick**: `pkill -f "[s]glang.launch_server"` not `pkill -f "sglang.launch_server"` — because the SSH process command line contains the kill pattern, `pkill -f` would match SSH itself and tear the connection down. Same applies to `pgrep -f`, `grep` over process lists, etc.
- **Long-running processes must be backgrounded**: if a process doesn't exit (inference server, training loop), use `nohup ... &` or `tmux new-session -d`, with `echo` placed **after** the background command using `;`:
  ```bash
  # Correct: nohup background + echo outside
  nohup python -m sglang.launch_server ... > /tmp/log 2>&1 & echo "PID=$!"
  # Correct: tmux detach + echo outside
  tmux new-session -d -s sglang "python -m sglang.launch_server ..."; echo "started"
  # Wrong: echo inside tmux's && chain, never executes
  tmux new-session -d -s sglang "python ... && echo started"
  ```

## Architecture

The daemon runs independently of any agent session (Unix socket), so every session shares one connection pool. The CLI is standalone too — usable in shells, scripts, or cron. Cluster-side `agent.py` speaks JSON-Lines v2.1.0 (streaming, cancel, batch, file transfer).

> **Upgrading from MCP v0.3.x**: `remote_bash(node, cmd)` → `rca exec -n node "cmd"`, `remote_bash_batch` → `rca batch`. Legacy `~/.config/remote-cluster-agent/*.md` markdown config auto-migrates on `rca config init`.
