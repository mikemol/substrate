------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
--
-- σ₅ + cycle5-Linear + HasOrder-cycle5 as thin renamings of the
-- parametric Cyclic.{cyclic-suc, cyclic-Linear, cyclic-HasOrder}
-- at n = 4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm; cyclic-Linear; cyclic-HasOrder)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₅ : Fin 5 → Fin 5
σ₅ = cyclic-suc {4}

σ₅-HasOrderPerm : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm = cyclic-suc-HasOrderPerm {4}

cycle5-Linear : Linear 5 5
cycle5-Linear = cyclic-Linear {4}

HasOrder-cycle5 : HasOrder (apply cycle5-Linear) 5
HasOrder-cycle5 = cyclic-HasOrder {4}
