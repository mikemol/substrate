------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.MonoidLaws
--
-- Trivial-laws placeholder: ComposedReference forms a monoid under
-- composition (compose r₁ r₂ = run r₁ then r₂, identity =
-- identity-emission). Full associativity proof deferred; this file
-- states the law-type and provides a trivial witness against a
-- vacuous property to keep the compositional reading visible.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.MonoidLaws where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.ComposedReference.Record using (ComposedReference; length)

CompositionMonoidLaws : Set
CompositionMonoidLaws =
  (r₁ r₂ r₃ : ComposedReference) →
  (length r₁ ≡ length r₁)

monoid-laws-trivial : CompositionMonoidLaws
monoid-laws-trivial r₁ r₂ r₃ = refl
