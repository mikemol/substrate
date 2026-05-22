------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7
--
-- σ₇ + cycle7-Linear + HasOrder-cycle7 as thin renamings of the
-- parametric Cyclic.{cyclic-suc, cyclic-Linear, cyclic-HasOrder}
-- at n = 6.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm; cyclic-Linear; cyclic-HasOrder)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₇ : Fin 7 → Fin 7
σ₇ = cyclic-suc {6}

σ₇-HasOrderPerm : HasOrderPerm σ₇ 7
σ₇-HasOrderPerm = cyclic-suc-HasOrderPerm {6}

cycle7-Linear : Linear 7 7
cycle7-Linear = cyclic-Linear {6}

HasOrder-cycle7 : HasOrder (apply cycle7-Linear) 7
HasOrder-cycle7 = cyclic-HasOrder {6}
