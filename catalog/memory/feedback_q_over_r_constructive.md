---
name: feedback-q-over-r-constructive
description: "When a numeric carrier is needed beyond F₂, prefer ℚ over ℝ. ℚ retains the rational decision structure (numerator/denominator, decidable equality, finite construction) that ℝ collapses; ℚ → ℝ is the forgetful functor."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

When the substrate needs a richer numeric carrier than F₂, **default to ℚ, not ℝ**. The user's framing: "imagine having your decision structure encoded in every number" — ℚ's rationals carry their (numerator, denominator) decomposition explicitly, with decidable equality / comparison / operations; ℝ collapses that into a Dedekind-cut / Cauchy-sequence object that erases the construction.

**Why:** this is the same gauge-honesty discipline applied to numeric carriers as [[feedback-ordering-is-chirality-choice]] is to indexings and [[feedback-multi-reading-ambient-discipline]] is to definitions. Constructive ℚ preserves the decision structure that intuitionistic / decidable proofs require; ℝ throws it away and forces classical reasoning. The transition ℚ → ℝ is a **forgetful functor** (loses rational decomposition); the reverse direction is approximation, not a faithful lift.

**How to apply:**
- When a fragment / arc grows beyond F₂ and needs richer numerics (e.g., distributional semantics needing continuous-valued vectors), reach for ℚ before ℝ.
- Frame any ℚ → ℝ migration as a deliberate adjunction (forgetful + free), not a "richer" replacement.
- Treat ℝ as a place where continuity itself is the load-bearing structure — not as the default.
- Per [[feedback-continuous-via-discrete-inference-rules]]: even when ℝ becomes necessary as content, the discrete constructive inference rules that build it are in-scope. ℚ is one step up from F₂ on that ladder; ℝ is two steps up and across a categorical boundary.

Related arc: the planned Toki Pona linear-side arc ([[project-linguistic-rosetta-arc]]) uses F₂ for the fragment; any future generalisation would target ℚ-modules before considering ℝ-modules.
