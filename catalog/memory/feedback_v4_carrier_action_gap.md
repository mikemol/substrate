---
name: feedback_v4_carrier_action_gap
description: "The data{e,α,β,γ} V4-carrier ×8 is NOT a false-positive: re-audit (user-corrected) shows most are ACTING GROUPS with unstructured/vacuous group-action laws — the non-relating is a latent GAP (relate to Groups.V4 + Actionᴳ), not a distinction. Don't credulously accept 'kept local' comments."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**Ⓒ.v4 (2026-07-05): a CORRECTED audit — my first pass wrongly declared the `data|e,α,β,γ` ×8
shape-parallel a false-positive-for-collapse. The user caught two credulity errors, both instances
of accepting a module's self-description instead of verifying it (the CLAUDE.md "a comment is a
hypothesis to verify, not a fact" rule).**

The correct finding: `data V₄ = e|α|β|γ` is the 4-element CARRIER; most of the eight USE it as an
ACTING GROUP but leave the group/action structure IMPLICIT or VACUOUS — so the missing link to the
center `Groups.V4` (`V4/Bundle.V₄-Group : Group V₄`) + `Algebra.GroupAction.Actionᴳ` is a LATENT
GAP, not a legitimate distinction:

- `Pipeline.Examples.RotateCrumb.V4Label` — carries a full Klein action `v4-xor : Crumb → V4Label →
  Crumb` (= F₂²-XOR, the regular action) but its `homomorphism-tag` is an EMPTY `record Preserves-V4`
  — a vacuous placeholder exactly where the `Actionᴳ` laws (act-id, act-∙) belong. The lack of
  relating IS the bug.
- `Category.ComposedReference.V4.V₄` — its comment says "kept local … dependency-light (no group-axiom
  infrastructure needed here)", but its own Record feeds `action : ActionAlgebra`. The "no group infra
  needed" claim is a RATIONALIZATION contradicted by usage — an LLM-under-context-pressure gloss, not
  a documented reason. Do not honor an asserted-but-unverified exclusion.
- `Category.ResidueCompensation.V₄` — V₄ elements are COMPOSED (`γ_q ∘ γ_R⁻¹`) and applied to bodies:
  group semantics, structure implicit.
- `Category.RuleAction.V4.V₄` — the acting group for rule-actions (structure in RuleAction.Record).
- `Algebra.TopologicalGroup.Sites.V4` — a bare Cayley `V4-op` with NO laws (a group site missing its
  group laws); `Category.Comonoid.Sites.V4` — a comonoid via the diagonal (a genuinely different
  structure — the one that may legitimately stand apart).
- Already related: `S5.S5TorsorWireV4.KleinV4 ≅ Groups.V4.V₄` (the precedent).

**The rule this corrects.** "It's just a label/site, relating is inappropriate" and "kept local to be
dependency-light" are BOTH absence-claims that must be VERIFIED before they license leaving a gap.
An implicit action IS a group action (needs the acted-on object + the action laws); a vacuous
preservation-tag is a gap, not a distinction. Contrast the genuine false-positive
[[feedback_bijection_parallel_false_positive]] (there the differing round-trip TYPES were real and
author-documented with a reason). Here the "reasons" were unverified self-descriptions. Governed by
[[feedback_dedup_preserve_crossdomain_bridges]] + the absence-words trigger in CLAUDE.md. Gaps to
close by relating to Groups.V4 + Actionᴳ: RotateCrumb (exemplar), ComposedReference (ActionAlgebra),
ResidueCompensation, RuleAction, Sites.V4.
