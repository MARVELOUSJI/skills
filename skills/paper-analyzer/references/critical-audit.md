# Critical Audit Guide

Read this file for standard deep reads and reproduction/review audits. Apply only relevant checks and report only issues that could change the interpretation.

## General Checks

### Claim and construct

- Does the stated metric or measurement represent the concept the paper claims to study?
- Are broad terms such as reasoning, robustness, intelligence, safety, or generalization operationally defined?
- Does the conclusion stay within the population, setting, and conditions actually tested?

### Attribution and alternatives

- Does the design isolate the proposed cause, or only establish association?
- Could data selection, preprocessing, tuning, instrumentation, or another uncontrolled variable explain the result?
- Does an ablation remove only the intended component, or change several factors at once?

### Reliability

- Are sample size, number of runs, variability, error bars, confidence intervals, or significance tests reported when appropriate?
- Is the practical effect meaningful, not merely statistically detectable?
- Are negative, null, or inconsistent results omitted from the main narrative?

### Generalization

- Are datasets, participants, environments, tasks, or conditions broad enough for the stated scope?
- Are out-of-distribution, robustness, or boundary-condition tests appropriate to the claim?
- Does the paper mistake benchmark performance for real-world capability?

### Reproducibility

- Are data, code, preprocessing, environment, hyperparameters, random seeds, hardware, and evaluation commands sufficiently specified?
- Are released artifacts consistent with the version and experiments described in the paper?
- Separate “artifacts available” from “results independently reproduced.”

## AI and Machine Learning Additions

- Check train/test leakage, benchmark contamination, data filtering, and use of hidden evaluation data.
- Check whether baselines receive comparable data, compute, model scale, tuning effort, and inference budget.
- Verify checkpoint identity, prompt/template, decoding parameters, judge model/version, and metric implementation.
- For LLM-as-judge or human evaluation, inspect rubric, blinding, inter-rater agreement, sample size, and denominator.
- For improvements across many benchmarks, check whether the claim survives variance, multiple comparisons, and selectively reported tasks.
- For ablations, ask whether the removed component was retuned fairly and whether interactions between components were tested.

## Robotics Additions

- Separate simulation, replay, hardware-in-the-loop, and real-robot evidence.
- Check calibration, sensing latency, control frequency, safety intervention, reset policy, and operator assistance.
- Verify whether success is per trial, per trajectory, per subtask, or per time window.
- Check environment diversity, initial-condition coverage, failure definitions, and sim-to-real assumptions.
- Distinguish algorithmic improvement from hardware, perception, training-data, or controller changes.

## Severity Rule

Prioritize findings as follows:

1. **Conclusion-changing**: invalidates or substantially narrows a headline claim.
2. **Confidence-reducing**: evidence may be correct but is too weak or incomplete.
3. **Reproduction-blocking**: prevents independent verification without necessarily disproving the result.
4. **Presentation-only**: clarity issues that do not affect the evidence.

Lead with levels 1–2. Mention levels 3–4 only when relevant to the user's goal.
