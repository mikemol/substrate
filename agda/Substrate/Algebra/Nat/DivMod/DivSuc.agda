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

module Substrate.Algebra.Nat.DivMod.DivSuc where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<?_)
open import Substrate.Foundation.Negation using (yes; no)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)

_div-suc_ : ℕ → ℕ → ℕ
zero   div-suc _ = zero
suc a  div-suc b with suc (a mod-suc b) <? suc b
... | yes _ = a div-suc b
... | no  _ = suc (a div-suc b)
