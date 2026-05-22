------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.PredictorSurprise
--
-- Example 3: predictor.surprise (read-only state query).
-- D-in = Char → D-out = ℕ (surprise in bits, simplified to ℕ).
-- S unchanged (S-out = S-in). Witnesses S⇒D; preserves Shannon
-- information modulo log.
--
-- Module-parametric on the runtime types (Char, Counts,
-- surprise-bits). The Char + Counts types are shared with
-- PredictorUpdate; the parent Examples module threads the same
-- choices through both.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Pipeline.Brick

module Substrate.Pipeline.Examples.PredictorSurprise
  (Char   : Set)
  (Counts : Set)
  (surprise-bits : Counts → Char → ℕ)
  where

open import Substrate.Foundation.Product using (_,_)

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
