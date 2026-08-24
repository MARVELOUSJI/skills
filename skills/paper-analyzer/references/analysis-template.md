# Paper Analysis Template

Use this template for a standard deep read. Translate headings into the user's language. Omit empty or irrelevant fields, and keep the main body concise.

## 1. Executive Takeaways

- **Motivation:** Why this problem matters and what limitation motivates the work.
- **Task:** What is being predicted, generated, explained, controlled, or measured.
- **Method:** The central mechanism in plain language.
- **Core result:** The strongest verified result and its condition.
- **Contribution/novelty:** What is claimed, what is demonstrated, and whether external novelty was checked.
- **Main limitation:** The issue most likely to narrow or change the conclusion.

## 2. Motivation

Write the chain:

`important problem → prior limitation or missing evidence → opportunity addressed by this paper`

State whether the gap is supported by cited prior work or is only asserted by the authors.

## 3. Setting Card

Use a table only for fields that apply.

| Field | What to record |
|---|---|
| Task/question | What must be predicted, generated, explained, controlled, or measured? |
| Input / intervention | What information or treatment enters the system? |
| Output / outcome | What is produced or measured? |
| Data / population / environment | On what evidence base is the claim tested? |
| Learning or study regime | Supervision, split, controls, assumptions, or protocol |
| Baselines / comparators | What is the method compared against? |
| Metrics | What each metric means, including denominator or judge |
| Constraints | Information, compute, hardware, or deployment restrictions |

## 4. Method Map

Explain the central idea first. Then map only important components:

| Problem or limitation | Design choice | Why it should work | Dependency or assumption |
|---|---|---|---|
| ... | ... | ... | ... |

## 5. Experiment–Claim Matrix

Each main row should answer what the experiment was designed to establish, not merely repeat its result.

| Experiment question / hypothesis | Comparison and controlled variables | Data and metric | Key result | Authors' interpretation | Actual support | Evidence locator |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | direct / partial / unsupported / unverified | p. N, Fig./Table/Section X |

Guidelines:

- Give separate rows to the main result, ablations, robustness/generalization, efficiency, and diagnostic/causal tests when they support different claims.
- State whether comparisons use the same data, checkpoint, training budget, tuning budget, and evaluation protocol when relevant.
- Explain the metric and denominator before interpreting a percentage or aggregate score.
- Group repeated secondary results instead of producing a row for every appendix table.

## 6. Contribution and Novelty

| Level | Finding |
|---|---|
| Author-claimed novelty | What the authors say is new |
| Internally demonstrated contribution | What the paper's own evidence substantiates |
| Externally verified novelty | Result of comparison with primary prior work, or “not checked” |

Classify contributions when useful: problem/setting, method/mechanism, empirical finding, theory, dataset/benchmark, system, or engineering integration.

## 7. Critical Audit

Report only material issues:

1. The strongest part of the evidence.
2. The main gap between claim and evidence.
3. The most plausible alternative explanation.
4. The boundary beyond which the result should not be generalized.
5. The missing information that most affects reproducibility.

## 8. Evidence Appendix

| Claim or number | Voice | Evidence locator | Status | Note |
|---|---|---|---|---|
| ... | authors / external source / analysis | p. N, Fig./Table/Section X or exact URL | direct / partial / unsupported / unverified | definition, condition, denominator, or caveat |

Keep most locators here so the main explanation remains easy to read. Repeat a locator in the main body only when it is central to the conclusion.
