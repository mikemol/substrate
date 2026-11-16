---
name: feedback_up_witness_is_constructive_solve_by_policy
description: "POLICY: a universal property's witness is the CONSTRUCTIVE solving map (solve : Spec n → Sol n = the extend/fold), NOT a proof-relevant Set-valued span (Witness : S → T → Set). The old UPArrow's relational span was flat-where-it-counts (Set₁). Consumers that rely on the relational/multi-witness reading are BUGGY and get fixed to the constructive form — not accommodated with a relational variant."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Stated 2026-07-11 while replacing `Category.UniversalProperty.UPArrow` (⟡upfamily-rewire). I
proposed asking whether the replacement UP-arrow should carry a constructive `solve` arrow or keep a
proof-relevant relational `Witness : Spec → Sol → Set`, noting "some consumers may not want" the
constructive commitment. The user: *"Yes. It's a real semantic commitment. That I require by policy."*
and *"Those consumers are buggy."*

**The policy.** A universal property's witness IS the constructive map that BUILDS the solution —
`solve : {n} → Spec n → Sol n` (the shape of `OrientationUniversal.fold : LehmerPath n → C n`, the
extend/catamorphism). It is NOT a Set-valued relation `Witness : Source → Target → Set` asserting a
solution exists. The flat `UPArrow` used the relational span, which is exactly the Set₁ cause (a
`Fam`, Set-valued) AND the ∃!-collapse the mission fights (a Σ/relation packaging an existence claim
instead of exposing the construction — [[feedback_exists-unique_is_a_construction_not_a_sigma]]). The
replacement `UPArrowᴳ (Spec Sol : ℕ → Set) : Set` with `solve` field is Set₀ (measured: 0 Set₁ added)
and is the policy-correct form.

**Why:** a UP that only PROVES a solution exists (relational witness) has collapsed the construction
to a proxy — the same thin-proxy enemy in the object language. The genuine UP HANDS YOU the solution
(the fold/extend). Proof-relevance of "sol solves spec" is not richer; it is the missing construction
hidden behind an existential. So "consumer needs the relational span" is not a requirement to honor —
it is a BUG (the consumer never exposed its constructive extend). The Vacuity/Contentful certificate
machinery built ON the relational Witness (proving the span is inhabited/non-trivial) is itself part
of that bug class: non-vacuity is trivially witnessed by the solve map's existence, no certificate
needed. Same root as [[set1-is-grade-collapse]] and [[adjunction-is-the-wedge-residue-counit]] (the
residue/counit is a constructive map, not a proposition).

**How to apply:** when replacing/writing a universal property, the witness field is a constructive
map `solve/extend/fold`, carriers are grade-indexed PARAMETERS (Set₀), never a Set-valued relation
and never held carrier fields. When migrating a consumer whose UP used a relational `Witness`, do NOT
add a relational variant to accommodate it — FIX the consumer: find/expose its constructive solve
(every genuine free/limit/adjunction UP has one: extend, mediate, fold), and drop the relational
witness + its Contentful certificate. If a consumer genuinely has no constructive solve, that is the
bug to surface, not a shape to support.
