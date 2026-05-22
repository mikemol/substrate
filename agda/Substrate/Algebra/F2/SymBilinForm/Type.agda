------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.Type
--
-- SymBilinForm n : the subtype of symmetric forms.
-- bilin-of / is-symmetric : the Σ projections.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.Type where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; proj₁; proj₂)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.IsSymmetric using (IsSymmetric)

SymBilinForm : ℕ → Set
SymBilinForm n = Σ (BilinForm n) IsSymmetric

bilin-of : ∀ {n} → SymBilinForm n → BilinForm n
bilin-of = proj₁

is-symmetric : ∀ {n} (M : SymBilinForm n) → IsSymmetric (bilin-of M)
is-symmetric = proj₂
