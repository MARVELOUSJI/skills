---
name: mac-app-uninstaller
description: Safely uninstall and clean up Mac applications by discovering app bundles, bundle IDs, launch agents, login/background items, receipts, caches, preferences, containers, and other leftovers, then presenting a user-confirmed cleanup plan before moving anything to Trash. Use this whenever the user wants to delete, uninstall, remove, cleanly reinstall, or thoroughly clean up a macOS app, menu bar utility, input method, background helper, or old/non-official app before installing a new version. Trigger on Chinese requests like "卸载 Mac 软件", "把 XX 删干净", "清理 XX 残留", "找 XX 装在哪", "先不要动，列清理方案", and "重装正版前清掉旧版本". NOT for cleaning code repos, build artifacts, package dependencies, browser history, malware incident response, or broad system cleanup without a specific app name.
---

# Mac App Uninstaller

Use this skill to remove a macOS application cautiously and reversibly. The goal is to help the user uninstall an app cleanly without surprising them: first identify the app and its true bundle IDs, then separate confirmed leftovers from risky/ambiguous matches, then wait for explicit confirmation before moving anything to Trash.

This skill is especially useful for apps that do not appear in `/Applications`, including input methods under `/Library/Input Methods`, menu bar tools, launch agents, background helpers, and apps installed by `.pkg` installers.

## Core Principles

- Start read-only. The first pass discovers and reports; it does not move, delete, unload, or kill anything.
- Prefer exact identifiers over fuzzy names. Once an `.app` is found, inspect `Contents/Info.plist` and use the bundle ID as the main cleanup key.
- Explain why each candidate belongs to the app. A path is safer to remove when it matches the app name, bundle ID, package receipt, launch label, or executable path.
- Move to a timestamped Trash directory by default. Do not permanently delete files unless the user separately requests it after seeing the reversible plan.
- Do not use broad destructive matches such as `*input*`, `*keyboard*`, `*switch*`, or `*输入法*` as deletion criteria. These are discovery hints only; they can match system components and unrelated tools.
- Treat system-level helpers as higher risk. Anything under `/Library/LaunchDaemons`, `/Library/PrivilegedHelperTools`, or requiring `sudo` needs a separate callout and confirmation.

## Intake

Begin by restating the app name and scope. If the app name is ambiguous, ask for one short clarification before searching.

Capture:

- App name as provided by the user, including Chinese and English variants.
- Whether the user wants uninstall only, reinstall cleanup, or a non-official/old-version cleanup before installing a new official version.
- Whether the app is likely to be an input method, menu bar utility, background helper, browser helper, or normal `.app`.
- Whether destructive operations are allowed later. Default: only move to Trash after confirmation.

## Phase 1: Read-Only Discovery

Search for app bundles and obvious install locations. Prefer `find`, `mdfind`, `pkgutil`, `brew`, `launchctl`, `sfltool`, and `ps` as read-only tools.

Useful search roots:

```bash
/Applications
$HOME/Applications
/Library/Input Methods
$HOME/Library/Input Methods
/Library/LaunchAgents
$HOME/Library/LaunchAgents
/Library/LaunchDaemons
/Library/PrivilegedHelperTools
/Library/Application Support
$HOME/Library/Application Support
/Library/Preferences
$HOME/Library/Preferences
/Library/Caches
$HOME/Library/Caches
$HOME/Library/HTTPStorages
$HOME/Library/Containers
$HOME/Library/Group Containers
$HOME/Library/Saved Application State
$HOME/Library/WebKit
$HOME/Library/Logs
$HOME/Downloads
$HOME/Desktop
$HOME/Documents
/Users/Shared
/private/var/db/receipts
```

Start with precise name queries. If the user only gives a generic Chinese name, search that exact name first, then likely English names.

Examples:

```bash
find /Applications "$HOME/Applications" "/Library/Input Methods" "$HOME/Library/Input Methods" \
  -maxdepth 3 \( -iname '*APP_NAME*' -o -iname '*APP_ALIAS*' \) -print 2>/dev/null

mdfind 'kMDItemFSName == "*APP_NAME*"c || kMDItemFSName == "*APP_ALIAS*"c'
```

When an app bundle is found, inspect its metadata:

```bash
plutil -p "/path/to/App.app/Contents/Info.plist" | \
  rg -n 'CFBundle|Identifier|Name|DisplayName|Version|Executable'
```

Then use the bundle ID and executable name to search for stronger matches:

```bash
pkgutil --pkgs | rg -i 'bundle-id|app-name'
brew list --cask 2>/dev/null | rg -i 'app-name|bundle-id'
sfltool dumpbtm 2>/dev/null | rg -i 'app-name|bundle-id'
launchctl print "gui/$(id -u)" 2>/dev/null | rg -i 'app-name|bundle-id'
launchctl print system 2>/dev/null | rg -i 'app-name|bundle-id'
ps -axo pid,comm,args | rg -i 'app-name|bundle-id|executable'
```

For input methods, also check whether the current input source still references the bundle:

