------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent.Xpow
--
-- Defines: xpow
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Idempotent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent.Xpow where

open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.GF256.Xtime



xpow : ℕ → Vector 8 → Vector 8
xpow zero    r = r
xpow (suc k) r = xpow k (xtime r)
