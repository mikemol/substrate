------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod.DivSuc
--
-- Structurally-recursive division by (suc b):
--   _div-suc_ : ℕ → ℕ → ℕ
--   a div-suc b = ⌊ a / (suc b) ⌋
-- Mirrors Substrate.Algebra.Nat.Mod._mod-suc_ structurally: recursion
-- is on `a` alone, with the same with-clause dispatch.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Nat.DivSuc where

open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf

_div-suc_ : ℕ → ℕ → ℕ
zero   div-suc _ = zero
suc a  div-suc b with suc (a mod-suc b) <? suc b
... | yes _ = a div-suc b
... | no  _ = suc (a div-suc b)
