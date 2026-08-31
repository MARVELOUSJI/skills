---
name: paper-analyzer
description: "Deep, source-grounded analysis of a specific academic paper from a local PDF, full-text URL, arXiv ID, or optional NotebookLM notebook. Use whenever the user wants to understand a paper beyond a summary: motivation and prior limitations, task/setting, architecture and end-to-end data flow, module-by-module implementation mechanisms, model inputs/outputs, training data/stages/losses, what each experiment tests, metric meanings, figure/table-by-figure interpretation, contribution/novelty, exact page/table/figure-level evidence, claim-evidence gaps, reproducibility, or research-hypothesis mapping. Supports direct reading (default), NotebookLM assistance, and dual verification. Triggers include 'analyze/deep dive/critical read this paper', 'explain how every module works', 'explain the architecture and training', 'what does each experiment prove', 'walk through every figure and table', 'is this paper really novel', '分析这篇论文', '论文深度分析', '逐模块讲清楚实现机制', '网络输入输出和 loss 是什么', '每个实验验证什么', '逐图逐表解释', '这篇论文到底说明了什么', or a PDF/URL/arXiv ID with analysis intent. NOT for paper discovery/filtering (use scholar-agent), quick summaries, broad multi-paper literature surveys, formal journal-style referee reports when a reviewer workflow is available, citation formatting, or merely adding sources to NotebookLM."
---

# Paper Analyzer

Analyze one paper through three passes: orient first, understand the paper through the reader's questions, then audit whether the evidence supports the claims. The goal is a concise and understandable explanation of what the paper solves, how it works, what its experiments establish, and where the evidence stops.

## Operating Principles

- Follow the user's reading backbone: **Motivation → Task/Setting → Method → Experiments → Contribution/Novelty**.
- Keep source retrieval separate from interpretation. The original paper is the authority; generated retrieval is only an aid.
- Prefer a short, layered answer. Put the conclusion first and evidence details later.
- Let detail follow the paper's complexity and the reader's understanding needs. Keep routine background compact, but explain the method until the reader can trace how the complete system works; do not target a fixed Method length.
- Distinguish what the authors claim, what the experiments demonstrate, and what you infer.
- Do not force every paper into the same critique. Apply only checks that matter for the paper type and the user's goal.

## Step 1: Set Reading Depth and Obtain the Source

Infer the reading goal from the request instead of asking routinely:

- **Orientation**: use only when the user explicitly asks for a quick understanding or invokes this skill for a short read.
- **Standard deep read**: default for analysis requests.
- **Reproduction/review audit**: use when the user asks to reproduce, review, verify, challenge, or assess reliability.

Accept a local PDF, full PDF/HTML URL, arXiv ID, DOI/publisher page with full text, or an existing NotebookLM source. An abstract or metadata page is enough for orientation but not for a definitive deep analysis. If full text remains unavailable, state the limitation and mark substantive conclusions **unverified**. Do not imitate a full deep-read report: give only a provisional paper map (normally no more than six bullets) and a short list of the evidence still needed.

Use **Direct reading** by default. For local PDFs, extract text and inspect rendered pages when layout, equations, tables, or figures carry evidence. Use NotebookLM only when requested, when an existing notebook is supplied, or when persistent retrieval over long sources is useful. Use both channels for explicit cross-checks or difficult tables/appendices. Never upload unpublished, private, or proprietary material to a third party without explicit permission.

Preserve the exact paper version supplied by the user. If another version is found, report the difference rather than silently replacing it. Read `references/source-backends.md` only when NotebookLM, source acquisition, or version conflicts require operational detail.

## Step 2: Pass One — Build the Paper Map

Scan the title, abstract, introduction, conclusion, section headings, figures/tables, and references before reading linearly. This pass prevents early details from hiding the paper's main logic.

Determine:

1. **Paper type**: method, empirical study, theory, benchmark/dataset, system, review, or position paper.
2. **Research question**: what the authors want to know or change.
3. **Headline claim**: the main claim in one plain-language sentence.
4. **Evidence map**: which figures, tables, proofs, or studies appear to support that claim.
5. **Reading priority**: which sections need close inspection for the user's goal.

