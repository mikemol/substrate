------------------------------------------------------------------------
-- The other direction, and its bound: `toBin` TRUNCATES, so reading the
-- value back recovers n exactly when n fits the predicted width. This is
-- the encoder-side statement of predicted ≥ actual. With ToBinSection it
-- gives Bin w ≅ { n : ℕ ∣ n < 2ʷ }.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.ToBinValue where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.SLesInjective
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinArith.Pow2
open import Substrate.Algebra.Wedge.BinBridge.Odd
open import Substrate.Algebra.Wedge.BinBridge.Half
open import Substrate.Algebra.Wedge.BinBridge.ToBin
open import Substrate.Algebra.Wedge.BinBridge.Divmod2
open import Substrate.Algebra.Wedge.BinBridge.HalfLt
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

toBin-value : (w n : ℕ) → n < pow2 w → value (toBin w n) ≡ n
toBin-value zero    zero    _  = refl
toBin-value zero    (suc _) (s≤s ())
toBin-value (suc w) n       lt =
  trans (cong (λ z → boolToℕ (odd n) ℕ+ (z ℕ+ z))
              (toBin-value w (half n) (half-lt n (pow2 w) lt)))
        (divmod2 n)
