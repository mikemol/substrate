------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.Type
--
-- BrickType: the typed-edge signature of a brick (4 typed edges:
-- D-in, D-out, S-in, S-out).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.Type where

-- ⟡set1-paydown: all four typed edges are Set-valued, forcing BrickType : Set₁. Parameterize each
-- into a module param; the record becomes the (empty) type-level tag over the four edges and lives
-- in Set. Consumers write `BrickType D-in D-out S-in S-out`; a brick type is constructed as
-- `record {}` under that annotation, and its edges are read off the type indices (not projections).
module _ (D-in D-out S-in S-out : Set) where
  record BrickType : Set where
