------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.ChooseRotation
--
-- Example 4: A chooser — selects which rotation to apply.
-- D-in = Window → D-out = RotIdx. S evolves (cache may grow).
-- Witnesses D⇒C (the window selects the compute); preserves
-- selection ranking under predictor evolution.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.ChooseRotation where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Pipeline.Brick

postulate
  Window    : Set
  RotIdx    : Set
  Predictor : Set
  Cache     : Set
  choose-rotation-impl
    : Window → Predictor × Cache → RotIdx × (Predictor × Cache)

Chooser-Type : BrickType
Chooser-Type = record
  { D-in  = Window
  ; D-out = RotIdx
  ; S-in  = Predictor × Cache
  ; S-out = Predictor × Cache
  }

record Preserves-Ranking : Set where

choose-rotation : Brick Chooser-Type
choose-rotation = record
  { witnesses = D⇒C
  ; step      = λ (w , s) → choose-rotation-impl w s
  ; homomorphism-tag = Preserves-Ranking
  }
