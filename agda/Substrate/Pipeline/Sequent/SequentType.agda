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

-- ⟡set1-paydown: parameterize A B
record SequentType (A B : Set) : Set where

sequent→BrickType : {A B : Set} → SequentType A B → BrickType
sequent→BrickType {A} {B} _ = record
  { D-in  = A
  ; D-out = B
  ; S-in  = ⊤
  ; S-out = ⊤
  }