```bash
plutil -p "$HOME/Library/Preferences/com.apple.HIToolbox.plist" 2>/dev/null | \
  rg -n 'app-name|bundle-id|input-mode-id'
```

If the environment cannot read the process list or some protected directories, say so and continue with the available evidence.

## Phase 2: Classify Findings

Before proposing actions, classify findings into three groups:

- **Safe to move to Trash**: paths that clearly match the app bundle ID, app-specific support directory, app-specific preferences, caches, HTTP storage, saved state, receipts, launch agents, or old installers.
- **Needs confirmation**: paths that share a vendor name or fuzzy alias but could belong to another app, shared framework, or future official install.
- **Do not touch**: system components, unrelated input methods, unrelated keyboard tools, Apple files, other apps, broad keyword matches, and any path whose relationship is not clear.

For each candidate, include:

- Path
- Evidence, such as bundle ID, filename, plist label, executable path, or search reason
- Risk level: low / medium / high
- Recommended action: move to Trash / unload then move / leave alone / user decide

## Phase 3: Present Cleanup Plan

After discovery, stop and show the plan. Do not execute cleanup until the user explicitly confirms.

Use this structure:

```markdown
# Mac App Uninstall Discovery: <app name>

## Summary
- App name:
- Bundle ID(s):
- Install location(s):
- Running/background status:
- Package manager / receipt status:

## Safe to Move to Trash
| Path | Evidence | Risk | Action |

## Needs Confirmation
| Path | Why it matched | Risk | Question |

## Do Not Touch
| Path | Reason |

## Proposed Cleanup Steps
1. Quit app / unload launch items if needed.
2. Create Trash backup directory.
3. Move confirmed files into the backup directory.
4. Refresh caches or preferences if appropriate.
5. Run verification searches.

## Trash Backup Directory
`$HOME/.Trash/<app-slug>-cleanup-YYYYMMDD-HHMMSS`

## Questions Before Execution
- ...
```

If there are no unresolved questions and all candidates are clearly app-specific, still wait for an explicit "确认", "可以清理", "go ahead", or equivalent.

## Phase 4: Execute After Confirmation

Once the user confirms, perform only the approved actions.

Use a timestamped Trash directory:

```bash
trash_dir="$HOME/.Trash/<app-slug>-cleanup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$trash_dir"
```

For files with the same basename from different source directories, preserve source grouping to avoid collisions:

```bash
mkdir -p "$trash_dir/Preferences" "$trash_dir/Caches" "$trash_dir/Application Support" "$trash_dir/LaunchAgents"
```

Move files, do not remove them:

```bash
mv "$source_path" "$trash_dir/<group>/"
```

If a launch agent or daemon is confirmed, unload it before moving the plist:

```bash
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/<label>.plist"
```

For system-level launch daemons or privileged helpers, request explicit elevated approval and explain why. Do not hide `sudo` behind a broad script.

If the app was installed through Homebrew cask, prefer:

```bash
brew uninstall --cask <cask-name>
```

Then do the same read-only residual search and Trash-based cleanup for leftovers.

## Phase 5: Verify

After cleanup, rerun targeted searches and report remaining hits. Exclude the Trash backup directory from "still installed" results.

Verify:

- App bundle no longer exists in `/Applications`, `~/Applications`, `/Library/Input Methods`, or `~/Library/Input Methods`.
- Launch agents/daemons no longer exist or no longer reference the bundle.
- `sfltool dumpbtm`, `launchctl`, package receipts, and process list do not show real running/background items.
- User Library locations no longer contain app-specific bundle ID leftovers.
- Any remaining ambiguous hits are listed separately.

If process commands only show the current `rg` or `ps` command itself, call that out as not a real app process.

Use this final report:

```markdown
# Cleanup Result: <app name>

## Moved to Trash
| Original path | Trash path |

## Skipped / Missing
| Path | Reason |

## Verification
- App bundle:
- Input source / login item / launch item:
- Package receipt:
- Running process:
- User Library leftovers:

## Remaining Items
- None / list ambiguous leftovers

## Trash Backup Location
`...`

## Suggested Next Steps
- Use the machine normally for a few days.
- Install the official version if desired.
- Empty Trash only after confirming everything works.
```

## Privacy and Permissions

Some app permissions are stored in macOS privacy databases and are safer to remove through System Settings. After file cleanup, remind the user to inspect:

- System Settings -> Privacy & Security -> Accessibility
- System Settings -> Privacy & Security -> Input Monitoring
- System Settings -> Privacy & Security -> Automation
- System Settings -> General -> Login Items

Do not edit TCC databases by default. If the user specifically asks to clean TCC entries, explain the risk and handle it as a separate task.

## Near Misses

Do not trigger this skill for:

- Cleaning a source-code repository, experiment outputs, Python caches, or build artifacts.
- Uninstalling package dependencies inside npm, pip, conda, uv, cargo, or Homebrew formula environments unless the user specifically asks to remove a macOS app/cask.
- Malware triage or incident response. For suspected malware, recommend a security-focused workflow and avoid promising complete forensic cleanup.
- Broad "clean my Mac" requests without a specific app name.

