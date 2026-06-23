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

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm; *-zeroʳ)

-- zero ∸ n ≡ zero (∸ cannot peel a neutral subtrahend, so this is not refl).
0∸n : (n : ℕ) → zero ∸ n ≡ zero
0∸n zero    = refl
0∸n (suc n) = refl

-- A common left addend cancels through monus:  (a + u) ∸ (a + v) ≡ u ∸ v.
+-∸-cancelˡ : (a u v : ℕ) → (a + u) ∸ (a + v) ≡ u ∸ v
+-∸-cancelˡ zero    u v = refl
+-∸-cancelˡ (suc a) u v = +-∸-cancelˡ a u v

-- a * suc b ≡ a + a * b  (the right-successor law, via *-comm — no *-distribʳ-+).
*-sucʳ : (a b : ℕ) → a * suc b ≡ a + a * b
*-sucʳ a b = trans (*-comm a (suc b)) (cong (a +_) (*-comm b a))

-- Multiplication distributes (on the left) over truncated subtraction.
*-distribˡ-∸ : (a b c : ℕ) → a * (b ∸ c) ≡ a * b ∸ a * c
*-distribˡ-∸ a b       zero    = sym (cong (λ z → a * b ∸ z) (*-zeroʳ a))
*-distribˡ-∸ a zero    (suc c) =
  trans (*-zeroʳ a) (sym (trans (cong (_∸ a * suc c) (*-zeroʳ a)) (0∸n (a * suc c))))
*-distribˡ-∸ a (suc b) (suc c) =
  trans (*-distribˡ-∸ a b c)
        (sym (trans (cong₂ _∸_ (*-sucʳ a b) (*-sucʳ a c))
                    (+-∸-cancelˡ a (a * b) (a * c))))
