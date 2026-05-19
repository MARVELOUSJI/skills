#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# collect-daily-data.sh
# Aggregates Claude Code sessions, Codex sessions, Git commits, and Notion tasks for a given day.
# Usage: bash collect-daily-data.sh --date today|yesterday|24h|YYYY-MM-DD
# =============================================================================

# ---------------------------------------------------------------------------
# 1. Parse arguments
# ---------------------------------------------------------------------------
DATE_ARG="today"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE_ARG="$2"; shift 2 ;;
    *) DATE_ARG="$1"; shift ;;
  esac
done

# ---------------------------------------------------------------------------
# 2. Resolve date range (epoch milliseconds)
# ---------------------------------------------------------------------------
case "$DATE_ARG" in
  today)
    DISPLAY_DATE=$(date +%Y-%m-%d)
    START_MS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DISPLAY_DATE 00:00:00" +%s)000
    END_MS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DISPLAY_DATE 23:59:59" +%s)999
    GIT_SINCE="$DISPLAY_DATE 00:00:00"
    GIT_UNTIL="$DISPLAY_DATE 23:59:59"
    ;;
  yesterday)
    DISPLAY_DATE=$(date -v-1d +%Y-%m-%d)
    START_MS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DISPLAY_DATE 00:00:00" +%s)000
    END_MS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DISPLAY_DATE 23:59:59" +%s)999
    GIT_SINCE="$DISPLAY_DATE 00:00:00"
    GIT_UNTIL="$DISPLAY_DATE 23:59:59"
    ;;
  24h)
    DISPLAY_DATE="past 24h ($(date -v-24H +%Y-%m-%d) ~ $(date +%Y-%m-%d))"
    END_MS=$(date +%s)000
    START_MS=$(date -v-24H +%s)000
    GIT_SINCE="24 hours ago"
    GIT_UNTIL="now"
    ;;
  [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])
    DISPLAY_DATE="$DATE_ARG"
    START_MS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DATE_ARG 00:00:00" +%s)000
    END_MS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$DATE_ARG 23:59:59" +%s)999
    GIT_SINCE="$DATE_ARG 00:00:00"
    GIT_UNTIL="$DATE_ARG 23:59:59"
    ;;
  *)
    echo "ERROR: Unknown date format: $DATE_ARG" >&2
    echo "Usage: --date today|yesterday|24h|YYYY-MM-DD" >&2
    exit 1
    ;;
esac

echo "Daily Summary: $DISPLAY_DATE"
echo "================================"
echo ""

# ---------------------------------------------------------------------------
# 3. Section 1: Claude Code Sessions
# ---------------------------------------------------------------------------
echo "=== CLAUDE CODE SESSIONS ==="
echo ""

HISTORY_FILE="$HOME/.claude/history.jsonl"
CODEX_SESSIONS_DIR="$HOME/.codex/sessions"
CODEX_SESSION_INDEX="$HOME/.codex/session_index.jsonl"

if [[ -f "$HISTORY_FILE" ]]; then
  START_MS="$START_MS" END_MS="$END_MS" python3 << 'PYEOF'
import json
import os
import re
from pathlib import Path
from collections import defaultdict

start_ms = int(os.environ["START_MS"])
end_ms = int(os.environ["END_MS"])
home = Path.home()
history_file = home / ".claude" / "history.jsonl"

# Read history entries within time range, group by sessionId
sessions = defaultdict(list)
session_projects = {}

