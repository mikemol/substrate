------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Category (T22)
-- PontryaginDual character group as a term-algebra (= cyclic word algebra).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Category where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Algebra.PontryaginDual.Term

++ᵪ-identityˡ : {n : ℕ} (t : CharTerm n) → ([] ++ᵪ t) ≡ t
++ᵪ-identityˡ _ = refl

++ᵪ-identityʳ : {n : ℕ} (t : CharTerm n) → (t ++ᵪ []) ≡ t
++ᵪ-identityʳ []       = refl
++ᵪ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᵪ-identityʳ xs)

++ᵪ-assoc :
  {n : ℕ}
  (t u v : CharTerm n) →
  ((t ++ᵪ u) ++ᵪ v) ≡ (t ++ᵪ (u ++ᵪ v))
++ᵪ-assoc []       u v = refl
++ᵪ-assoc (x ∷ xs) u v = cong (x ∷_) (++ᵪ-assoc xs u v)
