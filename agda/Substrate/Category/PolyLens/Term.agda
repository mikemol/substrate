------------------------------------------------------------------------
-- Substrate.Category.PolyLens.Term (T10)
-- Term-algebra encoding of dependent poly-lenses.
-- Since PolyLens = Poly._⇒_, the term datatype reuses Poly.Term (the witness
-- tower's free graded tower of combined generators).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PolyLens.Term where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Category.Poly.Term
  using (PolyTerm; []ₚ; _++ₚ_; poly-product)

-- A PolyLensTerm IS a PolyTerm (PolyLens = poly-morphism = poly-term).
PolyLensTerm : ℕ → Set
PolyLensTerm = PolyTerm

-- The empty poly-lens term (the identity morphism).
id-PolyLensTerm : PolyLensTerm 0
id-PolyLensTerm = []ₚ

_++ₗₚ_ : {m n : ℕ} → PolyLensTerm m → PolyLensTerm n → PolyLensTerm (m + n)
_++ₗₚ_ = _++ₚ_

infixr 4 _++ₗₚ_
