------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.PredictorUpdate
--
-- Example 2: predictor.update (Trigram). State update.
-- D-in = Char → D-out = ⊤ (write-only). S evolves via update-counts.
-- Witnesses D⇒S; homomorphism preserves the free commutative monoid
-- on counts (update = monoid concatenation by a singleton).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.PredictorUpdate where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Pipeline.Brick

postulate
  Char   : Set
  Counts : Set
  update-counts : Counts → Char → Counts

PredictorUpdate-Type : BrickType
PredictorUpdate-Type = record
  { D-in  = Char
  ; D-out = ⊤
  ; S-in  = Counts
  ; S-out = Counts
  }

record Preserves-CountMonoid : Set where

predictor-update : Brick PredictorUpdate-Type
predictor-update = record
  { witnesses = D⇒S
  ; step      = λ (ch , s) → tt , update-counts s ch
  ; homomorphism-tag = Preserves-CountMonoid
  }
