------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.Type
--
-- Sequent S: the structural-rule record over a SequentType. Has a
-- rule tag + derivation A → B. State is trivially ⊤ on both edges.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.Type where

open import Substrate.Pipeline.Sequent.SequentRule using (SequentRule)
open import Substrate.Pipeline.Sequent.SequentType using (SequentType)

record Sequent (S : SequentType) : Set₁ where
  open SequentType S
  field
    rule       : SequentRule
    derivation : A → B
