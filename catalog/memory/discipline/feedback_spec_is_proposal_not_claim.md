---
name: feedback-spec-is-proposal-not-claim
description: "Prose in code is suspect (default-distrust, zero proof-weight); a spec/docstring/plan is a PROPOSAL awaiting a witness, not a CLAIM of truth."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

Two epistemic disciplines from the user:

1. **Prose in code is suspect.** Comments/docstrings/prose carry zero proof-weight. The burden flips to default-distrust: treat any prose framing as unverified until the surrounding code (or a machine-checked witness) actually backs it. Sharpens [[feedback-comments-dont-overclaim]] (which says "don't overclaim") into "assume the prose overclaims until shown otherwise."

2. **A spec is a proposal, not a claim.** A spec / plan / scratch design asserts an *intention to be satisfied*, NOT a *truth that holds*. It proposes; it does not assert. This is exactly the v4cat stance: a spec is a witness OBJECT a domain extension introduces, and it becomes a CLAIM only once `witness` ties it to a break. Until something machine-checks it, a spec is a hypothesis on the table.

**Why:** in this project, LLM-authored prose and aspirational specs are the main vector for stale/false claims slipping into the substrate (see [[feedback-negative-findings-in-corpus]], [[feedback-silo-sprawl-orphans-fixes]]). Distinguishing proposal-status from claim-status keeps the proof-discipline honest.

**How to apply:**
- When reading a comment/spec, ask "is this witnessed, or proposed?" Don't cite a proposal as if it were established.
- When writing a scratch plan or spec (e.g. the untracked `scratch/*_plan.md`), frame it as a proposal — what you intend to discharge — not as a description of what is true.
- A spec earns claim-status only when a witness (proof, passing check, v4cat `witness` edge) is attached.
