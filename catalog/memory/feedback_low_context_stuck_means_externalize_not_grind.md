---
name: feedback_low_context_stuck_means_externalize_not_grind
description: "Being stuck while LOW ON CONTEXT is usually caused by the low context, not the problem — you can't hold enough structure to see the reformulation/reuse. The move is externalize + genericize + hand off, NOT grind more of the same."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Distinct from the difficulty-over-estimate class ([[feedback_probe_wall_try_alternate_encoding]]): that
one is "I tried one FORM and declared it hard." This one is "I keep circling the SAME derivation across
turns, and the real cause is that I'm out of context to hold the structure that contains the answer."

**Caught 2026-07-10 (⟡rig-UP-mul / fold-⊗, the graded-Lehmer-rig arc).** I circled fold-⊗ for
multiple turns — attempting it as a fold-recursion (like fold-⊕), each time hitting the ⊕/⊗ carrier
asymmetry. The USER diagnosed it: "You're running out of context to work with, and that's why you're
stuck. Right now is a good time to run the deduplication machinery with the typeholer, aggressively
genericizing and parameterizing common structure — that will make finding required shapes much easier,
because it will make reusing existing latent structure much easier." Exactly right: with low context I
couldn't hold the ⊕/⊗-generic structure whose instantiation IS fold-⊗; grinding produced nothing, and
a genericization pass (or handoff to a fresh session) would have made the shape a LOOKUP, not a
derivation.

**Why:** stuckness has two very different causes and they demand opposite responses. If the PROBLEM is
hard, grind/reformulate. If your CONTEXT is exhausted, grinding just burns the little you have left on
re-deriving what you can no longer hold — and each turn you have LESS. The tell: you're re-attempting
variations of the same thing across turns without new information; you can't recall the exact shape of a
module you built earlier; you're re-reading things you already read.

**How to apply:** when stuck, FIRST ask "is the problem hard, or am I low on context?" If low on context:
(1) STOP grinding; (2) run the dedup/typeholer to genericize+parameterize the latent structure (turns
derivations into lookups); (3) externalize the precise plan to the durable ledger; (4) hand off / clean
checkpoint for a fresh session — the reformulation is trivial with full context and impossible with none.
Do NOT keep attempting the derivation. Sibling of the clean-checkpoint discipline (don't commit a
stuck/partial state) — here: don't ENTER one. The right move under low context is a strategic retreat to
externalized structure, not a tactical push.
