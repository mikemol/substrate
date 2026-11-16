------------------------------------------------------------------------
-- Halving undoes doubling.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.HalfDouble where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Wedge.BinBridge.Half
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

half-double : (v : ℕ) → half (v ℕ+ v) ≡ v
half-double zero    = refl
half-double (suc v) =
  trans (cong half (cong suc (+ℕ-suc v v))) (cong suc (half-double v))
