------------------------------------------------------------------------
-- Substrate.Category.GroupoidCardinality
--
-- S9 of the S-arc. Groupoid cardinality: |G| = Σ_x 1/|Aut(x)| summed
-- over isomorphism classes. Per Baez-Dolan, this is the canonical
-- "cardinality" for higher-categorical / homotopy types.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GroupoidCardinality where

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

record GroupoidCardinality
  {ℓO ℓM : Level}
  (G : CategoryOf {ℓO} {ℓM})
  (Card : Set) : Set where
  field
    cardinality : Card
    -- The cardinality computation requires a concrete rationals-style
    -- target; user supplies the type + the value.
