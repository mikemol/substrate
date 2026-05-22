------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Category (T20)
-- DFT term-algebra category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Category.DiscreteFourierTransform.Term

++ᶠ-identityˡ : {s₁ s₂ : DFTContext} (t : DFTTerm s₁ s₂) → ([] ++ᶠ t) ≡ t
++ᶠ-identityˡ _ = refl

++ᶠ-identityʳ : {s₁ s₂ : DFTContext} (t : DFTTerm s₁ s₂) → (t ++ᶠ []) ≡ t
++ᶠ-identityʳ []       = refl
++ᶠ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᶠ-identityʳ xs)

++ᶠ-assoc :
  {s₁ s₂ s₃ s₄ : DFTContext}
  (t : DFTTerm s₁ s₂) (u : DFTTerm s₂ s₃) (v : DFTTerm s₃ s₄) →
  ((t ++ᶠ u) ++ᶠ v) ≡ (t ++ᶠ (u ++ᶠ v))
++ᶠ-assoc []       u v = refl
++ᶠ-assoc (x ∷ xs) u v = cong (x ∷_) (++ᶠ-assoc xs u v)