Treat the abstract as the authors' proposed story, not as verified evidence.

## Step 3: Pass Two — Understand the Paper Through the Reader's Backbone

### 3.1 Motivation

Explain the chain **important problem → prior limitation or missing study → opportunity addressed here**.

- Separate importance from novelty: an important problem is not automatically new.
- Identify whether the gap is a capability limit, assumption, missing setting, weak evidence, efficiency issue, or unexplored question.
- Check whether the paper supports its account of prior limitations with appropriate related work. Do not repeat a vague “few studies exist” claim as fact.

### 3.2 Task and Setting

Create a compact Setting Card containing only relevant fields:

- research task or question;
- inputs, outputs, intervention, or system boundary, including modality and shape/representation when informative;
- data/population/environment, source and scale, preprocessing/augmentation, and train-validation-test split when applicable;
- supervision, assumptions, constraints, and allowed information;
- baselines/comparators, metrics, and evaluation protocol.

Setting details define what the results mean. Compare results only when the underlying settings are genuinely comparable.

### 3.3 Method

Explain the method as **overall flow → component mechanisms → component interactions → training/inference behavior**. For each design, retain the link **problem → design choice → mechanism → expected effect** so the explanation says both how it works and why it exists.

- Start with the central idea before components, formulas, or implementation details.
- Inventory the method-defining modules and stages from the method text, architecture figures, algorithms, and training/inference descriptions before drafting. Include side branches, fusion paths, memories, controllers, and post-processing that affect the output. Explain repeated instances of the same block once, then state where and how often the block is reused.
- Trace one representative input through the complete method or system, from its original representation to the final output. Name intermediate representations and important shape changes when the paper reports them or they are needed to understand the mechanism.
- For every method-defining module or stage, explain its input, internal operation, output, connection to the next module, and functional role. State which parts are learned, frozen, rule-based, iterative, or shared when relevant.
- Do not treat a module name such as “Transformer block,” “adapter,” or “fusion layer” as an explanation. Open the block and describe the operations that materially define its behavior.
- Include equations, update rules, or pseudocode that define a transformation, routing/attention rule, state update, objective, or inference procedure. Explain the variables, computation order, and operational meaning; omit routine derivations that do not improve understanding.
- Use architecture and algorithm figures as maps: walk through their blocks and arrows in data-flow order, then connect them to the relevant text and equations.
- Separate genuine conceptual changes from combinations, scaling, engineering, or presentation choices.

Treat a module or stage as method-defining when it appears in the system pipeline, changes the representation or state, implements a claimed contribution, has its own objective/training stage, or affects inference. Use this comprehension test instead of a word-count target: after reading the Method section, the reader should be able to explain what enters each method-defining module, what transformation occurs, what leaves it, how modules connect, and how training and inference use the system. A simple method may need only a few paragraphs; a multi-stage system may require a longer walkthrough.

For learned methods and system papers, build an adaptive **Method and Training Walkthrough** with the applicable fields:

- architecture or system decomposition, including important backbones, modules, frozen/trainable parts, and information flow;
- model input and output, including modality, representation, tensor shape, prediction target, or control signal when reported and informative;
- end-to-end data flow: how raw input becomes the final output and where each proposed component acts;
- module mechanisms: the actual computation, algorithm, message exchange, state transition, or control logic inside each method-defining component, plus its output and downstream consumer;
- objectives and losses: each term's role, weighting, and schedule; explain what behavior it encourages rather than listing symbols only;
- training stages: pretraining, warm-up, stage-wise optimization, fine-tuning, distillation, or joint training, including what changes between stages;
- training data: source, scale, split, supervision, filtering, preprocessing, and augmentation;
- training-versus-inference behavior: which inputs, states, branches, objectives, or iterative steps differ, including decoding, sampling, test-time processing, or control loops;
- optimization and execution details that affect interpretation: optimizer, learning-rate schedule, batch size, stopping rule, seeds, compute, and checkpoint selection. In a standard deep read, expand these only when they affect the mechanism, fairness, or conclusion; cover them systematically for reproduction/review requests.

