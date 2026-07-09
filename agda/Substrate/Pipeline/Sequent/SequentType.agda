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

-- ⟡set1-paydown: BrickType edges are now type indices — moved into the annotation; body is the tag.
sequent→BrickType : {A B : Set} → SequentType A B → BrickType A B ⊤ ⊤
sequent→BrickType _ = record {}
