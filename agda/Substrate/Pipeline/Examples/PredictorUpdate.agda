------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.PredictorUpdate
--
-- Example 2: predictor.update (Trigram). State update.
-- D-in = Char → D-out = ⊤ (write-only). S evolves via update-counts.
-- Witnesses D⇒S; homomorphism preserves the free commutative monoid
-- on counts (update = monoid concatenation by a singleton).
--
-- Module-parametric on the runtime types per the substrate's
-- standard polymorphism pattern (see e.g. Substrate.Algebra.Lie.sl2).
-- Concrete runtime implementations live in scratch/eliza/eliza/ and
-- supply (Char, Counts, update-counts).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Pipeline.Brick

module Substrate.Pipeline.Examples.PredictorUpdate
  (Char   : Set)
  (Counts : Set)
  (update-counts : Counts → Char → Counts)
  where

open import Substrate.Foundation.Product using (_,_)

-- ⟡set1-paydown: BrickType edges are now type indices — moved into the annotation; body is the tag.
PredictorUpdate-Type : BrickType Char ⊤ Counts Counts
PredictorUpdate-Type = record {}

record Preserves-CountMonoid : Set where

predictor-update : Brick PredictorUpdate-Type Preserves-CountMonoid
predictor-update = record
  { witnesses = D⇒S
  ; step      = λ (ch , s) → tt , update-counts s ch
  }
