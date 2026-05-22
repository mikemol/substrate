------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Witnessing
--
-- The six oriented morphisms among the three brick sorts (D, S, C),
-- each witnessed by the third sort. D⇒S/S⇒D are witnessed by C;
-- D⇒C/C⇒D by S; S⇒C/C⇒S by D.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Witnessing where

data Witnessing : Set where
  D⇒S : Witnessing  -- write
  S⇒D : Witnessing  -- read
  D⇒C : Witnessing  -- data selects compute
  C⇒D : Witnessing  -- compute produces data
  S⇒C : Witnessing  -- state dispatches compute
  C⇒S : Witnessing  -- compute mutates state