Do not invent missing details. Mark important fields as **not reported** or **unclear**, because missing architecture, objective, data, or stage information is itself a reproducibility finding. Distinguish paper-reported implementation from your explanatory analogy or inference. For non-learning papers, adapt the walkthrough to the equivalent algorithm, system, intervention, study design, or proof pipeline instead of forcing neural-network terminology.

### 3.4 Experiments

Read claim-bearing figures and tables closely. Inspect axes, units, denominators, comparison conditions, uncertainty, captions, and the methods needed to interpret them.

For each distinct main-text experiment, assign an ID such as `E1` and record:

**question/hypothesis → what was done → comparison and controlled variables → data/split → metric meaning → result → authors' interpretation → actual support and rigor → evidence locator**

For every metric needed to interpret a result, state what it measures, whether higher or lower is better, its unit/scale and denominator or aggregation, and any important limitation. Define a repeated metric once in its first row or a compact glossary, then reuse the name. Give full rows to experiments that support headline contributions and compact rows to supporting main-text experiments. Repeated datasets, seeds, or variants that test the same hypothesis may share a row, but name every condition and do not hide a result that tests a different claim. Expand appendix experiments when they change a conclusion, expose a limitation, matter for reproduction, or the user requests exhaustive coverage.

For non-empirical papers, replace the experiment matrix with the closest evidence structure: **claim/theorem → assumptions → proof or argument → evidence/example → boundary or counterexample** for theory, and **position/claim → cited evidence → counterevidence → support level** for review or position papers. Do not force metrics, losses, or experiments where they do not apply.

Use the experiment matrix in `references/analysis-template.md`. A result table without the question each experiment tests is incomplete.

### 3.5 Figures and Tables

Create a compact **Figure/Table Ledger** after the experiment analysis:

- Standard deep read: cover every main-text figure and table once, including architecture diagrams, qualitative examples, ablations, and failure cases.
- Reproduction/review audit: also cover appendix figures and tables that contain methodological or experimental evidence.
- Explicit “逐图逐表 / every figure and table” request: cover all main-text and appendix items without omission.

For each item, state what it contains, how to read it, the message the authors intend, what it actually supports, and any material caveat. Keep the ledger compact. Quantitative settings and results belong in the experiment matrix; the ledger should reference the related `E#` row rather than duplicating numbers. Use it especially to explain architecture diagrams, qualitative examples, visual failure cases, and how multiple panels fit together.

## Step 4: Pass Three — Audit Claims and Evidence

### 4.1 Claim–Evidence Check

For every headline claim, decide whether the paper provides:

- **direct support**: the design and evidence test the stated claim;
- **partial support**: the evidence supports a narrower claim;
- **unsupported interpretation**: the conclusion exceeds the evidence;
- **unverified**: the source or required detail could not be located.

Actively look for reasonable alternative explanations. For causal language, ask whether the design isolates the proposed cause rather than showing correlation only.

### 4.2 Contribution and Novelty

Report novelty at three distinct levels:

1. **Author-claimed novelty**: what the paper says is new.
2. **Internally demonstrated contribution**: what the paper's own analysis or experiments substantiate.
3. **Externally verified novelty**: what remains new after comparison with relevant prior work.

A single paper cannot establish field-wide novelty by itself. Do not label novelty “externally verified” unless an external literature comparison was performed. If the user asks whether the work is *really* novel, search primary papers and official proceedings; use metadata or citation services for discovery, not as final evidence.

Classify the contribution when useful: problem/setting, method/mechanism, empirical finding, theory, dataset/benchmark, system, or engineering integration.

### 4.3 Critical Audit

Check only applicable risks: construct validity, causal attribution/confounders, statistical reliability, generalization, baseline fairness, missing ablations, and reproducibility. For AI/ML/robotics papers, use the domain-specific additions in `references/critical-audit.md`.

