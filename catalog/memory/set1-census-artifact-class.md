---
name: set1-census-artifact-class
description: "a Set₁ census count is an ANNOTATION claim (stale lsuc · alias head · unpaid referenced record); the 2-minute spelled-vs-reduced scratch probe is the decisive instrument — probe before classifying any orbit as floor; there is no floor, only unprobed walls"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

A def counted by the Set₁ ratchet is not necessarily "really" Set₁ — the count reads the
ANNOTATION, and the annotation can overstate the level in exactly three ways:

1. **Stale `lsuc`** — the record's level kept a successor its fields no longer force
   (CentralizerDescent, PFG, Monad/Comonad/Limit/KanExtension/Sheaf in the categoryof sweep).
   Move: drop it; the typechecker arbitrates.
2. **Alias head** — `X : Fam A` counts level 1 while the definitionally-equal `X : A → Set`
   counts 0, because the census does NOT δ-reduce alias heads (probe-verified 2026-07-16:
   a 6-line scratch module with `X-spelled : Fam ⊤` vs `X-reduced : ⊤ → Set` showed
   level 1 vs 0). Move: respell the use-site signatures; keep the alias for binders.
3. **Record-valued def over an unpaid record** — the def drops derivatively when the record
   it inhabits is paid down (parameterize its Set-valued fields; the vestigial-record form —
   ALL obligations as params, empty body — works even for ∀-over-families fields, since
   params never raise the sort: UPArrowP/mkUP, Refinement, Cell/Realizability).

**Why:** every "documented-immovable / genuine floor / legitimately-large" label the user
audited this arc collapsed under one of these moves once probed ('legitimate-large' →
'documented-immovable' → 'genuine floor' — three recurrences of the wall reflex at the
census-classification layer; the labels had been INHERITED from prior reports without
re-probing). User, verbatim: "There's no such thing as a genuine floor on this topic."

**reparam-record-net-zero (a build-taught corollary).** Reparameterizing a RECORD's carrier to a param pays
down only when the INSTANCES stop holding the carrier at Set₁ — moving the objects to a Set₀ universe AND
ensuring the morphisms are Set₀. The record reparam ALONE is a structural enabler, net-zero on the ratchet:
Set-Category dropped only once its Obj ranged over a Set₀ Tarski `data U`+`El` (not raw `Set`), and Rel-Allegory
did NOT drop even over U, because a relation `A→B→Set` is a proof-relevant Set₁-valued MORPHISM (Hom itself is
Set₁) — dissolving that needs relations valued in the code universe, a real re-valuation. Always MEASURE the
ratchet after a record reparam; don't assert −N.

**How to apply:** before classifying any Set₁ orbit as floor, run the 2-minute probe —
write a scratch module with the spelled and the reduced form of the def's type, typecheck,
read the two defmark levels from the core. Classify by MEASURED level, not by prose labels.
The standard moves (drop / respell / pay down the referent / parameterize the carrier /
vestigial record) cover every case observed across 298→207.

Relates to [[set1-carrier-always-parameterize]], [[set1-is-grade-collapse]],
[[level-poly-record-is-set1-paydown]], [[declaring-wall-rebuild-reflex]],
[[feedback_measure_instrument_before_theorize]].
