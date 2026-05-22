------------------------------------------------------------------------
-- Substrate.Category.Comonoid.Category (T13)
-- Comonoid as a term-algebra category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonoid.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Category.Comonoid.Term

++c-identityˡ : {C A B : Set} (t : ComonoidTerm C A B) → ([] ++c t) ≡ t
++c-identityˡ _ = refl

++c-identityʳ : {C A B : Set} (t : ComonoidTerm C A B) → (t ++c []) ≡ t
++c-identityʳ []       = refl
++c-identityʳ (x ∷ xs) = cong (x ∷_) (++c-identityʳ xs)

++c-assoc :
  {C A B D E : Set}
  (t : ComonoidTerm C A B) (u : ComonoidTerm C B D) (v : ComonoidTerm C D E) →
  ((t ++c u) ++c v) ≡ (t ++c (u ++c v))
++c-assoc []       u v = refl
++c-assoc (x ∷ xs) u v = cong (x ∷_) (++c-assoc xs u v)
