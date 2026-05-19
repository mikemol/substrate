------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-HasOrderPerm
--
-- HasOrderPerm σ₅ 5 via the Z5-Coxeter relation `a⁵ = ε`.
--
-- Mirror of Z3-Coxeter-HasOrderPerm / Z4 sliced at n=5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-HasOrderPerm where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
  using (σ₅)

σ₅-HasOrderPerm-from-Z5-Coxeter : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm-from-Z5-Coxeter zero                                  = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc zero)                            = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc (suc zero))                      = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc (suc (suc zero)))                = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc (suc (suc (suc zero))))          = refl
