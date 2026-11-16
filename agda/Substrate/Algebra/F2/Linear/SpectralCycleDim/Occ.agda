------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ
--
-- Defines: occ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc



------------------------------------------------------------------------
-- conn3: the per-coordinate orbit count. lookup j of Σ_{i<m} σ_p^i(eₖ) is the
-- F₂-tally of orbit visits to j. Induction on m, reusing conn2 +F lookup-+ⱽ.
------------------------------------------------------------------------

occ : ∀ {n} → ℕ → Fin (suc n) → Fin (suc n) → F₂
occ zero    k j = 𝟘
occ (suc m) k j = occ m k j +F lookup (basis (σ-iterate m (cyclic-suc) k)) j
