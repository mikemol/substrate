------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PuncturingAction
--
-- Defines: puncturing-action
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PuncturingAction where

open import Substrate.Groups.F2Cubed
open import Substrate.Algebra.SetoidGroup.Action
open import Substrate.Algebra.Group.ToSetoid
open import Substrate.Foundation.Eq
open import Substrate.Cocycles.F2CubedPuncturing.F23GroupSetoid
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingAct
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingActId
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingActDot



puncturing-action : Action F₂³ _≡_ F₂³-Group-Setoid PunctureIndex
puncturing-action = record
  { act    = puncturing-act
  ; act-id = puncturing-act-id
  ; act-∙  = puncturing-act-∙
  }
