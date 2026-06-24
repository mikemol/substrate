------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycle
--
-- Ⓕ.spectral (a), the LITERAL p-cycle shift — by INSTANTIATION, not grind.
-- The shift and its order-p law are already built, parametric over n, in
-- the Permutation package (the repo's architecture: build once, instantiate):
--
--   σ_p   = cyclic-Linear   : Linear (suc n) (suc n)   -- the p-cycle shift
--   σ_p^p = id              = cyclic-HasOrder            -- HasOrder, generic
--
-- (cyclic-suc i = (i+1) mod p on Fin p; basis-permutation-Linear lifts it to
--  the coordinate-permuting Linear map; cyclic-HasOrder transports the
--  HasOrderPerm witness to the Linear level — all derived once at abstract n.)
--
-- This module instantiates them and derives the eigenvalue-1 relation for the
-- cyclotomic operator Φ_p(σ_p) via the generic `ΦL-orbit-fixed`: on the orbit
-- (σ_p^p = id), every Φ_p(σ_p)-image is σ_p-fixed (im Φ_p(σ_p) ⊆ Fix σ_p) —
-- the relation the f090_2 multiplicity counts. The remaining connector
-- (Φ_p(σ_p) = A, the augmentation, ⟹ dim ker = p−1 via Augmentation.aug-dim)
-- is the orbit-sum Φ_p(σ_p)(eₖ) = ones.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycle where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Cyclotomic using (ΦL; powL; ΦL-orbit-fixed)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-Linear; cyclic-HasOrder)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

------------------------------------------------------------------------
-- The p-cycle shift and its order, INSTANTIATED (p = suc n).
------------------------------------------------------------------------

σ : ∀ {n} → Linear (suc n) (suc n)
σ {n} = cyclic-Linear {n}

σ-order : ∀ {n} → HasOrder (apply (σ {n})) (suc n)
σ-order {n} = cyclic-HasOrder {n}

-- Φ_p(σ_p) = id + σ_p + … + σ_p^{p-1}, the cyclotomic operator at the shift.
Φσ : ∀ {n} → Linear (suc n) (suc n)
Φσ {n} = ΦL (σ {n}) (suc n)

------------------------------------------------------------------------
-- Eigenvalue-1 relation: on the orbit, every Φ_p(σ_p)-image is σ_p-fixed.
-- σ_p^p v ≡ v (from σ-order) ⟹ σ_p (Φσ v) ≡ Φσ v (generic ΦL-orbit-fixed).
------------------------------------------------------------------------

Φσ-fixed : ∀ {n} (v : Vector (suc n)) →
           apply (powL (suc n) (σ {n})) v ≡ v →
           apply (σ {n}) (apply (Φσ {n}) v) ≡ apply (Φσ {n}) v
Φσ-fixed {n} v = ΦL-orbit-fixed (σ {n}) (suc n) v
