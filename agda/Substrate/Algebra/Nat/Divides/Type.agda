------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Type
--
-- The substrate-native divisibility predicate:
--   m ∣ n  iff  ∃ q. n ≡ q * m
-- Single constructor `divides q n≡q*m` packages the witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Type where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Eq using (_≡_)

infix 4 _∣_

data _∣_ (m n : ℕ) : Set where
  divides : (q : ℕ) → n ≡ q * m → m ∣ n
