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

open import Substrate.Algebra.Nat.DivMod.DivSuc         public
open import Substrate.Algebra.Nat.DivMod.Reconstruction public
open import Substrate.Algebra.Nat.Mod                   public
  using (_mod-suc_; mod-suc-bound)
