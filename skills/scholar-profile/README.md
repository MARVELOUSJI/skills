# scholar-profile

Get to know a scholar **fast and without hallucination**, and grow a **global
interactive relationship graph** across everyone you've ever asked about.

Invoke: `/scholar-profile <name> [affiliation/field to disambiguate]`
e.g. `/scholar-profile Yann LeCun`, `/scholar-profile 李飞飞 Stanford`.

## What you get

A four-part profile (`~/.config/scholar-profile/profiles/<slug>.md`):

1. **Career timeline** — chronological milestones, with links to their personal
   homepage and public CV (flagged if none found).
2. **Relationships (the focus)** — advisor (1 hop up), students & grand-students
   (2 hops down), notable direct collaborators. Each tie cites a source.
3. **Research & landmark work** — driven by their Google Scholar (areas,
   representative papers, citations, h-index), every claim cited.
4. **Evaluation** — what tier they are, by hard metrics (awards, citations,
   chairs), plus an explicitly-labelled cross-field analogy for intuition.

Plus the person is merged into a global graph
(`~/.config/scholar-profile/viewer.html`) — a single self-contained HTML with
**zero external dependencies** (no CDN, works offline / behind a firewall /
from file://). Open it in a browser to drag nodes, pan, zoom, and click any
node/edge to see its backing source links. New people auto-link to people
already in the graph whenever a sourced relationship exists.

## Zero-hallucination contract

Every conclusion sentence carries a source link right after it. Anything
without a reliable source is kept but explicitly tagged `〔未找到可靠来源〕`.
Analogies/inferences are tagged `〔类比·主观〕`/`〔推断〕`. The relationship
graph only draws a solid edge when a source backs it; unverified guesses show
as dotted "inferred" candidates, never as fact.

## Storage

All state lives **outside this repo** at `~/.config/scholar-profile/`
(`graph.json` = source of truth, `viewer.html` = regenerated artifact,
`profiles/*.md` = reports). Nothing personal is committed to the skills repo.

## Dependencies

No new external deps. `scripts/graph_store.py` is **stdlib only** and the
generated graph viewer has **no CDN/library dependency**. Web fetching of
JS-heavy pages (Google Scholar) reuses the existing `web-fetcher` skill;
proxy is taken from the environment (port 7897), never hardcoded.

## Not for

Reading/summarizing papers or the daily Scholar Inbox digest (→ `scholar-agent`);
just turning one URL into markdown (→ `web-fetcher`); literature reviews;
biographies of non-academics.
