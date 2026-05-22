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

open import Substrate.Foundation.Eq using (_≡_; _≢_)

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
