------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCrossCoherent
--
-- Ⓕ.tower-crossmul — the F₂↔ℚ cross-carrier coherence of the Φ_p multiplicity.
--
-- CORRECTION (user, 2026-06-25): an earlier draft READ the F₂↔ℚ characteristic
-- clash as a WALL — "no meaningful common-R cospan, so relocate to the field-free
-- rung." That is the declaring-a-wall reflex wearing a negative theorem as its
-- disguise. CrossMix is designed for EXACTLY this case: when two carriers'
-- meanings are not LOCALLY resolvable, the clash is not refused — it is recorded
-- as the cross-term's graded NILPOTENT RESIDUE, resolved LATER by embedding the
-- residue into a richer carrier. This is PARACONSISTENCY for symbolic logic: a
-- local contradiction (here MODULAR vs NON-MODULAR — over F₂ doubling is 0, over
-- ℚ it is invertible) does NOT explode (trivialise / refuse the bridge); it is
-- localised as a graded residue and carried. A `Bridge` respects recon + z, NOT
-- units/inverses, so the ring-level "2≡0 vs 2 invertible" never blocks the
-- CrossMix — it only GRADES it.
--
-- So the coherence SPLITS, exactly as CrossMul's grading prescribes:
--   • COHERENT part (cross-term degree 0, resolved locally): the Φ_p
--     multiplicity. `degΦ p = p ∸ 1` and the crossing-count `mult2` are ℕ-valued
--     (pre-field); the F₂ operator realizes degΦ as a kernel dimension
--     (`crosscoherent-F₂` = `dim-ker-Φσ`, dim ker Φ_p(σ_p) = p−1) — the same in
--     every field, the orthogonal locally-resolved invariant.
--   • RESIDUE part (graded obstruction, resolved later): the CHARACTERISTIC.
--     `double-F₂` (x+x≡𝟘) and `2ℚ≢0ℚ` (1+1≉0) MEASURE it — the cross-term's
--     content, NOT a proof that no bridge exists.
--
-- The actual residue-carrying CrossMix F₂-div ℚ-div R (the carrier into which
-- the modular residue embeds, à la the deferred CRT/numeral witness in
-- Wedge.CrossMul) is Ⓕ.tower-crossmul-residue — the proper completion. This
-- module pins the COHERENT part and MEASURES the residue.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCrossCoherent where

open import Substrate.Foundation.Nat using (ℕ; suc; _∸_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.SpectralCycle using (Φσ)
open import Substrate.Algebra.F2.Linear.SpectralCycleDim using (dim-ker-Φσ)
open import Substrate.WitnessTower.PhiMultiplicity using (mult2; nullity2)
open import Substrate.Algebra.F2.Linear.SpectralTower using (nullity2-factored)

------------------------------------------------------------------------
-- 1. The RESIDUE: the doubling map separates the carriers (modular vs non-
--    modular). This is NOT a wall — it is the cross-term content a CrossMix
--    carries paraconsistently (a graded nilpotent), resolved later by embedding.
--    F₂: x+x≡𝟘 (doubling is 0);  ℚ: 1+1≉0 (doubling is invertible).
------------------------------------------------------------------------

double-F₂ : (x : F₂) → (x + x) ≡ 𝟘
double-F₂ 𝟘 = refl
double-F₂ 𝟙 = refl

2ℚ≢0ℚ : ¬ ((1ℚ +ℚ 1ℚ) ≈ℚ 0ℚ)
2ℚ≢0ℚ ()

------------------------------------------------------------------------
-- 2. The COHERENT (degree-0) part: the per-factor multiplicity is ℕ-valued,
--    defined below the field, so it is identical in every carrier.
------------------------------------------------------------------------

degΦ : ℕ → ℕ                       -- per-factor degree of Φ_p = p − 1
degΦ p = p ∸ 1

------------------------------------------------------------------------
-- 3. The F₂ leg: the F₂ cycle operator REALIZES degΦ as its Φ_p-kernel
--    dimension. degΦ (suc n) = n by reduction, so this IS dim-ker-Φσ.
------------------------------------------------------------------------

crosscoherent-F₂ : (n : ℕ) → KernelDim (Φσ {n}) (degΦ (suc n))
crosscoherent-F₂ n = dim-ker-Φσ {n}

------------------------------------------------------------------------
-- 4. The multiplicity composition, in degΦ form: the cotype's nullity is the
--    crossing-multiplicity times the (field-free) per-factor degree. Both
--    factors are ℕ — the whole invariant is pre-field, hence cross-coherent.
------------------------------------------------------------------------

nullity-as-mult×degΦ : (n c : ℕ) → nullity2 (suc n) c ≡ mult2 (suc n) c * degΦ (suc n)
nullity-as-mult×degΦ n c = nullity2-factored n c
