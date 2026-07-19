------------------------------------------------------------------------
-- Substrate.WitnessTower.TowerLiftSplit
--
-- ◆AI-2 — the honest "does the graded machinery carry beyond S₄/A₄?" answer.
-- The audit (SnVersusTwoPow) showed the lift is NON-monotone; this file states
-- WHICH structure lifts general-n and WHICH is rung-3 (S₄) -specific, in Agda,
-- so the split is a checked fact and not a prose hedge.
--
-- The distinction is TYPE-ENFORCED, not a matter of unfinished proof:
--
--   LIFTS (general-n): quantified over (n : ℕ), re-exported below with their
--   ∀-n types. These ARE the witnessing-tower spine (Ⓣ₁, cf.
--   SnVersusTwoPowTowers):
--     • tower-graded    : GradedDivStr Perm (λ n → Fin (suc n))
--     • apply-injective : {n} {σ τ : Perm n} → (∀ i → …) → σ ≡ τ
--     • sign-step       : {n} (p : Fin (suc n)) (σ : Perm n) → …
--     • perms-length    : (n : ℕ) → lengthL (perms n) ≡ factorial n
--   Every one is a statement about Perm n / perms n at ARBITRARY n. The sign
--   COCYCLE structure (sign-step: sign over the witnessing insertion) lifts,
--   because it is defined by the step, and induction gives all rungs.
--
--   RUNG-3-SPECIFIC (does NOT lift): the sign-FACTORS-THROUGH-STAB result and
--   everything it routes through:
--     • sign-stab-total : (σ : Permutation) → sign(perm4 σ) ≡ sign(perm4(s-for σ))
--   where `Permutation` = Symmetric Axis (the 4 axes), perm4 : Permutation →
--   Perm 4, and the factorisation σ ≈ embed(v-for σ)·s-for σ routes through V₄.
--   THIS CANNOT REINDEX to general n, and the obstruction is structural, not a
--   missing proof:
--     • V₄ (Groups.V4) is DEFINED as a 4-element datatype; embed : V₄ →
--       Permutation targets the 4-axis symmetric group.
--     • the anchor is an Axis (D ∈ {D,C,S,W}); s-for/v-for are Axis-indexed.
--     • mathematically: V₄ is normal in Sₙ ONLY at n = 4 (the exceptional
--       A₄/S₄ structure; Sₙ is almost-simple for n ≥ 5, no normal Klein four).
--       So "sign factors through a normal-V₄ complement" is an n = 4 theorem
--       with no general-n analogue to lift TO.
--
--   THE SEAM (SnVersusTwoPow): the codeword power-of-2 closure 24 + 8 = 32 =
--   2⁵ is where the two towers (Ⓣ₁ |Sₙ|, Ⓣ₂ 2ⁿ) meet at n = 4. Its gap-8
--   REAPPEARS at n = 5 (120 + 8 = 128) but at a different ceiling exponent and
--   with NO V₄/Hodge-dim-4 construction — arithmetic coincidence, not the same
--   structure. So even the seam does not lift; it recurs with different character.
--
-- NET (three-way, following the parity — NOT a binary lifts/doesn't):
--   • the GRADED WITNESSING-TOWER SPINE lifts general-n (tower-graded,
--     faithful, sign-step, count);
--   • V₄'s PARITY / V₂×V₂ structure lifts too — it is F₂-graded via parity∘hom
--     (general combinator), the three gradings giving V₄ ≅ Z/2×Z/2, the
--     AB-diagonal the shared-point V₂; this is the "reappears" — the parity
--     survives where the subgroup role does not;
--   • only V₄-AS-NORMAL-COMPLEMENT-IN-S₄ (hence sign-stab-total's factorisation
--     route) is rung-3-specific — it needs V₄ ◁ Sₙ, true only at n=4;
--   • the codeword/Hodge closure is the rung-3 seam (24+8=32), gap-8 reappearing
--     at n=5 by different means.
-- "Carries beyond S₄" is TRUE for the spine AND for V₄'s parity/graded role,
-- FALSE-as-stated only for the normal-complement factorisation and the closure.
-- Each half is a term whose TYPE witnesses its side.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.TowerLiftSplit where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Foundation.Vec using (lookup; map)
open import Substrate.Foundation.Bool using (_xor_)
open import Substrate.Foundation.Fin.Punctured using (punchIn)

------------------------------------------------------------------------
-- LIFTS (general-n). Re-exported with their ∀-n types; the quantifier over
-- (n : ℕ) IS the witness that these carry up the whole tower.
------------------------------------------------------------------------

open import Substrate.WitnessTower.Enumerate using (Perm; perms; factorial; lengthL)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)
open import Substrate.WitnessTower.SnGroup using (apply-injective)
open import Substrate.WitnessTower.SignStepCocycle using (sign-step)
open import Substrate.WitnessTower.Enumerate using (insert-at)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign; parityLess)
open import Substrate.WitnessTower.Enumerate using (perms-length)

-- The graded tower itself: a GradedDivStr at ALL grades n.
lifts-tower-graded : GradedDivStr Perm (λ n → Fin (suc n))
lifts-tower-graded = tower-graded

-- Faithfulness at every rung: action-agreement ⟹ equality, for all n.
lifts-faithful : {n : ℕ} {σ τ : Perm n} → ((i : Fin n) → lookup σ i ≡ lookup τ i) → σ ≡ τ
lifts-faithful = apply-injective

-- The sign cocycle over the witnessing step: general-n (induction gives all
-- rungs). Full explicit type (no _), so this is unambiguously the real
-- step-correspondence at arbitrary n.
lifts-sign-step : {n : ℕ} (p : Fin (suc n)) (σ : Perm n) →
                  sign (insert-at p σ) ≡ (parityLess p (map (punchIn p) σ) xor sign σ)
