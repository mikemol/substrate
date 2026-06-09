------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.One
--
-- Divisors of 1 are 1: the only ℕ dividing the unit is the unit itself.
--   ∣-one : m ∣ 1 → m ≡ 1
--
-- Used to collapse Bézout/coprimality witnesses (a common divisor of two
-- coprime numbers divides 1, hence is 1).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.One where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Cancel using (suc-injective)
open import Substrate.Foundation.Nat.Properties.Mul using (*-zeroʳ; *-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)

-- `m ∣ 1` gives `q` with `1 ≡ q * m`. Pin `m`:
--   m = 0       → 1 ≡ q*0 ≡ 0, contradiction supplies the (vacuous) goal.
--   m = 1       → refl.
--   m = 2+      → q*m has a factor ≥ 2, so 1 ≡ q*m forces 0 ≡ suc _, absurd.
∣-one : {m : ℕ} → m ∣ 1 → m ≡ 1
∣-one {zero}        (divides q eq)       = sym (trans eq (*-zeroʳ q))
∣-one {suc zero}    _                    = refl
∣-one {suc (suc m)} (divides zero ())
∣-one {suc (suc m)} (divides (suc q) eq) with suc-injective eq
... | ()

-- A product equal to 1 forces each factor to 1 (both handednesses, via ∣-one).
*≡1ˡ : (m n : ℕ) → m * n ≡ 1 → m ≡ 1
*≡1ˡ m n eq = ∣-one (divides n (trans (sym eq) (*-comm m n)))

*≡1ʳ : (m n : ℕ) → m * n ≡ 1 → n ≡ 1
*≡1ʳ m n eq = *≡1ˡ n m (trans (*-comm n m) eq)
