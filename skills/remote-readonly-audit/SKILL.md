---
name: remote-readonly-audit
description: "Read remote source safely for diagramming, review, or fact-checking. Use when the user wants the actual code path from a remote repo without editing or fully syncing the project; copies the minimal file set with `rca cp` and inspects it locally. Triggers: 'read the remote code', 'what is the real method path', 'draw a flowchart from the remote source', '看一下远端代码', '根据远端源码画流程图', '核对方法实际走的分支'. NOT for: editing remote code, running training, or general cluster operations (use remote-cluster-agent), or repos that already have an authoritative local checkout."
user-invocable: false
allowed-tools:
  - Bash
  - Read
  - Grep
---

# Remote Read-Only Code Audit

## When to use

Use this when:
1. The user wants a code-grounded explanation, architecture diagram, or method fact check from a remote tree.
2. The task only needs source inspection, not remote edits or project initialization.
3. `rca exec` quoting / output size is likely to be brittle.

Do not use this when:
1. The user needs code changes on the remote repo.
2. The remote files must stay on the remote machine for policy reasons.
3. A local checkout already contains the authoritative files.

## Inputs / context to gather

1. Confirm the remote host / project alias and the exact file or entrypoint the user named.
2. Confirm whether the user needs:
   - architecture reconstruction,
   - fact checking,
   - debugging,
   - or provenance tracing.
3. Identify the minimum file set before copying:
   - entrypoint (`main.py`, training script, etc.),
   - direct model modules,
   - renderer / loss path,
   - dataset / normalization code if state semantics matter.

## Procedure

1. Start with the user-named entrypoint and infer the smallest dependent set.
2. Prefer copying files locally with `rca cp` over composing long remote shell pipelines.
3. Inspect the copied files locally with `rg`, `sed`, and line-numbered views.
4. Reconstruct the active path in execution order:
   - entrypoint / training loop,
   - model branch selection,
   - state encoding / normalization,
   - geometry deformation,
   - renderer / loss.
5. Separate active-path symbols from helper or legacy code before summarizing.
6. Write the result in the shape the user asked for:
   - figure flowchart,
   - reviewer-facing fact check,
   - provenance note,
   - or debugging summary.

Minimal usage example:

```bash
rca cp <node>:<remote-repo>/main.py /tmp/<project>_main.py
rg -n "<stage_flag>|<forward_fn>|render_mode|loss" /tmp/<project>_main.py
```

## Efficiency plan

1. Copy only the files needed for the active path; do not sync the whole repo.
2. Cache the local copied files for the rest of the session so repeated questions reuse the same evidence.
3. Stop expanding once the user-requested claim is grounded end-to-end.
4. If a symbol is defined but not used in the active branch, note it and move on instead of reverse-engineering every helper.

## Pitfalls and fixes

- Symptom: `rca exec` fails with quoting / JSON / escape errors.
  - Likely cause: command shape is too complex.
  - Fix: switch to `rca cp` and inspect locally.

- Symptom: the final summary turns into a generic architecture description.
  - Likely cause: the active branch was not distinguished from auxiliary code.
  - Fix: trace the actual call chain from the user-named entrypoint before writing.

- Symptom: the diagram includes too many training internals.
  - Likely cause: optimization mechanics were mixed into the core forward path.
  - Fix: keep the main figure on forward inference and move phase logic / optimizer details into an inset or separate note.

## Verification checklist

1. Every major box in the explanation maps to a specific file/function that was inspected.
2. The result names the active branch / method path, not just module names.
3. State semantics, renderer, and supervision are grounded in code if the user asked for method structure.
4. The final answer explicitly distinguishes active blocks from auxiliary or legacy code when that matters.
