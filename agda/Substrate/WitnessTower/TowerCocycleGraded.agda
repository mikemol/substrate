------------------------------------------------------------------------
-- Substrate.WitnessTower.TowerCocycleGraded
--
-- ⟡tower-cocycle-graded — the UNIFIER. The graded-wedge study (AxisWord)
-- showed the free graded wedge has TWO complementary forgets: the EXTERIOR
-- reading (keeps the SIGN, forgets multiplicity) and the k-d reading (keeps
-- multiplicity, forgets sign). This file records that the tower's
-- permutation SIGN cocycle IS the exterior/sign forget over the tower's
-- graded permutation carrier — unifying the WHT/chirality arc
-- (WHTCharacterBridge, sign-is-chirality) with the graded tower spine
-- (tower-graded : GradedDivStr Perm).
--
-- The pieces, now co-apexed:
--   * tower-graded : GradedDivStr Perm (λ n → Fin (suc n))   — the graded
--       permutation carrier (grade = rung; recon = insert-at). [WT.Wedge.Graded]
--   * sign : Perm n → Bool, sign-hom : sign (σ·τ) ≡ sign σ xor sign τ
--       (given IsPerm σ, IsPerm τ) — the permutation SIGN, a grade-additive
--       ℤ/2 cocycle over that carrier. [OrientationRigCatPermSign]
--   * bool→F₂-xor : the xor→+F transport, so sign-in-F₂ is a ℤ/2 HOM.
--   * sign-is-chirality (fifth guise) already ties this sign to the chirality
--       bit WHTCharacterBridge bridges. [OrientationRigCatPermSignChirality]
--
-- So: the SIGN is the exterior-forget cocycle of the graded permutation
-- wedge (the "reorder/sign residue" AxisWord named the next brick — the one
-- exterior keeps, k-d forgets). This is the graded-cocycle reading of the
-- chirality arc, over the UNBOUNDED tower (all n), not pinned at rung 3.
--
-- HONEST SCOPE: this co-apexes the SIGN cocycle with the graded carrier +
-- chirality arc — it does NOT yet build the full CY-5 codeword as a
-- GradedProduct (the multiplicity/k-d leg + the 5-bit codeword lift remain).
-- What is established: sign is the ℤ/2 exterior cocycle over tower-graded,
-- for every grade n. The chirality/WHT arc is thereby tower-graded-manifest.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.TowerCocycleGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Bool using (Bool; _xor_)
open import Substrate.Foundation.Eq using (_≡_; trans; cong; cong₂)
open import Substrate.Algebra.F2 using (F₂; _+_)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign; sign-hom)
open import Substrate.Algebra.F2.FromBool using (bool→F₂; bool→F₂-xor)

------------------------------------------------------------------------
-- 1. The graded carrier IS the tower's (imported → real edge in the graph).
--    tower-graded : GradedDivStr Perm (λ n → Fin (suc n)).
------------------------------------------------------------------------

graded-carrier = tower-graded

------------------------------------------------------------------------
-- 2. The SIGN cocycle in ℤ/2 over that carrier: bool→F₂ ∘ sign, a
--    grade-additive homomorphism (sign of a composite = sum of signs).
--    This is the exterior/sign forget — the reorder cocycle exterior keeps.
------------------------------------------------------------------------

signF : {n : ℕ} → Perm n → F₂
signF σ = bool→F₂ (sign σ)

-- THE ℤ/2 COCYCLE LAW over the graded carrier: for genuine permutations,
-- signF is additive over composition — the exterior sign cocycle, at EVERY
-- grade n (unbounded, not pinned at rung 3).
signF-cocycle :
  {n : ℕ} (σ τ : Perm n) → IsPerm σ → IsPerm τ →
  signF (compose σ τ) ≡ (signF σ + signF τ)
signF-cocycle σ τ pσ pτ =
  trans (cong bool→F₂ (sign-hom σ τ pσ pτ))
        (bool→F₂-xor (sign σ) (sign τ))
