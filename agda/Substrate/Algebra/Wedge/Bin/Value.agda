------------------------------------------------------------------------
-- The numeral's value: Σ bitᵢ·2ⁱ. Cited, not built — this is `morton`.
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.Value where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.CayleyDickson.Curve.Morton
open import Substrate.Algebra.Wedge.Bin.Carrier

value : {n : ℕ} → Bin n → ℕ
value = morton
