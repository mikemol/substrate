------------------------------------------------------------------------
-- At a fixed width, the value determines the bits — `value` is faithful
-- and the carrier holds no redundant representations. A corollary of the
-- retraction, in two lines.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.ValueInjective where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinBridge.ToBin
open import Substrate.Algebra.Wedge.BinBridge.ToBinSection
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans

value-injective : {w : ℕ} (b c : Bin w) → value b ≡ value c → b ≡ c
value-injective b c eq =
  trans (sym (toBin-section b))
        (trans (cong (toBin _) eq) (toBin-section c))
