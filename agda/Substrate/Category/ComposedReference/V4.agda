------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.V4
--
-- Local V₄ data type for ComposedReference's action algebra. Mirrors
-- Substrate.Groups.V4 but kept local to keep this primitive
-- dependency-light (no group-axiom infrastructure needed here).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.V4 where

data V₄ : Set where
  e α β γ : V₄
