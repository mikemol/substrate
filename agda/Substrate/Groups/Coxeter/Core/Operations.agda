------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.Operations
--
-- Section 1 of Coxeter.Core. The group operations defined up to
-- normalization equivalence:
--   _·_  : composition modulo normalize.
--   _≈_  : equality on normal forms.
--   _≉_  : inequality on normal forms.
--   ε    : the carrier identity (rebound from ε-in for re-export).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}


-- ⚑ THE SPLIT EMITTED THIS LEAF WITH NO IMPORTS AT ALL, yet its body uses
-- `_≡_` (:33) and `_≢_` (:36).  Both resolve unambiguously via def_index —
-- `Foundation.Eq` and `Foundation.Eq.Neq` — so this is a missing edge, not
-- an ambiguity.  Placed ABOVE the header for the same reason as the sibling
-- leaves: cheap, and correct whether the name is used in the telescope or
-- the body.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.List

module Substrate.Groups.Coxeter.Core.Operations
  (Word : Set)
  (_++_ : Word → Word → Word)
  (ε-in : Word)
  (normalize : Word → Word)
  where

ε : Word
ε = ε-in

infixl 7 _·_
infix  4 _≈_
infix  4 _≉_

_·_ : Word → Word → Word
w₁ · w₂ = normalize (w₁ ++ w₂)

_≈_ : Word → Word → Set
w₁ ≈ w₂ = normalize w₁ ≡ normalize w₂

_≉_ : Word → Word → Set
w₁ ≉ w₂ = normalize w₁ ≢ normalize w₂
