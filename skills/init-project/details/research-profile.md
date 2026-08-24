# Research Profile Documentation

The research profile adds research-project-specific structure on top of the base skeleton.

## Additional Generated Content

### Directories

| Path | Purpose |
|------|---------|
| `docs/reports/weekly/` | Weekly report output |
| `docs/reports/worktree/` | Worktree work reports |
| `docs/plans/` | Design docs and implementation plans |
| `docs/strategy/` | Project vision, roadmap, and strategic documents |
| `docs/strategy/decisions/` | Architectural and strategic decision records |
| `docs/strategy/meetings/` | Meeting notes |
| `docs/strategy/related-work/` | Related work analysis |
| `scripts/training/` | Training scripts |
| `scripts/benchmark/` | Evaluation and benchmark scripts |
| `scripts/data/` | Data processing scripts |
| `scripts/model/` | Model management scripts (merge, convert, etc.) |
| `scripts/infra/` | Infrastructure and DevOps scripts |
| `scripts/analysis/` | Result analysis, statistics, figures, and ablations |
| `scripts/monitoring/` | Training and job monitoring |
| `docs/paper-results/` | Canonical paper-results manifest |

### Files

| Path | Content |
|------|---------|
| `exp.config.yaml` | Points `exp` at `docs/experiment-registry/registry/` |
| `docs/experiment-registry/README.md` | Experiment registry guide (YAML-based, managed by `exp-registry` CLI) |
| `docs/experiment-registry/registry/` | Directory for per-experiment YAML files |
| `.claude/agents/domain-expert.md` | Domain expert agent scaffold (`memory: project`, `permissionMode: plan`) |
| `docs/strategy/vision.md` | Project vision template |
| `docs/strategy/roadmap.md` | Milestones and phases template |
| `docs/strategy/decisions/log.md` | Decision log format and template |
| `docs/paper-results/README.md` | Three-tier provenance and manifest workflow |
| `docs/paper-results/results.yaml` | Canonical numbers allowed into the paper |
| `scripts/benchmark/validate_paper_results.py` | Manifest schema and source-path validation |
| `scripts/benchmark/generate_paper_results.py` | Generate LaTeX result macros |

### CLAUDE.md Appended Content

Appends two compact sections to the canonical `CLAUDE.md`:

- Experiment registry pointer and its relationship to the paper manifest
- Project strategy document locations

Agent definitions are not duplicated in the guide; their frontmatter remains
the source of truth for discovery.

## Experiment Registry

Experiments are managed via the `exp-registry` CLI installed by the personal
skills dependency script, not manual markdown.

```bash
# Register a new experiment
exp register exp01a --type rl --model <model> --config <config-path>

# List all experiments
exp list

# Update status
exp update exp01a --status completed --finding "key result"
```

YAML files are stored in `docs/experiment-registry/registry/`, one per experiment.

## Paper Results Manifest

Paper-bound numbers use three provenance layers:

1. Raw outputs under `outputs/`
2. Full experiment history under `docs/experiment-registry/registry/`
3. Canonical paper values under `docs/paper-results/results.yaml`

Validate and generate LaTeX macros with:

```bash
python3 scripts/benchmark/validate_paper_results.py
python3 scripts/benchmark/generate_paper_results.py
```

The generated project can extend these stubs with model, dataset, checkpoint,
configuration, and artifact hashes when publication-grade provenance requires
them.

## Domain Expert Agent

`domain-expert.md` is a scaffold that users fill in per project:

- `description`: Domain expertise description
- `memory: project`: Retains cross-session diagnostic context
- `permissionMode: plan`: Read-only research, no code modifications
- When to use: Trigger scenarios
- Focus directories: Code locations to research
- Domain knowledge: Key constraints, interface contracts, historical lessons
- Chain hints: If output feeds another agent, note the downstream agent

Typically a research project has 1–3 domain expert agents (e.g., rl-training-expert, data-pipeline-expert).

## Future Extensible Profiles

| Profile | Purpose | Status |
|---------|---------|--------|
| research | Research projects (experiments, reports, domain experts) | Implemented |
| web-app | Web applications (component structure, CI/CD) | Planned |
| data-pipeline | Data pipelines (ETL, monitoring) | Planned |

New profiles are added via `scripts/init-<profile>-profile.sh` + `details/<profile>-profile.md`.
