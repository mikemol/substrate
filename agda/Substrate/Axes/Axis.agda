------------------------------------------------------------------------
-- Substrate.Axes.Axis
--
-- The four V₄ axes as a datatype.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.Axis where

data Axis : Set where      -- ⟦shape:cd5319ed D C S W⟧
  D C S W : Axis
