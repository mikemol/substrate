------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Axis
--
-- The three brick sorts (Axes): D (data), S (state), C (compute).
-- Tags for the third-axis-witnesses of the six morphisms.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Axis where

data BrickAxis : Set where      -- ⟦shape:cacdc9fc 𝔻,𝕊,ℂ⟧
  𝔻 : BrickAxis  -- Data witnesses
  𝕊 : BrickAxis  -- State witnesses
  ℂ : BrickAxis  -- Compute witnesses
