------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PunctureIndex
--
-- Defines: PunctureIndex
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PunctureIndex where

open import Substrate.Groups.F2Cubed



------------------------------------------------------------------------
-- Puncturing index space: the 8 coordinate puncturings of RM(1, 3).
--
-- Identified with F_2³ via the bit-pattern of the punctured coordinate.
-- This is a type-level distinction from F_2³-as-group: F_2³ here is
-- the underlying SET (the 8 puncturings); the F_2³ in F₂³-Group is the
-- gauge GROUP. They share carriers because the gauge acts on itself
-- by translation (regular representation).
------------------------------------------------------------------------

PunctureIndex : Set
PunctureIndex = F₂³
