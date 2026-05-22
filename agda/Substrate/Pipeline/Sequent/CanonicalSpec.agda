------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.CanonicalSpec
--
-- CanonicalSpec A: the canonical-form predicate + fixed-point
-- obligation. A derivation respects canonical forms iff it fixes
-- elements that satisfy the predicate.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.CanonicalSpec where

open import Substrate.Foundation.Eq using (_≡_)

record CanonicalSpec (A : Set) : Set₁ where
  field
    Canonical       : A → Set
    canonical-fixed : (derivation : A → A)
                    → (a : A)
                    → Canonical a
                    → derivation a ≡ a