Lead with the one or two issues that could change the conclusion. Do not pad the answer with generic limitations.

## Output Contract

Answer in the user's language. Default to a concise main answer with progressive detail.

Start with **极简结论 / Executive takeaways**, using one short sentence for each applicable item:

- Motivation
- Task
- Method
- Core result
- Contribution/novelty
- Main limitation

For a standard deep read, use this order:

1. Motivation
2. Task/Setting
3. Method, architecture, and training
4. Experiments and what each verifies
5. Figure/Table Ledger
6. Contribution and novelty
7. Critical audit
8. Evidence appendix
9. Research mapping or cross-paper connections, only when requested/configured

Follow these writing constraints:

- Put the conclusion before the derivation.
- Use short sentences and one main point per paragraph or bullet.
- Keep motivation, contribution, and limitations compact by default. Size Method and Experiments by the paper's actual complexity and the user's goal: stop when the mechanism and evidence are understandable, not at a preset bullet or word count.
- Explain a technical term in plain language before giving the paper's term in parentheses.
- Expand unfamiliar abbreviations on first use. Do not explain universally understood terms to an expert audience.
- Prefer “what enters, what operation happens, what exits, why the component exists, and what the experiment shows” over unexplained formulas or raw implementation dumps.
- Explicitly signal **authors' claim**, **experimental support**, and **analysis/inference** when they differ.
- Keep full numeric evidence in the evidence appendix unless a number is essential to the main conclusion or experiment matrix. Method, experiment, and figure/table locators may stay with their rows for easy verification. The evidence appendix is conditional: omit it entirely when all headline evidence already has complete locators elsewhere, and never repeat entries already complete in a matrix or ledger.
- Use tables for structured comparisons such as the Setting Card or experiment matrix, not for simple prose.
- Avoid repeating background, section-by-section summaries, and low-value details. Expand only the part the user asks about.
- For a complex method, use a numbered end-to-end flow and a compact module map when they make interactions easier to follow. For a simple method, cohesive prose is sufficient; do not force a table merely to look complete.

When the user asks about only one part, let that part replace the full report. Give only the minimum context needed, analyze the requested part at the necessary depth, and add at most three synthesis/audit bullets. Omit unrequested novelty, research mapping, and evidence appendix; do not repeat evidence that already has locators in the main matrix. For abstract-only input, omit the full Setting Card, Method and Training Walkthrough, experiment matrix, critical audit, and evidence ledger unless the user explicitly asks for them.

Use `references/analysis-template.md` for the full report template and compact evidence ledger.

## Source-Grounding Contract

- Attach a locator to every headline number and capability claim: PDF page plus section/table/figure, or exact full-text URL plus heading/figure.
- Re-open the original page for headline numbers, denominators, comparison conditions, and experimental settings. Do not rely on generated retrieval alone.
- Record the paper version/date when versions may differ.
- Label source-reported facts, external evidence, and your own inference clearly.
- If evidence cannot be located, mark it **unverified** and exclude it from definitive conclusions.
- Treat peer-reviewed papers, preprints, project pages, blogs, and demos as different evidence types.

## Optional Modules

These modules supplement the reader's backbone; they do not replace it.

- **Causal chain**: Use for diagnostic or causal papers, or when requested. Summarize phenomenon → setup → attribution → solution, then check whether each link follows.
- **Taxonomy tagging**: If `references/taxonomy.md` exists, read it and add the configured tag. Otherwise skip it. See `references/taxonomy.example.md`.
- **Research framework mapping**: If `references/hypothesis.md` exists or the user provides a framework, map the paper as support, challenge, or boundary condition. Otherwise skip it. See `references/hypothesis.example.md`.
- **Cross-paper connections**: Add only when the user is building related work or provides comparison papers. Separate genuine contradiction from differences in setup.

Optional modules belong after the complete standalone paper analysis so that a pre-existing framework does not distort the reading of the paper.
