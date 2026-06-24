------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim
--
-- Ⓕ.spectral (a) connector — closing dim ker Φ_p(σ_p) = p−1 via Φ_p(σ_p) = A.
-- Reuse-search verdict: the orbit-sum assembles from existing blocks
-- (basis-decomp, preserves-sum, iterate-on-basis, σ-iterate-toℕ, mod-suc) —
-- no off-the-shelf orbit-sum operator. This file builds the two REUSABLE
-- pieces the closure plugs into:
--
--   KernelDim-cong : pointwise-equal operators have the same KernelDim
--                    (so dim ker Φ_p(σ_p) = dim ker A once Φ_p(σ_p) = A).
--   A-on-basis     : apply A (basis k) ≡ ones  (the A-side of the agreement).
--
-- The remaining seam is the orbit-sum  Φ_p(σ_p)(basis k) ≡ ones  (then
-- Φ_p(σ_p) = A by linear-extensionality, and `dim` = `KernelDim-cong` of
-- `Augmentation.aug-dim`). Its one new lemma: the cyclic orbit hits each
-- coordinate exactly once (countHits p ≡ 𝟙 via mod-suc injectivity).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.Augmentation using (A; total; ones)

------------------------------------------------------------------------
-- Transport: pointwise-equal operators share their KernelDim. (Generic;
-- the dimension of a kernel depends on the operator only through inKer.)
------------------------------------------------------------------------

KernelDim-cong :
  ∀ {n m} {L L′ : Linear n m} {d} →
  ((v : Vector n) → apply L v ≡ apply L′ v) →
  KernelDim L′ d → KernelDim L d
KernelDim-cong {L = L} {L′} eq KD = record
  { into     = KernelDim.into KD
  ; retract  = KernelDim.retract KD
  ; into-ker = λ x → trans (eq (apply (KernelDim.into KD) x)) (KernelDim.into-ker KD x)
  ; indep    = KernelDim.indep KD
  ; spans    = λ v h → KernelDim.spans KD v (trans (sym (eq v)) h)
  }

------------------------------------------------------------------------
-- The A-side of Φ_p(σ_p) = A: total of a basis vector is 𝟙, so A(eₖ) = ones.
------------------------------------------------------------------------

total-𝟎 : ∀ {n} → total (𝟎ⱽ {n}) ≡ 𝟘
total-𝟎 {zero}  = refl
total-𝟎 {suc n} = total-𝟎 {n}

total-basis : ∀ {n} (k : Fin n) → total (basis k) ≡ 𝟙
total-basis {suc n} zero    = trans (cong (𝟙 +_) (total-𝟎 {n})) (+-identityʳ 𝟙)
total-basis {suc n} (suc k) = total-basis k

A-on-basis : ∀ {n} (k : Fin (suc n)) → apply (A {suc n}) (basis k) ≡ ones
A-on-basis k = trans (cong (_*ₛ ones) (total-basis k)) (*ₛ-identityˡ ones)

-- REMAINING (the orbit-sum, Φσ-side): apply Φ_p(σ_p) (basis k) ≡ ones, then
-- Φ_p(σ_p) = A by linear-extensionality (with A-on-basis), then `dim` =
-- KernelDim-cong (sym of that) (Augmentation.aug-dim). Path, now opacity-aware:
--   1. EXPOSE `cyclic-Linear-basis : apply cyclic-Linear (basis k) ≡ basis (cyclic-suc k)`
--      from Cyclic's `opaque` block (1 line = apply-basis-permutation-Linear; the
--      module's own "hand consumers the lemma" pattern — cyclic-Linear stays sealed).
--   2. apply-powL-basis i k : apply (powL i σ_p)(basis k) ≡ basis(σ-iterate i cyc k)
--      (induction on i, reusing (1)).
--   3. count: lookup (apply (geomSumL σ_p m)(basis k)) j ≡ Σ_{i<m} [σ-iterate i cyc k ≟ j]
--      (induction on m, reusing (2) + lookup-+ⱽ + basis-lookup).
--   4. orbit-hits-once: at m=p, that F₂-count ≡ 𝟙 (cyclic orbit covers each j once,
--      via cyclic-suc's σ-iterate-toℕ = (k+i) mod-suc n + mod-injectivity) — THE one
--      genuinely new lemma; everything else is reuse.
