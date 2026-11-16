------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.FiberIsTorsor
--
-- Defines: fiber-is-torsor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.FiberIsTorsor where

open import Substrate.Foundation.Product
open import Substrate.Groups.F2Cubed
open import Substrate.Algebra.SetoidGroup.Action
open import Substrate.Cocycle
open import Substrate.Algebra.Group.ToSetoid
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Cocycles.F2CubedPuncturing.F23GroupSetoid
open import Substrate.Cocycles.F2CubedPuncturing.WHTCore
open import Substrate.Cocycles.F2CubedPuncturing.Fiber
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingAction
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingFree
open import Substrate.Cocycles.F2CubedPuncturing.PuncturingTransitive



fiber-is-torsor : (i : WHTCore) → IsTorsor F₂³ _≡_ F₂³-Group-Setoid (Fiber i)
fiber-is-torsor wht-core = record
  { action     = puncturing-action
  ; free       = puncturing-free
  ; transitive = puncturing-transitive
  }
