------------------------------------------------------------------------
-- Halving discards the odd unit.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.HalfSucDouble where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Wedge.BinBridge.Half
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

half-suc-double : (v : ℕ) → half (suc (v ℕ+ v)) ≡ v
half-suc-double zero    = refl
half-suc-double (suc v) =
  trans (cong (λ z → suc (half z)) (+ℕ-suc v v)) (cong suc (half-suc-double v))
