---
name: feedback_unsolved_constraints_use_numpy
description: "An Agda 'unsolved constraints'/'unsolved metas' error means the elaborator can't infer an index/implicit — DON'T grind it by hand. Step back and use numpy to enumerate the concrete instance, read off which index forces the stuck meta, then pin it explicitly."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (the graded-rig-CATEGORY-perm build). The user, anticipating an Agda wall:
*"When you hit an 'unsolved constraints', step back and tackle it with numpy."*

**Why:** an `unsolved constraints` / `unsolved metas` error is the elaborator saying it cannot
INFER an index (a grade `i`/`j`, a `Perm` size, a matrix dimension) — usually because a
polymorphic lambda like `(λ i → i)` doesn't PIN it. That is a search problem, not a proof
problem: what SHAPE must the term have, and which index does its value depend on? numpy answers
that mechanically — it is the same probe-don't-introspect reflex that dissolved 6+ Set₁/difficulty
over-estimates this arc, and the same fix that killed the earlier `OrientationBifunctor`
UnsolvedConstraints (pin the implicit numpy showed was required + explicit-lambda record fields).

**How to apply:** on unsolved-constraints — (1) write a tiny numpy/python script that COMPUTES the
concrete object for small indices (e.g. the block-swap `Vec (Fin (i+j)) (i+j)` swapping the first
`i` with the last `j`, for `i,j ∈ {0..3}`), verify its law numerically (`swap∘swap = id`), and read
off which index the value depends on; (2) then PIN that index in the Agda term — make the implicit
explicit, or add the type ascription numpy showed is required — instead of leaving it to inference.
numpy gives the SHAPE; you write it with indices pinned. This is distinct from the FreeUP
route-around ([[feedback_opacity_blowup_routearound_freeup]], for `opaque`/OOM) and from
reflection+membudget (for KATs/tables): unsolved-constraints is specifically an INFERENCE gap, and
enumeration is the right instrument. Sibling of [[similarity-not-grep]] and the numpy⊗typeholer
pipeline (`jea/metalanguage/numpy_law_bridge.py`). If numpy shows the object genuinely isn't
reachable (not a mere inference gap), STOP and report what's missing — don't fake it.
