------------------------------------------------------------------------
-- Substrate.Category.Poly.Category (T8)
-- Poly as a term-algebra category. Laws hold structurally.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Category.Poly using (Poly)
open import Substrate.Category.Poly.Term

id-PolyTerm : (P : Poly) → PolyTerm P P
id-PolyTerm _ = []

++ₚ-identityˡ : {P Q : Poly} (t : PolyTerm P Q) → ([] ++ₚ t) ≡ t
++ₚ-identityˡ _ = refl

++ₚ-identityʳ : {P Q : Poly} (t : PolyTerm P Q) → (t ++ₚ []) ≡ t
++ₚ-identityʳ []       = refl
++ₚ-identityʳ (x ∷ xs) = cong (x ∷_) (++ₚ-identityʳ xs)

++ₚ-assoc :
  {P Q R S : Poly}
  (t : PolyTerm P Q) (u : PolyTerm Q R) (v : PolyTerm R S) →
  ((t ++ₚ u) ++ₚ v) ≡ (t ++ₚ (u ++ₚ v))
++ₚ-assoc []       u v = refl
++ₚ-assoc (x ∷ xs) u v = cong (x ∷_) (++ₚ-assoc xs u v)
