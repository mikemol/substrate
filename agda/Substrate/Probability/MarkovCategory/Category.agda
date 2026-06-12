------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Category
--
-- T2: the Markov category presented as a term-algebra category.
--
-- Objects = Markov objects; Morphisms = MarkovTerm; identity = [];
-- composition = list concatenation. Category laws hold STRUCTURALLY:
--   * left identity:  [] ++ₘ t ≡ t      (by definition)
--   * right identity: t ++ₘ [] ≡ t      (by induction)
--   * associativity:  (t ++ₘ u) ++ₘ v ≡ t ++ₘ (u ++ₘ v) (by induction)
--
-- This mirrors Substrate.Category.UniversalProperty.Category exactly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Category where

open import Substrate.Foundation.Eq
  using (_≡_; refl; cong)

open import Substrate.Probability.MarkovCategory.Term
open import Substrate.Category.CategoryOf using (CategoryOf)

------------------------------------------------------------------------
-- Identity and composition at the term level.

id-MarkovTerm : (X : Obj) → MarkovTerm X X
id-MarkovTerm _ = []

compose-MarkovTerm :
  {X Y Z : Obj} →
  MarkovTerm Y Z → MarkovTerm X Y → MarkovTerm X Z
compose-MarkovTerm g f = f ++ₘ g

------------------------------------------------------------------------
-- Category laws (structural, mechanical induction).

++ₘ-identityˡ :
  {X Y : Obj} (t : MarkovTerm X Y) → ([] ++ₘ t) ≡ t
++ₘ-identityˡ _ = refl

++ₘ-identityʳ :
  {X Y : Obj} (t : MarkovTerm X Y) → (t ++ₘ []) ≡ t
++ₘ-identityʳ []       = refl
++ₘ-identityʳ (x ∷ xs) = cong (x ∷_) (++ₘ-identityʳ xs)

++ₘ-assoc :
  {X Y Z W : Obj}
  (t : MarkovTerm X Y) (u : MarkovTerm Y Z) (v : MarkovTerm Z W) →
  ((t ++ₘ u) ++ₘ v) ≡ (t ++ₘ (u ++ₘ v))
++ₘ-assoc []       u v = refl
++ₘ-assoc (x ∷ xs) u v = cong (x ∷_) (++ₘ-assoc xs u v)

------------------------------------------------------------------------
-- GROUNDED: this IS a substrate-named `Category.CategoryOf` — objects = Obj,
-- morphisms = MarkovTerm, identity = [], composition = ++ₘ. The bare category
-- laws above witness the named primitive — the morphism layer the
-- categorical-name-first discipline asks a "category" to carry. (compose g f =
-- f ++ₘ g, so left-id/right-id pair with ++ₘ-identityʳ/ˡ.)
------------------------------------------------------------------------

MarkovCategory : CategoryOf
MarkovCategory = record
  { Obj      = Obj
  ; Mor      = MarkovTerm
  ; id       = id-MarkovTerm
  ; compose  = compose-MarkovTerm
  ; left-id  = ++ₘ-identityʳ
  ; right-id = ++ₘ-identityˡ
  ; assoc    = ++ₘ-assoc
  }
