------------------------------------------------------------------------
-- THE WEDGE ON ℕ: a = 2·q ℕ+ r, the ℕ-side twin of Bin.BinDivmod2Value.
-- That one is `refl` — dividing by the radix on the bit carrier is a
-- pattern match. This one costs a three-case induction and four `+-suc`
-- transports. The asymmetry is the migration's whole thesis.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.Divmod2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Algebra.Wedge.BinBridge.Odd
open import Substrate.Algebra.Wedge.BinBridge.Half
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

divmod2 : (n : ℕ) → boolToℕ (odd n) ℕ+ (half n ℕ+ half n) ≡ n
divmod2 zero       = refl
divmod2 (suc zero) = refl
divmod2 (suc (suc n)) =
  trans (+ℕ-suc (boolToℕ (odd n)) (half n ℕ+ suc (half n)))
  (trans (cong (λ z → suc (boolToℕ (odd n) ℕ+ z)) (+ℕ-suc (half n) (half n)))
  (trans (cong suc (+ℕ-suc (boolToℕ (odd n)) (half n ℕ+ half n)))
         (cong (λ z → suc (suc z)) (divmod2 n))))
