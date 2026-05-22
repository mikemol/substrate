------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Type
--
-- BrickType: the typed-edge signature of a brick (4 typed edges:
-- D-in, D-out, S-in, S-out).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Type where

record BrickType : Set₁ where
  field
    D-in  : Set
    D-out : Set
    S-in  : Set
    S-out : Set
