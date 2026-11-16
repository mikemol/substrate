------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ConstructWedge
--
-- construct-wedge : (a b : ℕ) → Wedge-GCD a (suc b).
-- Bridges substrate-native DivMod (`_div-suc_` ℕ+ `_mod-suc_` ℕ+
-- `div-mod-eq`) to the Wedge-GCD structural decomposition record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.ConstructWedge where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Nat.DivSuc
open import Substrate.Algebra.Nat.DivMod.Reconstruction using (div-mod-eq)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.GCD.Wedge using () renaming (Wedge-GCD to Wedge-GCD)
open import Substrate.Foundation.Eq.Trans
open import Substrate.Algebra.Nat.GCD.Wedge
construct-wedge : (a b : ℕ) → Wedge-GCD a (suc b)
construct-wedge a b = record
  { quotient  = a div-suc b
  ; remainder = a mod-suc b
  ; wedge-eq  =
      trans (div-mod-eq a b)
            (+ℕ-comm (a mod-suc b) ((a div-suc b) * suc b))
  ; r<b       = mod-suc-bound a b
  }
