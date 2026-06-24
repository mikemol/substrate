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
open import Substrate.Foundation.Vec using (_∷_; []; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.Augmentation using (A; total; ones)
open import Substrate.Algebra.F2.Linear.Cyclotomic using (powL; geomSumL)
open import Substrate.Algebra.F2.Linear.SpectralCycle using (σ)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate using (σ-iterate)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-Linear-basis)

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

------------------------------------------------------------------------
-- conn2: σ_p^i sends basis k to the orbit position basis(σ-iterate i cyc k).
-- Induction on i, reusing the exposed cyclic-Linear-basis (conn1).
------------------------------------------------------------------------

apply-powL-basis :
  ∀ {n} (i : ℕ) (k : Fin (suc n)) →
  apply (powL i (σ {n})) (basis k) ≡ basis (σ-iterate i (cyclic-suc {n}) k)
apply-powL-basis zero    k = refl
apply-powL-basis (suc i) k =
  trans (cong (apply (σ)) (apply-powL-basis i k))
        (cyclic-Linear-basis (σ-iterate i (cyclic-suc) k))

------------------------------------------------------------------------
-- conn3: the per-coordinate orbit count. lookup j of Σ_{i<m} σ_p^i(eₖ) is the
-- F₂-tally of orbit visits to j. Induction on m, reusing conn2 + lookup-+ⱽ.
------------------------------------------------------------------------

occ : ∀ {n} → ℕ → Fin (suc n) → Fin (suc n) → F₂
occ zero    k j = 𝟘
occ (suc m) k j = occ m k j + lookup (basis (σ-iterate m (cyclic-suc) k)) j

orbit-count :
  ∀ {n} (m : ℕ) (k j : Fin (suc n)) →
  lookup (apply (geomSumL (σ {n}) m) (basis k)) j ≡ occ m k j
orbit-count zero    k j = lookup-𝟎 j
orbit-count (suc m) k j =
  trans (lookup-+ⱽ (apply (geomSumL (σ) m) (basis k)) (apply (powL m (σ)) (basis k)) j)
        (cong₂ _+_ (orbit-count m k j)
                   (cong (λ w → lookup w j) (apply-powL-basis m k)))

-- REMAINING — conn4 (the one new lemma) then conn5 (close):
--   conn4 orbit-hits-once : occ (suc n) k j ≡ 𝟙 (cyclic orbit visits each j once;
--         σ-iterate-toℕ = (toℕ k + i) mod-suc n + mod-injectivity).
--   conn5 : apply Φ_p(σ_p)(basis k) ≡ ones (≡-from-lookup ∘ orbit-count(suc n) ∘ conn4),
--         then Φ_p(σ_p)=A by linear-extensionality (+A-on-basis), then dim =
--         KernelDim-cong of Augmentation.aug-dim.
