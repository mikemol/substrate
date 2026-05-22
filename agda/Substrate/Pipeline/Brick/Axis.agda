------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Axis
--
-- The three brick sorts (Axes): D (data), S (state), C (compute).
-- Tags for the third-axis-witnesses of the six morphisms.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Axis where

data Axis : Set where
  𝔻 : Axis  -- Data witnesses
  𝕊 : Axis  -- State witnesses
  ℂ : Axis  -- Compute witnesses
