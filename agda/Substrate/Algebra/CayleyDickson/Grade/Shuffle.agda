------------------------------------------------------------------------
-- A 4-term commutative-monoid shuffle: (a+b)ℕ+(c+d) = (a+c)ℕ+(b+d).
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.Shuffle where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
shuffle a b c d =
  trans (+ℕ-assoc a b (c ℕ+ d))
  (trans (cong (a ℕ+_) (sym (+ℕ-assoc b c d)))
  (trans (cong (λ z → a ℕ+ (z ℕ+ d)) (+ℕ-comm b c))
  (trans (cong (a ℕ+_) (+ℕ-assoc c b d))
         (sym (+ℕ-assoc a c (b ℕ+ d))))))
