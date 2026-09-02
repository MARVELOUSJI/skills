# Paper Analysis Template

Use this template for a standard deep read. Translate headings into the user's language. Omit empty or irrelevant fields. Keep routine material concise, but let method detail scale with the actual method until its mechanisms and connections are understandable.

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

## 4. Method, Architecture, and Training

Explain the central idea first, then trace one representative input through the complete system in computation order:

`raw input → representation/preprocessing → module or stage 1 → ... → final output`

Name intermediate representations and important shape changes when reported or necessary for understanding. For an iterative method, show one update and explain how it repeats. For a control or interactive system, show the observation–decision–action–feedback loop.

Before drafting, inventory modules and stages from the method text, architecture figures, algorithms, and training/inference descriptions. Include branches and post-processing that affect the output. A method-defining item is one that changes representation/state, implements a claimed contribution, has separate training, or affects inference. Explain a repeated block once and state where it is reused rather than duplicating identical descriptions.

For a multi-module system, first give a compact index. It is a navigation aid, not the explanation itself:

| Module / stage | Local bottleneck and motivation | Input → output / connection | Implementation form | Evidence locator |
|---|---|---|---|---|
| ... | problem at this point; why the item is introduced | representation/state change and next consumer | architecture block / iterative algorithm / rule / objective | p. N, Sec./Fig./Eq./Alg. X |

Then explain every indexed item in pipeline order. For a complex item, use this close-up structure; for a simple item, cover the same fields in cohesive prose:

### Component or algorithm: name — one-line purpose

- **Local motivation:** the specific limitation or bottleneck here, why this item is introduced, and whether that rationale is author-stated or analysis/inference.
- **Architecture or algorithm flow:** for a module, list sublayers/operators, branches, merge points, residual/normalization/activation, sharing, and important dimensions in execution order; for an algorithm, list initialization, maintained state, ordered updates, decision rule, loop/stopping condition, and returned result.
- **Data/state walkthrough:** exact input → each material transformation or update → exact output. Align equations and pseudocode with the step they implement and explain the variables operationally.
- **Connections:** upstream producer, downstream consumer, side-path re-entry, and dependencies on other modules or stages.
- **Learning and use:** learned/frozen/fixed/shared parts, the objective or signal that trains or updates them, and training-versus-inference behavior.
- **Intended effect and evidence boundary:** what behavior the design should create or failure it should avoid; do not call it necessary or causal without isolating evidence.
- **Source status:** paper/appendix locator; **not reported** or **unclear** for missing details; code-grounded facts separated from paper-reported facts.

A component name is not a mechanism description. Explain what happens inside blocks such as attention, fusion, adapter, memory, planner, or decoder when those internals affect the paper's contribution or data flow. A table cell saying only “uses attention” or “reduces noise” is incomplete. Connect architecture-figure blocks and arrows to the text and mechanism-defining equations.

Use this cross-component rationale table only when it helps compare several design choices; it does not replace the per-component motivation and implementation walkthrough:

| Problem or limitation | Design choice | Why it should work | Dependency or assumption |
|---|---|---|---|
| ... | ... | ... | ... |

Add the applicable implementation details. Write **not reported** rather than guessing. Do not infer hidden tensor shapes, module internals, or training stages from convention. In standard deep reads, keep routine optimization and compute compact unless they affect the mechanism, comparison fairness, or conclusion; expand them for reproduction/review audits.

The module map and the following aspect list are collection aids, not two mandatory duplicate tables. In the final answer, use the clearest representation and avoid restating the same mechanism twice.

| Aspect | What to record |
|---|---|
| Architecture / system | Backbone, modules, connections, frozen/trainable/shared parts, and information flow |
| Input | Modality, representation, tensor shape, context, or intervention |
| Output | Prediction target, generated object, state estimate, action, or measured outcome |
| End-to-end data flow | Each transformation and intermediate representation from input to output; where every proposed component acts |
| Module internals | Computation, update rule, message exchange, memory/state change, control logic, or algorithm steps inside each method-defining component |
| Objectives / losses | Formula or term, role, weight, schedule, and intended behavior |
| Training stages | Stage order, initialization/checkpoint, trainable parts, data, objective, and transition between stages |
| Training data | Source, scale, supervision, split, filtering, preprocessing, and augmentation |
| Optimization | Optimizer, learning-rate schedule, batch size, epochs/steps, stopping rule, seeds, compute, and checkpoint selection |
| Training vs. inference | What inputs, branches, state updates, objectives, or iterative steps differ between learning and use |
| Inference / deployment | Decoding, sampling, test-time processing, stopping condition, control loop, latency, or deployment constraints |

