------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Record
--
-- Brick: typed 2-cell + step function + Witnessing tag + homomorphism
-- declaration. The homomorphism-tag is informational (names the
-- preserved algebraic structure); per-instance lemmas verify.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Record where

open import Substrate.Foundation.Product using (_×_)
open import Substrate.Pipeline.Brick.Witnessing using (Witnessing)
open import Substrate.Pipeline.Brick.Type using (BrickType)

-- ⟡set1-paydown: BrickType is now indexed by its four edges; Brick takes them as implicit params
-- (inferred from T) and reads them directly (the `open BrickType T public` re-export is gone —
-- there are no edge projections on the empty tag). Brick itself stays Set₁ (its homomorphism-tag :
-- Set field is the floor).
record Brick {D-in D-out S-in S-out : Set}
             (T : BrickType D-in D-out S-in S-out) : Set₁ where
  field
    witnesses : Witnessing
    step      : D-in × S-in → D-out × S-out
    homomorphism-tag : Set
