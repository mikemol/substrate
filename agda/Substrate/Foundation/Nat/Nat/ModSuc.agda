------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.ModSuc
--
-- Defines: _mod-suc_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Nat.ModSuc where

open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble



------------------------------------------------------------------------
-- 1. Modular reduction.
--
-- `a mod-suc b` returns the canonical-form representative of `a`
-- modulo `suc b`. The divisor is stored as `suc b` rather than as
-- an arbitrary positive ℕ so non-zero-ness is structural.
------------------------------------------------------------------------

_mod-suc_ : ℕ → ℕ → ℕ
zero   mod-suc _ = zero
suc a  mod-suc b with suc (a mod-suc b) <? suc b
... | yes _ = suc (a mod-suc b)
... | no  _ = zero
