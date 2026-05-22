------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.IsSymmetric
--
-- IsSymmetric M : the predicate "M(i, j) ≡ M(j, i)". Orthogonal to
-- the BilinForm data; SymBilinForm = (M, symmetry-witness).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.IsSymmetric where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)

IsSymmetric : ∀ {n} → BilinForm n → Set
IsSymmetric {n} M = (i j : Fin n) → M i j ≡ M j i
