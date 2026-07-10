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

-- ⟡set1-paydown: cascades from CanonicalSpec — the predicate `Canonical` is now a
-- module param (was `CanonicalSpec.Canonical spec`). Take (A, Canonical) as params so
-- `spec : CanonicalSpec A Canonical` and the obligation refer to the in-scope Canonical;
-- SequentFixed drops from Set₁ to Set. Consumers write `SequentFixed A Canonical`.
module _ (A : Set) (Canonical : A → Set) where

  record SequentFixed : Set where
    field
      derivation : A → A
      spec       : CanonicalSpec A Canonical
      obligation : (a : A) → Canonical a
                            → derivation a ≡ a
