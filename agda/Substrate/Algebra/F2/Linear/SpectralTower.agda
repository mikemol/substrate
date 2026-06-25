------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralTower
--
-- Ⓕ.tower (bridge) — connecting (a)'s spectral per-factor result to the
-- JEA-Pi cotype's f090_2 multiplicity count.
--
-- The cotype's spectral input was: mult2/2 IS the multiplicity of Φ_p in the
-- cycle-space operator's char poly; equivalently the Φ_p-isotypic dimension is
--   nullity = (multiplicity) · (degΦ_p).
-- Three pieces, now status:
--   • multiplicity  mult2 p c  — PROVEN combinatorially (PhiMultiplicity, as the
--     FaceCount-fibered crossing count). The CROSSING count: mult2 p 0 = 0 (a single
--     p-cycle in isolation contributes none — it is crossings that produce factors).
--   • composition   nullity2 = mult2 · (p∸1)  — PROVEN (PhiMultiplicity, nullity2 def).
--   • per-factor    (p∸1) = degΦ_p  — now SPECTRALLY GROUNDED by (a): it IS the
--     machine-checked dim ker Φ_p(σ_p) = n (= p−1) for the p-cycle shift (p = suc n).
--
-- This module records the bridge: the multiplicand (p∸1) in the cotype's nullity2 is
-- no longer a probe-verified INPUT — it is the proven kernel dimension `dim-ker-Φσ`.
--
-- "You don't need the result — you need to be able to READ the result." We do NOT build
-- the crossing operator and COMPUTE its char-poly multiplicity (that is the result we
-- don't need). The cotype's nullity is READABLE, by reduction, off two now-proven factors:
-- the multiplicity `mult2` (FaceCount-fibered crossing count) and the per-factor degΦ_p
-- (= dim ker Φ_p(σ_p), (a)). `nullity2-factored` is that read — `refl` — and `per-factor-dim`
-- supplies the spectral witness for the multiplicand. The strata = eigenspaces identification
-- is the cotype's probe finding; FaceCount (mult2) + (a) ground its two numerical factors,
-- and reading their product IS the grounding — no operator construction required.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralTower where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.WitnessTower.PhiMultiplicity using (mult2; nullity2)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.SpectralCycle using (Φσ)
open import Substrate.Algebra.F2.Linear.SpectralCycleDim using (dim-ker-Φσ)

------------------------------------------------------------------------
-- The per-factor Φ_p dimension, spectrally grounded (a): for the p-cycle
-- shift (p = suc n), dim ker Φ_p(σ_p) = n = p−1 = degΦ_p. Re-exported as the
-- multiplicand witness of the cotype's nullity.
------------------------------------------------------------------------

per-factor-dim : ∀ {n} → KernelDim (Φσ {n}) n
per-factor-dim = dim-ker-Φσ

------------------------------------------------------------------------
-- The cotype's nullity factors as (doubled) multiplicity × per-factor dimension.
-- nullity2 (suc n) c ≡ mult2 (suc n) c · n, where the multiplicand n is exactly
-- `per-factor-dim`'s dimension (= dim ker Φ_p(σ_p), machine-checked).
------------------------------------------------------------------------

nullity2-factored : (n c : ℕ) → nullity2 (suc n) c ≡ mult2 (suc n) c * n
nullity2-factored n c = refl
