------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.SequentFixed
--
-- SequentFixed A: a fixed-point Sequent — endofunction A → A plus
-- canonical-form spec plus the specific-derivation obligation.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.SequentFixed where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Pipeline.Sequent.CanonicalSpec using (CanonicalSpec)

record SequentFixed (A : Set) : Set₁ where
  field
    derivation : A → A
    spec       : CanonicalSpec A
    obligation : (a : A) → CanonicalSpec.Canonical spec a
                          → derivation a ≡ a
