------------------------------------------------------------------------
-- Substrate.Category.Poly.Term
--
-- T7: term-algebra encoding of polynomial-functor morphisms.
--
-- A PolyTerm P Q is a sequence of polymorphism generators stacking
-- from P to Q. Each generator is a named elementary poly-move.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Term where

open import Substrate.Category.Poly using (Poly)

data PolyGen : Poly → Poly → Set₁ where
  lift-poly : (P Q : Poly) → PolyGen P Q

data PolyTerm : Poly → Poly → Set₁ where
  []  : {P : Poly} → PolyTerm P P
  _∷_ : {P Q R : Poly} →
        PolyGen P Q → PolyTerm Q R → PolyTerm P R

infixr 5 _∷_

_++ₚ_ : {P Q R : Poly} → PolyTerm P Q → PolyTerm Q R → PolyTerm P R
[]       ++ₚ ys = ys
(x ∷ xs) ++ₚ ys = x ∷ (xs ++ₚ ys)

infixr 4 _++ₚ_