lifts-sign-step = sign-step

-- The count law |Sₙ| = n! at every rung.
lifts-count : (n : ℕ) → lengthL (perms n) ≡ factorial n
lifts-count = perms-length

------------------------------------------------------------------------
-- RUNG-3-SPECIFIC — but ONLY V₄'S ROLE AS NORMAL COMPLEMENT IN S₄. Following
-- the parity (the "disappears and reappears"): V₄'s structure does NOT wholly
-- fail to lift. It SPLITS into two roles, and only one is rung-3-bound.
--
--   (a) V₄-AS-NORMAL-COMPLEMENT-IN-S₄ — rung-3-specific, does NOT lift.
--       sign-stab-total routes through THIS: σ ≈ embed(v-for σ)·s-for σ needs
--       V₄ ◁ S₄, which holds ONLY at n=4 (Sₙ almost-simple, n≥5). Re-exported
--       below as rung3-sign-stab; its type is fixed to Permutation (4 axes).
--
--   (b) V₄-AS-V₂×V₂-WITH-PARITY — GENERAL, DOES lift (reappears). V₄ ≅ Z/2×Z/2
--       is an F₂-GRADED object, built by the GENERAL combinator
--       Category.RGradedMonoid.FromCoxeterHomomorphism ("any Coxeter Word +
--       an ℕ-homomorphism gives an F₂-graded RGradedMonoid via parity∘hom").
--       The THREE parity gradings ARE the three V₂ subgroups / the coordinate
--       iso V₄ ≅ Z/2×Z/2 (V4-Coxeter-F2Graded-CountB: "length-parity +
--       count-A-parity + count-B-parity gives the coordinate iso"):
--         length-parity : {ε,AB}₀ vs {A,B}₁      -- the AB-DIAGONAL V₂ (even)
--         count-A-parity: {ε,B}₀  vs {A,AB}₁      -- the A-axis V₂
--         count-B-parity: {ε,A}₀  vs {B,AB}₁      -- the B-axis V₂
--       AB (the diagonal / "the V₂ that shares a point with both") is EVEN
--       under length-parity but ODD under both count-A and count-B — the
--       shared point of the two V₂ factors. This F₂-graded/parity structure is
--       general (parity∘hom over any Coxeter word), NOT S₄-bound, and it is the
--       SAME parity that sign=stab-parity (rung3-sign-stab) is one instance of.
--       So the PARITY lifts even though the normal-complement does not.
------------------------------------------------------------------------

open import Substrate.Groups.S4 using (Permutation)
open import Substrate.WitnessTower.SignStabTotal using (sign-stab-total; sign-of)
open import Substrate.WitnessTower.SignEmbedVEven using (perm4)
open import Substrate.Groups.SemidirectProduct.S using (s-for)

-- (a) the rung-3 reading: fixed to the 4-axis symmetric group.
rung3-sign-stab : (σ : Permutation) → sign-of σ ≡ sign-of (s-for σ)
rung3-sign-stab = sign-stab-total

-- (b) the GENERAL reading: V₄ as an F₂-graded object (parity), and the three
-- parity gradings that give the V₂×V₂ coordinate iso. These LIFT — they are
-- instances of the general parity∘homomorphism combinator, not S₄ structure.
open import Substrate.Groups.V4-Coxeter-F2Graded using (V4-F2Graded)
open import Substrate.Groups.V4-Coxeter-F2Graded-CountA using (V4-F2Graded-CountA)
open import Substrate.Groups.V4-Coxeter-F2Graded-CountB using (V4-F2Graded-CountB)

-- the AB-diagonal parity (length), the shared-point V₂ made even:
lifts-v4-parity-diagonal = V4-F2Graded
-- the two axis parities (the V₂×V₂ factors):
lifts-v4-parity-A = V4-F2Graded-CountA
lifts-v4-parity-B = V4-F2Graded-CountB
-- together = the coordinate iso V₄ ≅ Z/2×Z/2, all three general F₂-gradings.

------------------------------------------------------------------------
-- THE OBSTRUCTION, precisely located (NOT "V₄ can't lift" — that was too
-- coarse). V₄ as a DATATYPE is 4-element (v4-cover below exhausts it in four
-- cases; no V₄ n). That 4-boundedness blocks ONE thing: V₄ acting as a normal
-- subgroup of the ℕ-indexed Perm n tower (the (a) reading). It does NOT block
-- the PARITY: V₄'s F₂-graded structure (the (b) reading) is built by parity∘hom
-- over a Coxeter word, general in the hom, and reappears wherever that graded
-- machinery does. So the datatype's finiteness bounds the SUBGROUP role, not
-- the GRADED role — the split above.
------------------------------------------------------------------------

open import Substrate.Groups.V4 using (V₄; e; α; β; γ)

-- V₄'s carrier is exhausted by four constructors: every v : V₄ is one of
-- e, α, β, γ. This 4-boundedness is what stops V₄ from being a subgroup of
-- Perm n at general n (no V₄ n) — but NOT what stops the parity (which is
-- parity∘hom, general). Contrast Perm n / CayleyDickson.Carrier n: suc-indexed.
data OneOfFour : Set where is-e is-α is-β is-γ : OneOfFour

v4-cover : V₄ → OneOfFour
v4-cover e = is-e
v4-cover α = is-α
v4-cover β = is-β
v4-cover γ = is-γ
-- total by exactly four cases: the carrier has no ℕ-parameter to grow a
-- subgroup role — yet its three parity gradings (lifts-v4-parity-*) DO lift.
