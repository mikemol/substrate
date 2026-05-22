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

record Brick (T : BrickType) : Set₁ where
  open BrickType T public
  field
    witnesses : Witnessing
    step      : D-in × S-in → D-out × S-out
    homomorphism-tag : Set
