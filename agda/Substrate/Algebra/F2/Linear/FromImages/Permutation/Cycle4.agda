------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
--
-- σ₄ on Fin 4 + HasOrderPerm, as a thin instance of
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic.
--
-- σ₄ = cyclic-suc {3}; HasOrderPerm comes free.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4 where

open import Substrate.Foundation.Fin using (Fin)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₄ : Fin 4 → Fin 4
σ₄ = cyclic-suc {3}

σ₄-HasOrderPerm : HasOrderPerm σ₄ 4
σ₄-HasOrderPerm = cyclic-suc-HasOrderPerm {3}

cycle4-Linear : Linear 4 4
cycle4-Linear = basis-permutation-Linear σ₄

HasOrder-cycle4 : HasOrder (apply cycle4-Linear) 4
HasOrder-cycle4 = HasOrder-from-perm σ₄ 4 σ₄-HasOrderPerm
