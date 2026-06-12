------------------------------------------------------------------------
-- Substrate.Probability.ConjugateMonad.Category (T18)
-- ConjugateMonad term-algebra category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.ConjugateMonad.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Probability.ConjugateMonad.Term
open import Substrate.Category.CategoryOf using (CategoryOf)

++ᶜ-identityˡ : {s₁ s₂ : ConjState} (t : ConjTerm s₁ s₂) → ([] ++ᶜ t) ≡ t
++ᶜ-identityˡ _ = refl

++ᶜ-identityʳ : {s₁ s₂ : ConjState} (t : ConjTerm s₁ s₂) → (t ++ᶜ []) ≡ t
++ᶜ-identityʳ []       = refl
++ᶜ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᶜ-identityʳ xs)

++ᶜ-assoc :
  {s₁ s₂ s₃ s₄ : ConjState}
  (t : ConjTerm s₁ s₂) (u : ConjTerm s₂ s₃) (v : ConjTerm s₃ s₄) →
  ((t ++ᶜ u) ++ᶜ v) ≡ (t ++ᶜ (u ++ᶜ v))
++ᶜ-assoc []       u v = refl
++ᶜ-assoc (x ∷ xs) u v = cong (x ∷_) (++ᶜ-assoc xs u v)

------------------------------------------------------------------------
-- GROUNDED: this IS a substrate-named `Category.CategoryOf` — objects =
-- ConjState, morphisms = ConjTerm, identity = [], composition = ++ᶜ. The
-- bare category laws above witness the named primitive. (compose g f =
-- f ++ᶜ g, so left-id/right-id pair with ++ᶜ-identityʳ/ˡ.)
------------------------------------------------------------------------

ConjugateCategory : CategoryOf
ConjugateCategory = record
  { Obj      = ConjState
  ; Mor      = ConjTerm
  ; id       = λ _ → []
  ; compose  = λ g f → f ++ᶜ g
  ; left-id  = ++ᶜ-identityʳ
  ; right-id = ++ᶜ-identityˡ
  ; assoc    = ++ᶜ-assoc
  }
