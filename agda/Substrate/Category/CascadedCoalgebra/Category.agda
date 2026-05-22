------------------------------------------------------------------------
-- Substrate.Category.CascadedCoalgebra.Category (T16)
-- Cascaded-coalgebra category from term-algebra.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CascadedCoalgebra.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Category.CascadedCoalgebra.Term

++ᶜᶜ-identityˡ : {s₁ s₂ : CascadeState} (t : CascadeTerm s₁ s₂) → ([] ++ᶜᶜ t) ≡ t
++ᶜᶜ-identityˡ _ = refl

++ᶜᶜ-identityʳ : {s₁ s₂ : CascadeState} (t : CascadeTerm s₁ s₂) → (t ++ᶜᶜ []) ≡ t
++ᶜᶜ-identityʳ []       = refl
++ᶜᶜ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᶜᶜ-identityʳ xs)

++ᶜᶜ-assoc :
  {s₁ s₂ s₃ s₄ : CascadeState}
  (t : CascadeTerm s₁ s₂) (u : CascadeTerm s₂ s₃) (v : CascadeTerm s₃ s₄) →
  ((t ++ᶜᶜ u) ++ᶜᶜ v) ≡ (t ++ᶜᶜ (u ++ᶜᶜ v))
++ᶜᶜ-assoc []       u v = refl
++ᶜᶜ-assoc (x ∷ xs) u v = cong (x ∷_) (++ᶜᶜ-assoc xs u v)