Use equations or pseudocode when they define a transformation, routing rule, state update, objective, or inference procedure. Explain symbols and computation order in plain language; skip derivations that do not change how the method is understood.

Before moving to Experiments, apply this comprehension check:

1. Can the reader trace a representative input to the final output?
2. Can the reader explain the local problem and motivation for every method-defining module or algorithm?
3. Can the reader redraw the reported architecture or restate the algorithm as ordered steps without hiding work behind a block name?
4. Can the reader say what enters, changes internally, and exits every method-defining item?
5. Are module interactions, side branches, intermediate representations, state updates, and stopping conditions clear?
6. Are the loss terms and training stages connected to the components they train?
7. Is the difference between training and inference clear?

The required length is whatever satisfies the applicable questions. Do not lengthen a simple method or compress a complex system to fit a fixed format.

## 5. Experiment–Claim Matrix

Each main row should answer what the experiment was designed to establish, not merely repeat its result.

| ID / experiment question or hypothesis | What was done; comparison and controls | Data / split | Metric meaning | Key result | Authors' interpretation | Actual support / rigor | Evidence locator |
|---|---|---|---|---|---|---|---|
| E1 — ... | ... | ... | define direction, unit, denominator, aggregation, and caveat | ... | ... | direct / partial / unsupported / unverified; key confounder | p. N, Fig./Table/Section X |

Guidelines:

- Give separate rows to the main result, ablations, robustness/generalization, efficiency, and diagnostic/causal tests when they support different claims.
- Cover every distinct main-text experiment. Use compact rows for supporting experiments rather than omitting them.
- State whether comparisons use the same data, checkpoint, training budget, tuning budget, and evaluation protocol when relevant.
- Explain what each metric measures, whether higher or lower is better, its unit/scale, denominator or aggregation, and important failure modes before interpreting it. Define repeated metrics once in the first relevant row or a compact glossary.
- Repeated datasets, seeds, or variants that test the same hypothesis may share a row, but name every condition. Keep separate rows when the hypothesis, controlled variable, or conclusion changes.
- For theory, review, or position papers, replace this matrix with the applicable claim–assumption–proof/evidence–boundary structure instead of inventing experiments or metrics.

## 6. Figure/Table Ledger

Cover every main-text figure and table once. Include appendix items for reproduction/review audits or explicit exhaustive requests.

| Item | Related method / experiment | What it contains / how to read it | Intended message | Actual support and caveat | Evidence locator |
|---|---|---|---|---|---|
| Fig./Table X | Method Walkthrough or E1 | axes, panels, rows/columns, conditions, or qualitative examples | what the authors want it to show | what follows, what does not, and any ambiguity | p. N, caption/section |

Cross-reference the experiment matrix instead of repeating settings or numbers. Use this ledger to explain architecture/data-flow diagrams, panel relationships, qualitative examples, and failure cases; identify whether examples appear representative or selectively chosen.

## 7. Contribution and Novelty

| Level | Finding |
|---|---|
| Author-claimed novelty | What the authors say is new |
| Internally demonstrated contribution | What the paper's own evidence substantiates |
| Externally verified novelty | Result of comparison with primary prior work, or “not checked” |

Classify contributions when useful: problem/setting, method/mechanism, empirical finding, theory, dataset/benchmark, system, or engineering integration.

## 8. Critical Audit

Report only material issues:

1. The strongest part of the evidence.
2. The main gap between claim and evidence.
3. The most plausible alternative explanation.
4. The boundary beyond which the result should not be generalized.
5. The missing information that most affects reproducibility.

## 9. Evidence Appendix

Use this section only for headline claims or numbers not already fully located in the Setting Card, Method Walkthrough, experiment matrix, or Figure/Table Ledger. Omit the section when it would only repeat earlier evidence.

| Claim or number | Voice | Evidence locator | Status | Note |
|---|---|---|---|---|
| ... | authors / external source / analysis | p. N, Fig./Table/Section X or exact URL | direct / partial / unsupported / unverified | definition, condition, denominator, or caveat |

Keep most locators here so the main explanation remains easy to read. Omit entries already fully captured in a matrix or ledger, and repeat a locator in the main body only when it is central to the conclusion.
