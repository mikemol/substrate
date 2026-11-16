------------------------------------------------------------------------
-- One more than a doubled ℕ is odd.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.OddSucDouble where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Wedge.BinBridge.Odd
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

odd-suc-double : (v : ℕ) → odd (suc (v ℕ+ v)) ≡ true
odd-suc-double zero    = refl
odd-suc-double (suc v) = trans (cong odd (+ℕ-suc v v)) (odd-suc-double v)
