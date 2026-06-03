------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Units
--
-- The units mod (suc m) — "the survivors": elements that carry a modular
-- inverse. The inverse IS the witness (the oriented bridge to invertibility),
-- and it is exactly the coprimes — produced by the EEA fold
-- (unit-from-coprime via inverse-from-trace). The units form a monoid
-- (one-is-unit, unit-mult closure), hence the group (ℤ/(suc m))* on which
-- Euler's theorem (a^φ ≡ 1) stands. This slice builds that group's carrier +
-- closure + the coprime↔unit bridge; Euler's theorem itself (Lagrange /
-- product-of-units) is the larger follow-on.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Units where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc; *-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-mult-hom)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (inverse-from-trace)

------------------------------------------------------------------------
-- 1. A unit mod (suc m): an element carrying a right inverse.
------------------------------------------------------------------------

IsUnit : (m a : ℕ) → Set
IsUnit m a = Σ ℕ (λ b → (a * b) mod-suc m ≡ 1 mod-suc m)

-- 1 is a unit (its own inverse).
one-is-unit : (m : ℕ) → IsUnit m 1
one-is-unit m = 1 , refl

------------------------------------------------------------------------
-- 2. Units are closed under multiplication (the inverse of a·b is b⁻¹·a⁻¹).
------------------------------------------------------------------------

unit-mult : (m a b : ℕ) → IsUnit m a → IsUnit m b → IsUnit m (a * b)
unit-mult m a b (ia , ea) (ib , eb) = (ia * ib) , proof
  where
    rearr : (a * b) * (ia * ib) ≡ (a * ia) * (b * ib)
    rearr =
      trans (*-assoc a b (ia * ib))
      (trans (cong (a *_) (sym (*-assoc b ia ib)))
      (trans (cong (λ z → a * (z * ib)) (*-comm b ia))
      (trans (cong (a *_) (*-assoc ia b ib))
             (sym (*-assoc a ia (b * ib))))))
    proof : ((a * b) * (ia * ib)) mod-suc m ≡ 1 mod-suc m
    proof =
      trans (cong (_mod-suc m) rearr)
      (trans (mod-mult-hom (a * ia) (b * ib) m)
      (trans (cong₂ (λ u v → (u * v) mod-suc m) ea eb)
             (sym (mod-mult-hom 1 1 m))))

------------------------------------------------------------------------
-- 3. The units ARE the coprimes: a coprimality trace yields a unit, with
--    the EEA-computed inverse as the witness.
------------------------------------------------------------------------

unit-from-coprime : {m n : ℕ} → EEATrace (suc m) (suc n) 1 → IsUnit m (suc n)
unit-from-coprime = inverse-from-trace

------------------------------------------------------------------------
-- Oracles.
------------------------------------------------------------------------

-- 2 is a unit mod 3 (2·2 = 4 ≡ 1).
ex-2-unit : IsUnit 2 2
ex-2-unit = 2 , refl

-- closure: 4 = 2·2 is a unit mod 3 (inverse 2·2 = 4 ≡ 1).
ex-4-unit : IsUnit 2 (2 * 2)
ex-4-unit = unit-mult 2 2 2 ex-2-unit ex-2-unit
