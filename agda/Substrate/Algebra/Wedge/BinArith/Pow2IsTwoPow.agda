------------------------------------------------------------------------
-- The tie to the ambient power, so `pow2` is not a private reinvention.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.Pow2IsTwoPow where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Algebra.Wedge.BinArith.Pow2
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans

pow2-is-two^ : (n : ℕ) → pow2 n ≡ 2 ^ n
pow2-is-two^ zero    = refl
pow2-is-two^ (suc n) =
  trans (cong₂ _ℕ+_ (pow2-is-two^ n) (pow2-is-two^ n))
        (cong ((2 ^ n) ℕ+_) (sym (+ℕ-identityʳ (2 ^ n))))
