------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides
--
-- Substrate-native divisibility on ℕ. Replaces stdlib's
-- `Data.Nat.Divisibility`. File-per-lemma:
--
--   Divides.Type   — the _∣_ predicate
--   Divides.Refl   — ∣-refl : m ∣ m
--   Divides.Trans  — ∣-trans : a ∣ b → b ∣ c → a ∣ c
--   Divides.Mul    — m∣m*n, n∣m*n
--   Divides.Sum    — ∣m∣n⇒∣m+n : c ∣ m → c ∣ n → c ∣ (m + n)
--   Divides.Zero   — ∣-zero : m ∣ 0
--   Divides.One    — ∣-one : m ∣ 1 → m ≡ 1
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides where

open import Substrate.Algebra.Nat.Divides.Type  public
open import Substrate.Algebra.Nat.Divides.Refl  public
open import Substrate.Algebra.Nat.Divides.Trans public
open import Substrate.Algebra.Nat.Divides.Mul   public
open import Substrate.Algebra.Nat.Divides.Sum   public
open import Substrate.Algebra.Nat.Divides.Zero  public
open import Substrate.Algebra.Nat.Divides.One   public
