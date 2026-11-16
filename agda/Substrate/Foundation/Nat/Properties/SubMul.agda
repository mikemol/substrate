------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.SubMul
--
-- The monus×multiplication interaction lemmas (the gap surfaced by Ⓕ.mult):
-- multiplication distributes (left) over truncated subtraction, and an addend
-- cancels through monus. Standard ℕ facts, absent from Add/Mul/Sub; proven here
-- WITHOUT *-distribʳ-+ (also absent) by routing through *-comm (`*-sucʳ`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.SubMul where

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm; *-zeroʳ)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym

-- zero ∸ n ≡ zero (∸ cannot peel a neutral subtrahend, so this is not refl).
0∸n : (n : ℕ) → zero ∸ n ≡ zero
0∸n zero    = refl
0∸n (suc n) = refl

-- A common left addend cancels through monus:  (a ℕ+ u) ∸ (a ℕ+ v) ≡ u ∸ v.
+-∸-cancelˡ : (a u v : ℕ) → (a ℕ+ u) ∸ (a ℕ+ v) ≡ u ∸ v
+-∸-cancelˡ zero    u v = refl
+-∸-cancelˡ (suc a) u v = +-∸-cancelˡ a u v

-- a * suc b ≡ a ℕ+ a * b  (the right-successor law, via *-comm — no *-distribʳ-+).
*-sucʳ : (a b : ℕ) → a * suc b ≡ a ℕ+ a * b
*-sucʳ a b = trans (*-comm a (suc b)) (cong (a ℕ+_) (*-comm b a))

-- Multiplication distributes (on the left) over truncated subtraction.
*-distribˡ-∸ : (a b c : ℕ) → a * (b ∸ c) ≡ a * b ∸ a * c
*-distribˡ-∸ a b       zero    = sym (cong (λ z → a * b ∸ z) (*-zeroʳ a))
*-distribˡ-∸ a zero    (suc c) =
  trans (*-zeroʳ a) (sym (trans (cong (_∸ a * suc c) (*-zeroʳ a)) (0∸n (a * suc c))))
*-distribˡ-∸ a (suc b) (suc c) =
  trans (*-distribˡ-∸ a b c)
        (sym (trans (cong₂ _∸_ (*-sucʳ a b) (*-sucʳ a c))
                    (+-∸-cancelˡ a (a * b) (a * c))))
