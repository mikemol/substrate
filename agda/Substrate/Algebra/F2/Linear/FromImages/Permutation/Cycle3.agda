------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
--
-- σ₃ on Fin 3 + HasOrderPerm, as a thin instance of
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic.
--
-- σ₃ = cyclic-suc {2}; HasOrderPerm comes free (no per-position
-- enumeration). The cycle3-Linear + HasOrder-cycle3 lift uses the
-- substrate's basis-permutation-Linear + HasOrder-from-perm machinery.
--
-- Per [[project-torsion-element-universal]]: substrate's first
-- non-involution torsion element. Generator of A₃ ⊂ S₃.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3 where

open import Substrate.Foundation.Fin using (Fin)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

σ₃ : Fin 3 → Fin 3
σ₃ = cyclic-suc {2}

σ₃-HasOrderPerm : HasOrderPerm σ₃ 3
σ₃-HasOrderPerm = cyclic-suc-HasOrderPerm {2}

cycle3-Linear : Linear 3 3
cycle3-Linear = basis-permutation-Linear σ₃

HasOrder-cycle3 : HasOrder (apply cycle3-Linear) 3
HasOrder-cycle3 = HasOrder-from-perm σ₃ 3 σ₃-HasOrderPerm
