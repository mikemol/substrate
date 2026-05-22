------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle2
--
-- σ₂ + cycle2-Linear + HasOrder-cycle2 as thin renamings of the
-- parametric Cyclic.{cyclic-suc, cyclic-Linear, cyclic-HasOrder}
-- at n = 1. σ₂ is the swap: zero ↔ suc zero.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle2 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm; cyclic-Linear; cyclic-HasOrder)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₂ : Fin 2 → Fin 2
σ₂ = cyclic-suc {1}

σ₂-HasOrderPerm : HasOrderPerm σ₂ 2
σ₂-HasOrderPerm = cyclic-suc-HasOrderPerm {1}

cycle2-Linear : Linear 2 2
cycle2-Linear = cyclic-Linear {1}

HasOrder-cycle2 : HasOrder (apply cycle2-Linear) 2
HasOrder-cycle2 = cyclic-HasOrder {1}
