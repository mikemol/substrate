------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Category
--
-- T5: stochastic-lens category as term-algebra.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Category where

open import Substrate.Foundation.Eq
  using (_≡_; refl; cong)

open import Substrate.Category.StochasticLens.Term

id-LensTerm : (t : LensTriple) → LensTerm t t
id-LensTerm _ = []

++ₗ-identityˡ :
  {t₁ t₂ : LensTriple} (s : LensTerm t₁ t₂) → ([] ++ₗ s) ≡ s
++ₗ-identityˡ _ = refl

++ₗ-identityʳ :
  {t₁ t₂ : LensTriple} (s : LensTerm t₁ t₂) → (s ++ₗ []) ≡ s
++ₗ-identityʳ []       = refl
++ₗ-identityʳ (x ∷ xs) = cong (x ∷_) (++ₗ-identityʳ xs)

++ₗ-assoc :
  {t₁ t₂ t₃ t₄ : LensTriple}
  (s : LensTerm t₁ t₂) (u : LensTerm t₂ t₃) (v : LensTerm t₃ t₄) →
  ((s ++ₗ u) ++ₗ v) ≡ (s ++ₗ (u ++ₗ v))
++ₗ-assoc []       u v = refl
++ₗ-assoc (x ∷ xs) u v = cong (x ∷_) (++ₗ-assoc xs u v)
