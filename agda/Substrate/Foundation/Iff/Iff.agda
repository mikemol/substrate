------------------------------------------------------------------------
-- Logical equivalence of TYPES, at Set₀.
-- Context: Substrate/Foundation/Iff/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Iff.Iff where

open import Substrate.Foundation.Product

infix 3 _⇔_

_⇔_ : Set → Set → Set
A ⇔ B = (A → B) × (B → A)
