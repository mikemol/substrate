---
name: project_cayley_dickson_generator
description: "The Cayley-Dickson doubling is a GENERATOR (one step — multiply+conjugate, doubling the carrier — applied structurally recursively), built at Algebra.CayleyDickson as the ℕ-indexed tower over ℚ. It does NOT 'stop at the octonions': Carrier n is total for all n; what stops is a PROPERTY (Hurwitz), and the 𝕆→𝕊 zero divisor is a NAMED algebraic fact the construction COMPUTES (refl), not a wall. SAME doubling-with-involution principle as nedge's Evidence carrier-doubling."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

(user, 2026-06-12) "I don't want to keep getting told 'this stops at the octonions'
when what's really meant is 'there's zero divisors, that's hard'." And: "it's a
multiplication and conjugation that takes you from real to complex; everything
higher is that same precise step, applied structurally recursively — the same
principle as the carrier-doubling in nedge."

`Sphere.agda` had flagged "Cayley-Dickson NOT in substrate (build)"; there was NO ℂ
carrier and NO CD multiplication (`MultiscaleOctonionLoop` is the orthogonal
SCALE/rotation generator, not the doubling algebra). Now BUILT:
`Substrate.Algebra.CayleyDickson` (commit 52e4897), --safe --without-K, zero
postulates.

**The design = the user's framing.** ONE step, recursed:
`Carrier (suc n) = Carrier n × Carrier n`, with `mul`/`conj` recursing
(`conj (a,b)=(a*,−b)`; `mul (a,b)(c,d)=(ac−d*b, da+bc*)`). Total for every n ⟹
"doesn't stop" is LITERAL (`Carrier 5` = 𝕋 as constructible as ℂ). Base = ℚ (the
constructive *-ring, conj=id): ℂ=ℚ(i), ℍ, 𝕆, 𝕊, … (ℂ over RealTrace-ℝ is blocked
only by the open Gosper +/× — [[project_substrate_real_arc]] — a separate item).
`i²≈−1` by the doubled product (pointwise `≈ℚ`).

**The "wall" is a DISCARDED RESIDUE, not a halt.** Two corrections from the user
sharpened this:
(a) Don't SEARCH for the zero divisor (empirical-hunt reflex) — the Cayley step is
    deterministic; write one and the construction confirms it.
(b) DEEPER (the real point): "a zero divisor is just a modulo in the multiplicative
    domain where we didn't keep the remainder/residue. el-atlas works around zero
    divisors by keeping the vector just-prior-to-zero-divisor + the zero-divisor
    space — maintaining the generator state in the rational, not collapsing to 0."
My first cut (`mul 4 xZD yZD ≈ 0`) was the COLLAPSED look — it threw the residue
away. Rebuilt on never-discard-residue (the gcd-ℕ = proj₁ ∘ compute-trace pattern):
`Prod n` + `mulW` keep the four level-n sub-products of one doubling product;
`value` is the lossy projection; `mul ≡ value ∘ mulW` (refl). For the witness
`(e₁+e₁₀)(e₄−e₁₅)`: `zd-value-0` (collapsed value 0), `zd-residue-coincides`
(left coord cancels ONLY because acP ≈ dbP — a multiplicative MODULO, not
annihilation), `zd-residue-nonzero` (the kept remainder acP = e₁ᴼ·e₄ᴼ = e₅ᴼ is a
NONZERO unit octonion). The "annihilation" is `acP ≈ dbP`; the residue e₅ᴼ is held,
exactly as el-atlas holds the just-prior vector. The doubling continues 𝕊→𝕋→…
unobstructed. ([[feedback_never_discard_residue]], [[feedback_wedge_not_projection]].)

**Same principle as nedge's carrier-doubling** (convergence-over-isolation, the
user's pointer): `Logic.Evidence.Verdict.Evidence = ⟨pos,neg⟩` is `Bool` doubled;
`negNeg ⟨p,n⟩=⟨p,¬n⟩` negates the imaginary half = CD `conj`; `negBoth` is the −1
antipode (`Verdict.Phase.negBoth-invol`); involutions = V₄. CD instantiates the
doubling over ℚ WITH the twisted product (normed-algebra face); nedge over the
Belnap/F₂ lattice (involution/lattice face). Layering blocks importing Evidence
(it sits above Algebra), so the tie is prose; a bridge module above both is a
follow-on. Relates [[project_commuting_sphere]] #3 (Morton≅CD cocycle — the cocycle
bridge is still the open cell) and [[feedback_octonion_loop_expressivity_limit]].

**Nedge-over-arbitrary-carrier [LANDED, 5cc8473]** `Logic.Evidence.DualRail` — the
user's "I want Nedge not over Bool but over an arbitrary compatible carrier (Real,
Complex, CD); it feels almost stateful." It is: `EvCarrier C = C × C` is one
doubling, nesting = the state; `Verdict.Evidence` is the C=Bool instance frozen.
A compatible carrier needs (1) an involution `neg` (the §5 chart involutions; V₄
laws proved GENERICALLY — `Phase.negBoth-invol` is that at Bool) and (2) a SEMIRING
`(add,mul)` for the connectives. KEY CORRECTION the user forced: the connectives are
NOT a lattice and use NO min/max — min/max TRUNCATE (never-discard-residue forbids
it). Bool's ∧/∨ are the Boolean semiring's ×/+; connectives act rail-wise with the
carrier's own +,× (⊗E=×-both, ⊕E=+-both, ∧E=⟨×,+⟩, ∨E=⟨+,×⟩), so they generalize to
ℂ/CD too (no order needed). min/max = only the tropical semiring (one gauge of
[[project_commuting_sphere]] #6, the lossy one). Instances: Bool (recovers Verdict),
ℚ (+ℚ/*ℚ). UNIFICATION proved: `cd-doubling-is-dualrail : Carrier (suc n) ≡
EvCarrier (Carrier n)` (refl) — one Nedge step = one CD doubling. LESSON: a
connective/aggregation gauge is a SEMIRING; reaching for min/max is the
truncation/lossy reflex.

OPEN/follow-on: associativity-loss witnesses (¬assoc at 𝕆, ¬comm at ℍ) as the graded
residue ladder; the norm + Hurwitz statement; the Morton/cocycle bridge; a ℚ-base
*-ring record so CD is `StarRing → StarRing` parametrically (currently the concrete
ℚ-tower). Pattern lesson: the doubling tower is the [[project_center_free_universal_property]]
generator shape again — name the step, recurse it, track the residue; don't stop.
