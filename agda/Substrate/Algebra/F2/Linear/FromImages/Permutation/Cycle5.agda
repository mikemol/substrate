------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
--
-- The 5-cycle σ₅ : Fin 5 → Fin 5 lifted via basis-permutation-Linear
-- to an order-5 HasOrder instance on Vector 5.
--
-- Sibling of Cycle3 / Cycle4 at n=5. First cyclic torsion instance
-- at prime > 3 in the substrate.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5 where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

------------------------------------------------------------------------
-- N-1: σ₅ — the 5-cycle on Fin 5 (0 → 1 → 2 → 3 → 4 → 0).
------------------------------------------------------------------------

σ₅ : Fin 5 → Fin 5
σ₅ zero                                  = suc zero
σ₅ (suc zero)                            = suc (suc zero)
σ₅ (suc (suc zero))                      = suc (suc (suc zero))
σ₅ (suc (suc (suc zero)))                = suc (suc (suc (suc zero)))
σ₅ (suc (suc (suc (suc zero))))          = zero

------------------------------------------------------------------------
-- N-2: σ₅ has order 5 as a permutation.
------------------------------------------------------------------------

σ₅-HasOrderPerm : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm zero                                  = refl
σ₅-HasOrderPerm (suc zero)                            = refl
σ₅-HasOrderPerm (suc (suc zero))                      = refl
σ₅-HasOrderPerm (suc (suc (suc zero)))                = refl
σ₅-HasOrderPerm (suc (suc (suc (suc zero))))          = refl

------------------------------------------------------------------------
-- N-3: cycle5-Linear — the linear endomap induced by σ₅.
------------------------------------------------------------------------

cycle5-Linear : Linear 5 5
cycle5-Linear = basis-permutation-Linear σ₅

------------------------------------------------------------------------
-- N-4: HasOrder-cycle5 — order-5 instance via the structural lift.
------------------------------------------------------------------------

HasOrder-cycle5 : HasOrder (apply cycle5-Linear) 5
HasOrder-cycle5 = HasOrder-from-perm σ₅ 5 σ₅-HasOrderPerm
