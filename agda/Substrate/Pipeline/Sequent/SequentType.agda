------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.SequentType
--
-- SequentType: the signature of a sequent (A → B as a record).
-- sequent→BrickType lifts a SequentType into a stateless BrickType
-- (S-in = S-out = ⊤).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.SequentType where

open import Substrate.Pipeline.Brick

record SequentType : Set₁ where
  field
    A : Set
    B : Set

sequent→BrickType : SequentType → BrickType
sequent→BrickType S = record
  { D-in  = SequentType.A S
  ; D-out = SequentType.B S
  ; S-in  = ⊤
  ; S-out = ⊤
  }
