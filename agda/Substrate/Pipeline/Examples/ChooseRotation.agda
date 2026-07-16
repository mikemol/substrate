------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.ChooseRotation
--
-- Example 4: A chooser — selects which rotation to apply.
-- D-in = Window → D-out = RotIdx. S evolves (cache may grow).
-- Witnesses D⇒C (the window selects the compute); preserves
-- selection ranking under predictor evolution.
--
-- Module-parametric on the runtime types per the substrate's
-- standard polymorphism pattern. Concrete runtime implementations
-- live in scratch/eliza/eliza/.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Product using (_×_)
open import Substrate.Pipeline.Brick

module Substrate.Pipeline.Examples.ChooseRotation
  (Window    : Set)
  (RotIdx    : Set)
  (Predictor : Set)
  (Cache     : Set)
  (choose-rotation-impl
    : Window → (Predictor × Cache) → (RotIdx × (Predictor × Cache)))
  where

open import Substrate.Foundation.Product using (_,_)

-- ⟡set1-paydown: BrickType edges are now type indices — moved into the annotation; body is the tag.
Chooser-Type : BrickType Window RotIdx (Predictor × Cache) (Predictor × Cache)
Chooser-Type = record {}

record Preserves-Ranking : Set where

choose-rotation : Brick Chooser-Type Preserves-Ranking
choose-rotation = record
  { witnesses = D⇒C
  ; step      = λ (w , s) → choose-rotation-impl w s
  }
