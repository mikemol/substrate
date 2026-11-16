------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PuncturingActId
--
-- Defines: puncturing-act-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PuncturingActId where

open import Substrate.Groups.F2Cubed
open import Substrate.Foundation.Eq
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingAct



puncturing-act-id : (p : PunctureIndex) → puncturing-act ε p ≡ p
puncturing-act-id = +-identityˡ
