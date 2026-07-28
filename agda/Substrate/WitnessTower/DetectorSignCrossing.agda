------------------------------------------------------------------------
-- Substrate.WitnessTower.DetectorSignCrossing
--
-- ◆AI-5 — the DETECTOR/SIGN GRADE CROSSING (the "hinge", corrected from a wrong
-- "gestural" verdict — user: "binary vs unary — that's a grade crossing").
--
-- Two F₂-valued gradings on the SAME tower carrier Perm n, ONE cohomological
-- degree apart:
--   · signF   : Perm n → F₂            (TowerCocycleGraded) — DEGREE 1, the SIGN
--       1-cochain (signF σ = bool→F₂(sign σ)); a 1-cocycle (δ signF = 0).
--   · detectP : Perm n → Perm n → F₂   (FaithfulnessApex)   — DEGREE 2, the
--       DISTINCTION 2-cochain (detect σ τ = 𝟘 iff σ ≡ τ; kernel = diagonal).
--
-- THE CROSSING (grade-map RAISE, degree 1 → 2 by adding an argument):
--   (A) DIAGONAL AGREEMENT: detectP σ σ ≡ signF σ + signF σ (both 𝟘). The two
--       zeros are the SAME phenomenon — self-pairing gives 𝟘: the detector's
--       diagonal law on the degree-2 side, F₂ char-2 self-cancel (x + x = 𝟘) on
--       the degree-1 side.
--   (B) OFF-DIAGONAL FREENESS: detectP is STRICTLY FINER — a FREE degree-2
--       companion, NOT a coboundary of signF. Two distinct EVEN perms (id and a
--       3-cycle, both sign 𝟘) have detectP = 𝟙 but signF + signF = 𝟘. detectP
--       separates same-sign unequal perms that no signF-combination can.
--
-- So the hinge is REAL and PROVABLE, not gestural: signF (deg 1) and detectP
-- (deg 2) are the two F₂-cochains on the perm tower, sharing the diagonal-
-- vanishing law, with the degree-2 detector free over (finer than) the sign.
--
-- --safe --without-K, no Σ / Set₁. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.DetectorSignCrossing where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; +-self-inverse)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FaithfulnessApex using (detectP; action-agreement→detect-𝟘)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)

------------------------------------------------------------------------
-- detectP σ σ ≡ 𝟘 : the detector vanishes on the diagonal. From
-- action-agreement→detect-𝟘 fed the trivial agreement (λ i → refl).
------------------------------------------------------------------------

detectP-diag : {n : ℕ} (σ : Perm n) → detectP σ σ ≡ 𝟘
detectP-diag σ = action-agreement→detect-𝟘 (λ i → refl)

------------------------------------------------------------------------
-- (A) DIAGONAL AGREEMENT. detectP σ σ ≡ signF σ + signF σ (both 𝟘). Degree-2
-- side by detectP-diag; degree-1 side by F₂ self-cancellation.
------------------------------------------------------------------------

diagonal-agreement :
  {n : ℕ} (σ : Perm n) → detectP σ σ ≡ (signF σ + signF σ)
diagonal-agreement σ = trans (detectP-diag σ) (sym (+-self-inverse (signF σ)))

------------------------------------------------------------------------
-- (B) OFF-DIAGONAL FREENESS. Two distinct even perms of Perm 3: detectP = 𝟙
-- (they differ) while signF + signF = 𝟘 (same sign). So detectP is finer.
------------------------------------------------------------------------

id3 : Perm 3
id3 = zero ∷ suc zero ∷ suc (suc zero) ∷ []

cyc3 : Perm 3
cyc3 = suc zero ∷ suc (suc zero) ∷ zero ∷ []

detect-separates : detectP id3 cyc3 ≡ 𝟙
detect-separates = refl

signsum-blind : (signF id3 + signF cyc3) ≡ 𝟘
signsum-blind = refl

𝟙≢𝟘 : ¬ (𝟙 ≡ 𝟘)
𝟙≢𝟘 ()

-- detectP is strictly finer: at (id3 , cyc3) the two disagree, so no signF-
-- combination equals detectP. The degree-2 companion is free.
detector-finer-than-sign : ¬ (detectP id3 cyc3 ≡ (signF id3 + signF cyc3))
detector-finer-than-sign eq = 𝟙≢𝟘 (trans (sym detect-separates) (trans eq signsum-blind))
