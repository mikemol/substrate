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

-- ⟡set1-paydown: the Set-valued family `Canonical : A → Set` was a FIELD, forcing
-- CanonicalSpec to Set₁. Lift it (with the carrier A) to module params → the record
-- lives in Set. Consumers write `CanonicalSpec A Canonical` and reach the predicate
-- through the in-scope `Canonical` param (replacing the removed `CanonicalSpec.Canonical
-- spec` projection).
module _ (A : Set) (Canonical : A → Set) where

  record CanonicalSpec : Set where
    field
      canonical-fixed : (derivation : A → A)
                      → (a : A)
                      → Canonical a
                      → derivation a ≡ a
