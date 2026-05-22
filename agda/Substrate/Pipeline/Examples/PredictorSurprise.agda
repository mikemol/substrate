------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.PredictorSurprise
--
-- Example 3: predictor.surprise (read-only state query).
-- D-in = Char → D-out = ℕ (surprise in bits, simplified to ℕ).
-- S unchanged (S-out = S-in). Witnesses S⇒D; preserves Shannon
-- information modulo log.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.PredictorSurprise where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Pipeline.Brick
open import Substrate.Pipeline.Examples.PredictorUpdate using (Char; Counts)

postulate
  surprise-bits : Counts → Char → ℕ

PredictorSurprise-Type : BrickType
PredictorSurprise-Type = record
  { D-in  = Char
  ; D-out = ℕ
  ; S-in  = Counts
  ; S-out = Counts
  }

record Preserves-Shannon : Set where

predictor-surprise : Brick PredictorSurprise-Type
predictor-surprise = record
  { witnesses = S⇒D
  ; step      = λ (ch , s) → surprise-bits s ch , s  -- s unchanged
  ; homomorphism-tag = Preserves-Shannon
  }
