---
name: publication-asset-freeze
description: "Freeze final visualization outputs into a reproducible, publication-ready bundle. Use when the user wants final `output/` artifacts, code, settings, manifests, QA, and methods-style docs preserved together so future reruns do not need rediscovery. Triggers: 'freeze the final figures', 'make the outputs reproducible', 'publication asset bundle', '定稿这些图', '冻结最终产物', '把 output 固化成可复现', '论文图资产打包'. NOT for: pausing feature development and writing handoff docs (use wrap-up), freeing disk space (use folder-cleanup), or exploratory sweeps whose pipeline is still changing."
argument-hint: "[asset-root-or-output-dir]"
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Grep
---

# Publication Asset Freeze

## When to use

Use this when:
1. The user says final visualization outputs under `output/` must stay reproducible.
2. The task is a wrap-up / freeze / handoff for publication assets rather than an exploratory sweep.
3. The user wants code, settings, manifests, QA artifacts, and prose/doc context preserved together.

Do not use this when:
1. The output style or pipeline contract is still exploratory.
2. The user only wants one image regenerated, not a durable asset bundle.
3. The workspace truth still lives elsewhere and this directory is not meant to become the keeper output root.

## Inputs / context to gather

1. Identify the keeper output root the user expects, usually `output/`.
2. Find the source-of-truth generation scripts, tests, and any existing manifests or summary JSON files.
3. Confirm whether there are manual exceptions that must be recorded explicitly:
   - fixed crops,
   - rotations,
   - color overrides,
   - selected subsets,
   - special naming/layout rules.
4. Check whether the user wants publication-facing prose, and if so whether the target tone is Supplementary Methods / Nature / Science Robotics style.
5. Identify the working runtime that actually has the required dependencies.

## Procedure

1. Freeze the contract before cleanup.
   - List what final artifacts are supposed to remain.
   - Separate keeper outputs from exploratory sweeps, caches, or transient scratch files.
   - If deletion is involved, give a short retain/delete plan first.
2. Make the generation path explicit.
   - Locate the authoritative generation script(s).
   - Record final settings in machine-readable or at least file-based form.
   - Prefer manifests, summary JSON, or dedicated settings files over chat-only notes.
3. Preserve reproducibility metadata alongside the assets.
   - Add or update:
     - settings/manifest file,
     - checksums,
     - reproduce command note,
     - QA builder if a contact sheet or board is part of the deliverable.
4. Verify with the real runtime.
   - Use the environment that actually contains the dependencies.
   - Prefer `python -m pytest` over console-entry `pytest` when local import behavior is brittle.
   - Keep at least one end-to-end verification command written down.
5. Do a stronger-than-files-exist reproducibility pass.
   - Rebuild QA artifacts from the frozen outputs or manifests.
   - If feasible, do a clean-room rerun in a fresh temp root.
   - Compare rebuilt outputs against the frozen set with checksums or byte equality.
   - For remote rendering, explicitly pull the exact generated artifacts and hash them;
     do not treat one-way synchronization as checksum evidence.
   - Freeze the accepted master under a stable output path and require later edits to use
     a new version/run rather than overwrite it.
6. Preserve long-term context if the directory is meant to be resumed later.
   - Add/update `CLAUDE.md`.
   - Keep `AGENTS.md -> CLAUDE.md` if this workspace uses that compatibility pattern.
   - Store durable background/progress/decisions under `docs/knowledge/`.
7. Write the final handoff in publication-facing style when requested.
   - Keep prose restrained and auditable.
   - Explicitly distinguish automatic behavior from manual overrides.

Minimal usage example:

```bash
conda run -n <env> python -m pytest tests -v
python utils/build_contact_sheet.py
python utils/verify_reproducibility.py
```

## Efficiency plan

1. Start from existing output summaries, manifests, and keeper directories before reading large code paths.
2. Reuse an existing reference implementation instead of inventing new heuristics when the user points to one.
3. Treat the final output tree as the primary routing layer; only dig deeper when a setting or provenance detail is missing.
4. Stop once the bundle has:
   - keeper outputs,
   - explicit settings/manifests,
   - one real verification path,
   - and durable docs/context.

## Pitfalls and fixes

- Symptom: tests fail under `pytest` but not `python -m pytest`.
  - Likely cause: console-entry import path behavior differs in this environment.
  - Fix: switch to `python -m pytest` in the known-good env and record that as the default command.

- Symptom: the final tree keeps regaining `.DS_Store` or other Finder metadata.
  - Likely cause: macOS metadata regeneration during browsing/verification.
  - Fix: finish with an explicit delete-and-recheck pass.

- Symptom: the verifier fails when dynamically loading a dataclass-bearing module.
  - Likely cause: the module was not inserted into `sys.modules` before `exec_module`.
  - Fix: register the module first, then execute it.

- Symptom: outputs are “saved,” but reproducibility still depends on the current tree.
  - Likely cause: only static files were checked.
  - Fix: perform a clean-room rerun and compare checksums or byte-identical outputs.

- Symptom: an older cache appears interchangeable because one stage matches.
  - Likely cause: cache identity was inferred from partial visual/output similarity.
  - Fix: preserve and verify the exact accepted stage caches and frame-directory hashes;
    regenerate derived pages/videos in the clean-room run.

- Symptom: Supplementary prose overclaims what was automatic.
  - Likely cause: manual overrides were not separated from algorithmic steps.
  - Fix: spell out fixed crops/rotations/manual selections as predefined visualization choices.

## Verification checklist

1. The keeper output root contains only the intended final artifacts.
2. Final settings are stored in files, not just conversation history.
3. There is a reproducibility manifest or equivalent machine-readable contract.
4. There is at least one recorded verification command that passes in the real runtime.
5. QA artifacts can be rebuilt from the frozen assets or manifests.
6. If feasible, a clean-room rerun reproduces the frozen outputs and checksum equality is checked.
7. Publication-facing prose matches the actual pipeline boundaries and manual exceptions.
8. Remote-produced final artifacts were explicitly transferred and hashed, and future edits
   have a new-version path that cannot overwrite the accepted master.
