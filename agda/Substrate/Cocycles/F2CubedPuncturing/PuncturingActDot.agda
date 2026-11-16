------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PuncturingActDot
--
-- Defines: puncturing-act-∙
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PuncturingActDot where

open import Substrate.Groups.F2Cubed
open import Substrate.Foundation.Eq
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingAct



puncturing-act-∙ :
  (g h : F₂³) (p : PunctureIndex) →
  puncturing-act (g + h) p ≡ puncturing-act g (puncturing-act h p)
puncturing-act-∙ = +-assoc
