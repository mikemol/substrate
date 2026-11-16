------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosZero
--
-- Defines: toℕ-inv-pos-zero
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosZero (n : ℕ) where

-- ⚑ `Cyclic.Inverse` DISSOLVED; `…InvInv.Private` provides ZERO names (Ⓐ¹²′).
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPos n


toℕ-inv-pos-zero : toℕ (inv-pos (zero {n})) ≡ 0
toℕ-inv-pos-zero =
  trans (toℕ-inv-pos zero) (suc-mod-suc-self n)
