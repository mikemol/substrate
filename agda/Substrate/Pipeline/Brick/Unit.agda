------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Unit
--
-- The local ⊤ unit for trivial brick edges (pure transforms /
-- read-only / no-state). Kept local to avoid Foundation.Unit
-- coupling at the brick-framework layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Unit where

record ⊤ : Set where
  constructor tt
