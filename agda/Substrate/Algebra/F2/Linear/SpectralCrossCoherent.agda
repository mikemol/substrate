------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCrossCoherent
--
-- Ⓕ.tower-crossmul — the F₂↔ℚ cross-carrier coherence of the Φ_p multiplicity.
--
-- The ROSTER framed this as a CrossMul COSPAN F₂ → R ← ℚ with common R. That
-- shape is WRONG, and finding out why is the content: a *meaningful* common
-- multiplicative carrier R receiving both F₂ and ℚ cannot exist, because the
-- two fields disagree on the doubling map —
--     over F₂:  x + x ≡ 𝟘    for every x      (`double-F₂`, characteristic 2)
--     over ℚ:   1 + 1 ≉ 0                      (`2ℚ≢0ℚ`, characteristic 0)
-- so any R honouring both would need 2 ≡ 0 AND 2 ≢ 0. The carriers are
-- comparable=False at the FIELD rung (cf. the oneforest comparability guard /
-- Ⓗ.neg-guard — "numbers quotiented of meaning").
--
-- The cross-coherence therefore lives one quotient DOWN, at the FIELD-FREE rung:
-- the Φ_p multiplicity is ℕ-valued (defined before any field) and each field
-- REALIZES it separately. The per-factor degree `degΦ p = p ∸ 1` and the
-- crossing-multiplicity `mult2` (WitnessTower.PhiMultiplicity) are pure ℕ; the
-- F₂ operator realizes the per-factor degree as a kernel dimension
-- (`crosscoherent-F₂` = `dim-ker-Φσ`, dim ker Φ_p(σ_p) = p−1). This is the
-- cospan replaced by a SPAN whose apex is the field-free invariant.
--
-- The ℚ leg (the signed/char-0 operator realizing the SAME degΦ) is gated on
-- Ⓕ.tower-ℚ-inst (the ≈ℚⱽ vector setoid); when it lands, cross-coherence =
-- "both legs realize degΦ", and the agreement is automatic because degΦ is ℕ.
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
-- 1. The characteristic obstruction: the doubling map separates the carriers.
--    F₂ and ℚ cannot share a doubling-respecting carrier R (2≡0 vs 2≢0), so
--    there is no meaningful common-R cospan — the cross-coherence is NOT a
--    CrossMix. (This IS the field-rung comparability guard.)
------------------------------------------------------------------------

double-F₂ : (x : F₂) → (x + x) ≡ 𝟘
double-F₂ 𝟘 = refl
double-F₂ 𝟙 = refl

2ℚ≢0ℚ : ¬ ((1ℚ +ℚ 1ℚ) ≈ℚ 0ℚ)
2ℚ≢0ℚ ()

------------------------------------------------------------------------
-- 2. The field-free invariant (the SPAN apex): the per-factor multiplicity is
--    ℕ-valued, defined below the field.
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
