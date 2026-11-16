---
name: section-then-lemma-for-parametric
description: "Parametric modules decompose by section FIRST (sub-modules sharing the parameter set), then file-per-lemma within sections. Direct file-per-lemma on a parametric module multiplies parameter-forwarding boilerplate."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

When a monolithic Agda file is a **parametric module** (8+ module parameters bound at the top), do not jump straight to file-per-lemma. The forwarding boilerplate would dominate each leaf and make the decomposition harder to read than the monolith.

Instead, decompose in two passes:

1. **Section first.** Each numbered section (or thematic group) of the parametric module becomes its own parametric sub-module, taking only the parameters it actually consumes. The parent module instantiates each section with its own parameter set and re-exports `public`.
2. **File-per-lemma within sections.** For sections with multiple lemmas of similar shape — especially inductive ladders like `triple / quad / quint / sext / sept` — split each lemma into its own file in a per-section subdirectory. The section file becomes a thin aggregator re-exporting the leaves.

**Why:** The similarity checker (`scripts/agda_similarity.py --skeleton --typed-holes`) needs uniform structure visible at the file boundary to surface candidate quotients. Inductive ladders of the form `step n+1 = base-op a + cong (step n)` become visible as 5 sibling files with identical skeletons; the script can then propose a parametric combinator. Bundled in a monolith, the same structure is hidden inside section comments.

**How to apply:**
- Identify whether the file declares a parametric module (`module M (... params ...) where`).
- If yes, find the section structure first (numbered headers, thematic groupings); decompose by section. Each section sub-module imports the prior sections it needs and re-passes the parameters.
- Then, within each multi-lemma section, split file-per-lemma. Section aggregator files re-export leaves with `public`.
- If only one lemma per section, leave the section file as the leaf — no further split required.

Concrete example: `Substrate.Groups.Coxeter.Core` (commit 559f28f) — 209-line monolith → 76-line shim + 8 section files + 7 leaf files. `HigherArity` ladder of 5 uniformly-shaped lemmas is the prime similarity-checker target.

See also: [[feedback-composable-primitives-over-flat-enumeration]] (the same discipline at the algebra layer), [[feedback-skeleton-as-pullback]] (similarity-skeleton mechanics).
