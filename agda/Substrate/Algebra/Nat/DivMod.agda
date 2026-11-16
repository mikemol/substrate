------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod
--
-- Substrate-native truncated division by `suc b` and the
-- reconstruction equation. Replaces stdlib's `Data.Nat.DivMod`.
-- File-per-lemma:
--
--   DivMod.DivSuc          — _div-suc_ structural recursion on a
--   DivMod.Reconstruction  — div-mod-eq : a ≡ (a mod-suc b) + (a div-suc b) * (suc b)
--
-- Bounds (m%n<n analog) live in Substrate.Algebra.Nat.Mod's
-- `mod-suc-bound`; this shim re-exports both for parity with stdlib's
-- DivMod surface.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.DivMod where

open import Substrate.Foundation.Nat.Nat.DivSuc
open import Substrate.Algebra.Nat.DivMod.Reconstruction
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
