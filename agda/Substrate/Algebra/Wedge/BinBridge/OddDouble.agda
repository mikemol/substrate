------------------------------------------------------------------------
-- A doubled ℕ is even. The `+-suc` transport re-exposes the
-- two-at-a-time pattern `odd` recurses on.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.OddDouble where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Wedge.BinBridge.Odd
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

odd-double : (v : ℕ) → odd (v ℕ+ v) ≡ false
odd-double zero    = refl
odd-double (suc v) = trans (cong odd (cong suc (+ℕ-suc v v))) (odd-double v)
