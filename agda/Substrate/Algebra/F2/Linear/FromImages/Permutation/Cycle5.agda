------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
--
-- σ₅ on Fin 5 + HasOrderPerm, as a thin instance of
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic.
--
-- σ₅ = cyclic-suc {4}; HasOrderPerm comes free (no per-position
-- enumeration). The linear lift cycle5-Linear + HasOrder-cycle5 use
-- the substrate's basis-permutation-Linear + HasOrder-from-perm
-- machinery.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5 where

open import Substrate.Foundation.Fin using (Fin)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₅ : Fin 5 → Fin 5
σ₅ = cyclic-suc {4}

σ₅-HasOrderPerm : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm = cyclic-suc-HasOrderPerm {4}

cycle5-Linear : Linear 5 5
cycle5-Linear = basis-permutation-Linear σ₅

HasOrder-cycle5 : HasOrder (apply cycle5-Linear) 5
HasOrder-cycle5 = HasOrder-from-perm σ₅ 5 σ₅-HasOrderPerm
