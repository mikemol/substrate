------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.IterCyc
--
-- Defines: σ-iter-cyc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.IterCyc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



-- the rotation-of-the-orbit identity (direct induction, no σ-iterate-add).
σ-iter-cyc : ∀ {n} (m : ℕ) (k : Fin (suc n)) →
             σ-iterate m (cyclic-suc {n}) (cyclic-suc k) ≡ σ-iterate (suc m) (cyclic-suc {n}) k
σ-iter-cyc zero    k = refl
σ-iter-cyc (suc m) k = cong (cyclic-suc) (σ-iter-cyc m k)
