------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PuncturingAct
--
-- Defines: puncturing-act
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PuncturingAct where

open import Substrate.Groups.F2Cubed
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex



------------------------------------------------------------------------
-- The action: F_2³ acts on PunctureIndex by translation (XOR).
------------------------------------------------------------------------

puncturing-act : F₂³ → PunctureIndex → PunctureIndex
puncturing-act g p = g + p
