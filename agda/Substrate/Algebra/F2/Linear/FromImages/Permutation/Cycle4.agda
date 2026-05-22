------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
--
-- σ₄ + cycle4-Linear + HasOrder-cycle4 as thin renamings of the
-- parametric Cyclic.{cyclic-suc, cyclic-Linear, cyclic-HasOrder}
-- at n = 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm; cyclic-Linear; cyclic-HasOrder)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₄ : Fin 4 → Fin 4
σ₄ = cyclic-suc {3}

σ₄-HasOrderPerm : HasOrderPerm σ₄ 4
σ₄-HasOrderPerm = cyclic-suc-HasOrderPerm {3}

cycle4-Linear : Linear 4 4
cycle4-Linear = cyclic-Linear {3}

HasOrder-cycle4 : HasOrder (apply cycle4-Linear) 4
HasOrder-cycle4 = cyclic-HasOrder {3}
