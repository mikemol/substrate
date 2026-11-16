---
name: feedback_read_structure_dont_rebuild
description: "READ structure that's already present (in data / a tool / a lossless rep); don't flatten, reimplement, or re-derive it — the dual of collapse-to-smallest. Caught ≈9× one session."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The recurring reflex (≈9× in one session, each caught only by a user correction): the structure is **already present** — in the data, in an existing tool, or in a lossless representation — and I default to **flattening / reimplementing / re-deriving** it instead of **reading/using** it. Three instances of one move:

- **collapse** a graded relation to a scalar / bit / finest-quotient when the graded relation is right there ([[feedback_dont_collapse_to_smallest_representable]]);
- **reimplement** a tool's core with raw data-SVD + per-mode-argmax when the tool already reads boilerplate-robust **group-invariants** (eliza: route a token-stream into the FIXED S₄/V₄⋊S₃ geometry and read the orbit / irrep-block, which is robust to a dominant boilerplate mode — do NOT SVD the corpus and argmax raw modes);
- **re-derive** a lossless structure (Sequitur's grammar is an SPPF, lossless — read its own depth-14 rule-nesting + fan-in; don't extract phrases and re-align them flat, which collapses the hierarchy to depth-1).

**Why:** rebuilding discards what the existing structure already encodes — the graded relation becomes noise, the tool's boilerplate-robustness reappears as the dominant-mode artifact, the lossless hierarchy flattens to depth-1. The structure IS the residue; flattening/rebuilding is the same loss as discarding it. This is the dual of [[feedback_dont_collapse_to_smallest_representable]] (and the read-side of never-discard-residue): collapse is "flatten the relation," this is "flatten/rebuild any given structure."

**How to apply:** before collapsing a relation to a number, reimplementing a mechanism, or re-deriving what's already computed — ask *is this structure already present (in the data / a tool / a lossless rep)?* If yes, READ it: keep it a truncatable graded curve, conform to the tool and read its invariants, read the lossless form's own nesting. Escalated into the [[construct-dont-classify]] skill as meta-substitution #5 (rebuild-vs-read / flatten-the-given), the dual of #1 classify-vs-construct.
