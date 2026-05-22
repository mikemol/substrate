------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.EmissionSource
--
-- Two-element data type tagging where an emission's payload comes from:
-- a rule body slice (QUOT-style) or arbitrary recent history (LZ77-style).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.EmissionSource where

data EmissionSource : Set where
  Rule    : EmissionSource
  Recent  : EmissionSource
