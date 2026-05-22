------------------------------------------------------------------------
-- Substrate.Category.PolyLens.Term (T10)
-- Term-algebra encoding of dependent poly-lenses.
-- Since PolyLens = Poly._⇒_, the term datatype reuses Poly.Term.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PolyLens.Term where

open import Substrate.Category.Poly using (Poly)
open import Substrate.Category.Poly.Term public
  using (PolyGen; PolyTerm; []; _∷_; _++ₚ_; lift-poly)

-- A PolyLensTerm IS a PolyTerm (PolyLens = poly-morphism = poly-term).

PolyLensTerm : Poly → Poly → Set₁
PolyLensTerm = PolyTerm

id-PolyLensTerm : (P : Poly) → PolyLensTerm P P
id-PolyLensTerm _ = []

_++ₗₚ_ : {P Q R : Poly} → PolyLensTerm P Q → PolyLensTerm Q R → PolyLensTerm P R
_++ₗₚ_ = _++ₚ_
