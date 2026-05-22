------------------------------------------------------------------------
-- Substrate.Category.Comonoid.Term (T12)
-- Term-algebra encoding of comonoid morphisms.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonoid.Term where

open import Substrate.Foundation.Level using (Level)

-- A comonoid morphism between two comonoid carriers (each carrier is
-- abstract). The term datatype indexes by (carrier, tensor-on-carrier).

-- For simplicity here we use Set-level indexing (concrete instances
-- at level zero).

data ComonoidGen (C : Set) : Set → Set → Set₁ where
  lift-comonoid-mor : (A B : Set) → ComonoidGen C A B

data ComonoidTerm (C : Set) : Set → Set → Set₁ where
  []  : {A : Set} → ComonoidTerm C A A
  _∷_ : {A B D : Set} →
        ComonoidGen C A B → ComonoidTerm C B D → ComonoidTerm C A D

infixr 5 _∷_

_++c_ : {C A B D : Set} →
        ComonoidTerm C A B → ComonoidTerm C B D → ComonoidTerm C A D
[]       ++c ys = ys
(x ∷ xs) ++c ys = x ∷ (xs ++c ys)

infixr 4 _++c_
