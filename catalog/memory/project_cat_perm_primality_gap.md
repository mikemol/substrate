---
name: project_cat_perm_primality_gap
description: "In the graded symmetric rig categorification (orientationRigCatPerm), the braidings generate Sₙ iff n is composite; at prime n≥3 they reach only Cₙ. Block-swaps are rotations (Cₙ); the MULTIPLICATIVE factor-swaps fill in Sₙ, and primes are where ⊗ contributes nothing."
metadata:
  node_type: memory
  type: project
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Discovered 2026-07-11 building ⟡rig-UP-cat-perm-UP (the functor-UP of `orientationRigCatPerm`,
`Substrate.WitnessTower.Wedge.OrientationRigCatPermUP`). numpy-verified, then Agda-committed
(21c228f + the perm-UP commit).

**The fact.** `orientationRigCatPerm` has one object per grade (`Objₛ`) and the full symmetric
group `Perm n = Sₙ` as morphisms at grade n. Its two families of braiding morphisms are:
- **block-swaps** `braid⊕{i}{j}` (i+j=n) = `blockSwap i (n−i)` = the cyclic shift by n−i → together
  they generate exactly the ROTATIONS `Cₙ`;
- **factor-swaps** `braid⊗{i}{j}` (i·j=n) = the i×j grid transpose (`factorSwap`).

Their closure under composition: **⟨block-swaps ∪ factor-swaps⟩ = Sₙ ⟺ n is composite (or n∈{1,2});
for prime n≥3 the factor-swaps are trivial (no nontrivial i·j=n) and only rotations survive → Cₙ ⊊
Sₙ.** Measured: n=1,2,4,6,8 → |Sₙ|=1,2,24,720,40320 (full); n=3,5,7 → order 3,5,7 (just Cₙ).

**Why it matters (the center it names).** The ADDITIVE braidings only ever reach Cₙ; it is the
MULTIPLICATIVE braidings that make a grade fully symmetric — and they exist exactly when the grade
factors. So the categorification carries a genuine number-theoretic shadow: **composite grades are
braiding-symmetric, prime grades are braiding-rigid (stuck at rotations).** This is why the functor-UP
is an honest PARTIAL: F-obj is forced ∀ target (objects are `Objₛ`, same as the skeletal cat), F-hom
is forced on braiding-WORDS, but `orientationRigCatPerm` is NOT free/initial via its braidings — at
prime grades the full Sₙ homs are unpinned. The two obstructions: primality (⊗ gives nothing) AND the
absence of a monoidal-product-on-MORPHISMS (a bifunctor `gmap`) — with a bifunctor, `s_i = id ⊕ s₁ ⊕
id` becomes reachable and adjacent transpositions generate Sₙ (Coxeter).

**STATUS (2026-07-11, both proven):** the gap witness is CLOSED —
`OrientationRigCatPermGap.transposition-∉-braidings` proves (0 1) ∉ ⟨grade-3 braidings⟩ = C₃ by
FINITE CLOSURE (no sign homomorphism needed; an earlier "needs a sign that doesn't exist" was a false
absence claim — the alternating sign DOES walk the tower via `CycleType.cycle-type`). The bifunctor is
BUILT (`OrientationRigCatPermBifunctor`): `blockSum-id`/`blockSum-compose` (= gmap-id/∘) ARE the
⊕-bifunctor on morphisms, the previously-missing structure; and `OrientationRigCatPermAdjClosure`
proves the dual `adjT-generate-S₃` — ⟨adjacent transpositions⟩ = ALL of S₃. So the gap CLOSES at grade
3 (rotations→C₃; +bifunctor's adjacent transpositions→S₃), machine-checked. **Ⓐ ⟡coxeter-completeness** —
CONCRETE grades now MECHANICAL: the ⟡pipeline-driver synthesizer's `--class orbit` (synth_agda_
prototype.py) BFS-maps ⟨gens⟩ and emits every element as an explicit generator-word +
`complete : AllGen σ → Gen σ`; when |orbit|=n! it IS Coxeter-completeness at grade n. Committed
`OrientationRigCatPermCoxeter4` proves it for all 24 of S₄ (synthesized, green); grade 3 is the hand
`OrientationRigCatPermAdjClosure`. Any finite grade is a synthesis away. The GENERAL ∀-n theorem
still needs the inductive `insert-at = adjacent-transposition bubble-run` bridge over the tower's
Perm≅LehmerPath (⇒ F-hom determined by F(s₁) ⇒ free) — the one remaining hand proof. Sibling of [[coxeter-word-is-combine-generators]]
(act on generators, extend over words) and [[feedback_reuse_search_before_feasibility_conclusions]].
