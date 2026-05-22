------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
--
-- σ₃ + cycle3-Linear + HasOrder-cycle3 as thin renamings of the
-- parametric Cyclic.{cyclic-suc, cyclic-Linear, cyclic-HasOrder}
-- at n = 2. No per-position enumeration; every witness comes free
-- from the parametric chain in
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic.
--
-- Per [[project-torsion-element-universal]]: substrate's first
-- non-involution torsion element. Generator of A₃ ⊂ S₃.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm; cyclic-Linear; cyclic-HasOrder)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₃ : Fin 3 → Fin 3
σ₃ = cyclic-suc {2}

σ₃-HasOrderPerm : HasOrderPerm σ₃ 3
σ₃-HasOrderPerm = cyclic-suc-HasOrderPerm {2}

cycle3-Linear : Linear 3 3
cycle3-Linear = cyclic-Linear {2}

HasOrder-cycle3 : HasOrder (apply cycle3-Linear) 3
HasOrder-cycle3 = cyclic-HasOrder {2}
