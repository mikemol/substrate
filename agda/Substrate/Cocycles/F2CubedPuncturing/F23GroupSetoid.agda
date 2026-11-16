------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.F23GroupSetoid
--
-- Defines: F₂³-Group-Setoid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.F23GroupSetoid where

open import Substrate.Groups.F2Cubed
open import Substrate.Algebra.Group.ToSetoid



F₂³-Group-Setoid = to-setoid F₂³-Group