with open(history_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = entry.get("timestamp", 0)
        if start_ms <= ts <= end_ms:
            sid = entry.get("sessionId", "")
            if sid:
                sessions[sid].append(entry)
                if "project" in entry:
                    session_projects[sid] = entry["project"]

if not sessions:
    print("(no sessions found)")
else:
    def encode_path(p):
        """Encode path like Claude does: non-alnum and non-hyphen chars become hyphens."""
        return re.sub(r'[^a-zA-Z0-9\-]', '-', p)

    for sid in sorted(sessions.keys(), key=lambda s: min(e["timestamp"] for e in sessions[s])):
        entries = sessions[sid]
        project_path = session_projects.get(sid, "unknown")
        project_name = os.path.basename(project_path) if project_path != "unknown" else "unknown"

        # Compute time range for this session
        timestamps = [e["timestamp"] for e in entries]
        from datetime import datetime
        start_dt = datetime.fromtimestamp(min(timestamps) / 1000)
        end_dt = datetime.fromtimestamp(max(timestamps) / 1000)

        # Read session JSONL for user messages
        encoded_cwd = encode_path(project_path)
        session_jsonl = home / ".claude" / "projects" / encoded_cwd / f"{sid}.jsonl"

        user_messages = []
        if session_jsonl.exists():
            with open(session_jsonl) as sf:
                for sline in sf:
                    sline = sline.strip()
                    if not sline:
                        continue
                    try:
                        msg = json.loads(sline)
                    except json.JSONDecodeError:
                        continue
                    if msg.get("type") != "user":
                        continue
                    if msg.get("userType") == "system":
                        continue

                    # Extract text content
                    content = msg.get("message", {}).get("content", "")
                    if isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text_parts.append(part.get("text", ""))
                        content = " ".join(text_parts)
                    if not isinstance(content, str):
                        continue

                    content = content.strip()
                    # Redact potential secrets (API keys, tokens)
                    content = re.sub(r'(ntn_|sk-|ghp_|gho_|glpat-|xoxb-|xoxp-)\S+', r'\1***', content)
                    # Skip messages starting with < or /
                    if content.startswith("<") or content.startswith("/"):
                        continue
                    # Skip very short messages
                    if len(content) < 5:
                        continue

                    # Truncate to 120 chars
                    if len(content) > 120:
                        content = content[:117] + "..."
                    user_messages.append(content)

        msg_count = len(user_messages)
        print(f"[{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}] {project_name} ({msg_count} msgs)")
        for um in user_messages[:8]:
            print(f"  - {um}")
        if msg_count > 8:
            print(f"  ... and {msg_count - 8} more messages")
        print()
PYEOF
else
  echo "(history.jsonl not found)"
  echo ""
fi

# ---------------------------------------------------------------------------
# 3b. Section 1b: Codex Sessions
# ---------------------------------------------------------------------------
echo "=== CODEX SESSIONS ==="
echo ""

if [[ -d "$CODEX_SESSIONS_DIR" ]]; then
  START_MS="$START_MS" END_MS="$END_MS" CODEX_SESSIONS_DIR="$CODEX_SESSIONS_DIR" CODEX_SESSION_INDEX="$CODEX_SESSION_INDEX" python3 << 'PYEOF'
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

start_ms = int(os.environ["START_MS"])
end_ms = int(os.environ["END_MS"])
sessions_dir = Path(os.environ["CODEX_SESSIONS_DIR"])
session_index = Path(os.environ["CODEX_SESSION_INDEX"])

thread_names = {}
if session_index.exists():
    with open(session_index) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = entry.get("id")
            if sid:
                thread_names[sid] = entry.get("thread_name", "")

def iso_to_ms(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return int(dt.timestamp() * 1000)

def local_hhmm(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%H:%M")

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in {"input_text", "text"}:
                parts.append(item.get("text", ""))
        return " ".join(parts)
    return ""

def keep_user_text(text):
    text = text.strip()
    if len(text) < 5:
        return ""
    skip_prefixes = (
        "<",
        "# AGENTS.md instructions",
        "The following is the Codex agent history",
        ">>> TRANSCRIPT",
        "Reviewed Codex session id:",
    )
    if text.startswith(skip_prefixes):
        return ""
    text = re.sub(r"(ntn_|sk-|ghp_|gho_|glpat-|xoxb-|xoxp-)\S+", r"\1***", text)
    return text[:117] + "..." if len(text) > 120 else text

items = []
for path in sessions_dir.rglob("*.jsonl"):
    meta = {}
    timestamps = []
    user_messages = []
    skip_session = False

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            payload = entry.get("payload", {})
            if entry.get("type") == "session_meta":
                meta = payload if isinstance(payload, dict) else {}
                source = meta.get("source")
                if isinstance(source, dict) and "subagent" in source:
                    skip_session = True
                    break

            ts_ms = iso_to_ms(entry.get("timestamp"))
            in_range = ts_ms is not None and start_ms <= ts_ms <= end_ms
            if in_range:
                timestamps.append(ts_ms)

            if not in_range:
                continue
            if entry.get("type") != "response_item":
                continue
            if not isinstance(payload, dict):
                continue
            if payload.get("type") != "message" or payload.get("role") != "user":
                continue

            text = keep_user_text(extract_text(payload.get("content", "")))
            if text:
                user_messages.append(text)

    if skip_session or not timestamps:
        continue

    sid = meta.get("id") or path.stem.split("-")[-1]
    cwd = meta.get("cwd", "unknown")
    project_name = os.path.basename(cwd) if cwd != "unknown" else "unknown"
    thread_name = thread_names.get(sid, "")
    items.append((min(timestamps), max(timestamps), project_name, thread_name, user_messages))

if not items:
    print("(no sessions found)")
else:
    for start, end, project_name, thread_name, user_messages in sorted(items, key=lambda item: item[0]):
        label = f"{project_name}"
        if thread_name:
            label += f" / {thread_name}"
        print(f"[{local_hhmm(start)}-{local_hhmm(end)}] {label} ({len(user_messages)} msgs)")
        for msg in user_messages[:8]:
            print(f"  - {msg}")
        if len(user_messages) > 8:
            print(f"  ... and {len(user_messages) - 8} more messages")
        print()
PYEOF
else
  echo "(~/.codex/sessions not found)"
  echo ""
fi

# ---------------------------------------------------------------------------
# 4. Section 2: Git Commits
# ---------------------------------------------------------------------------
echo "=== GIT COMMITS ==="
echo ""

# Collect project paths from history.jsonl + hardcoded extras
PROJECT_PATHS=()

if [[ -f "$HISTORY_FILE" ]]; then
  while IFS= read -r proj; do
    if [[ -d "$proj/.git" ]]; then
      PROJECT_PATHS+=("$proj")
    fi
  done < <(python3 -c "
import json, sys
seen = set()
with open('$HISTORY_FILE') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            e = json.loads(line)
            p = e.get('project','')
            if p and p not in seen:
                seen.add(p)
                print(p)
        except: pass
")
fi

# Add project paths observed in Codex sessions.
if [[ -d "$CODEX_SESSIONS_DIR" ]]; then
  while IFS= read -r proj; do
    if [[ -d "$proj/.git" ]]; then
      PROJECT_PATHS+=("$proj")
    fi
  done < <(CODEX_SESSIONS_DIR="$CODEX_SESSIONS_DIR" python3 - << 'PYEOF'
import json
import os
from pathlib import Path

seen = set()
for path in Path(os.environ["CODEX_SESSIONS_DIR"]).rglob("*.jsonl"):
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "session_meta":
                continue
            payload = entry.get("payload", {})
            if not isinstance(payload, dict):
                continue
            source = payload.get("source")
            if isinstance(source, dict) and "subagent" in source:
                break
            cwd = payload.get("cwd")
            if cwd and cwd not in seen:
                seen.add(cwd)
                print(cwd)
            break
PYEOF
)
fi

# Add hardcoded extra repos
EXTRA_REPOS=(
  "$HOME/workspace/dotfiles"
  "$HOME/workspace/agentic_umm/agentic_umm"
)
for repo in "${EXTRA_REPOS[@]}"; do
  if [[ -d "$repo/.git" ]]; then
    PROJECT_PATHS+=("$repo")
  fi
done

# Deduplicate using a temp file
UNIQUE_PATHS=()
_seen_file=$(mktemp)
trap "rm -f $_seen_file" EXIT
for p in "${PROJECT_PATHS[@]}"; do
  real_p=$(cd "$p" 2>/dev/null && pwd -P) || continue
  if ! grep -qxF "$real_p" "$_seen_file" 2>/dev/null; then
    echo "$real_p" >> "$_seen_file"
    UNIQUE_PATHS+=("$p")
  fi
done

FOUND_COMMITS=false
for proj in "${UNIQUE_PATHS[@]}"; do
  proj_name=$(basename "$proj")
  commits=$(cd "$proj" && git log --since="$GIT_SINCE" --until="$GIT_UNTIL" --format="%ai %s" --all 2>/dev/null || true)
  if [[ -n "$commits" ]]; then
    FOUND_COMMITS=true
    echo "[$proj_name]"
    while IFS= read -r commit_line; do
      # Extract time (HH:MM) and message from format "YYYY-MM-DD HH:MM:SS +ZZZZ message"
      commit_time=$(echo "$commit_line" | awk '{print substr($2,1,5)}')
      commit_msg=$(echo "$commit_line" | cut -d' ' -f4-)
      echo "  $commit_time $commit_msg"
    done <<< "$commits"
    echo ""
  fi
done

if [[ "$FOUND_COMMITS" = false ]]; then
  echo "(no commits found)"
  echo ""
fi

# ---------------------------------------------------------------------------
# 5. Section 3: Notion Tasks
# ---------------------------------------------------------------------------
echo "=== NOTION TASKS ==="
echo ""

NOTION_SCRIPT=""
for candidate in \
  "$HOME/.agents/skills/notion-lifeos/scripts/query-tasks.sh" \
  "$HOME/.claude/skills/notion-lifeos/scripts/query-tasks.sh"; do
  if [[ -x "$candidate" ]] || [[ -f "$candidate" ]]; then
    NOTION_SCRIPT="$candidate"
    break
  fi
done

if [[ -n "$NOTION_SCRIPT" ]]; then
  if [[ "$DATE_ARG" = "24h" ]]; then
    # Query both yesterday and today
    YESTERDAY=$(date -v-1d +%Y-%m-%d)
    TODAY=$(date +%Y-%m-%d)
    echo "--- $YESTERDAY ---"
    bash "$NOTION_SCRIPT" --date "$YESTERDAY" --limit 50 2>/dev/null || echo "(query failed)"
    echo ""
    echo "--- $TODAY ---"
    bash "$NOTION_SCRIPT" --date "$TODAY" --limit 50 2>/dev/null || echo "(query failed)"
  else
    QUERY_DATE="$DISPLAY_DATE"
    # For "today" or "yesterday", DISPLAY_DATE is already YYYY-MM-DD
    bash "$NOTION_SCRIPT" --date "$QUERY_DATE" --limit 50 2>/dev/null || echo "(query failed)"
  fi
else
  echo "(notion-lifeos skill not found, skipping)"
fi

echo ""
echo "================================"
echo "End of daily data collection"
