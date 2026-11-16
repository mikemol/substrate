------------------------------------------------------------------------
-- Substrate.Algebra.Z.Coprime.Bezout1Tocoprime
--
-- Defines: bezout-1→coprime
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Coprime; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Coprime.Bezout1Tocoprime where
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Mul

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Arithmetic
open import Substrate.Algebra.Z.Properties.MulFull
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.Divides.One
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Algebra.Z.Coprime.UnitZ



-- Bézout-1 ⟹ coprime: a combination equal to 1 forces gcd 1.
bezout-1→coprime : (s t : ℤ) (a b : ℕ) →
  (s *ℤ (+ a)) +ℤ (t *ℤ (+ b)) ≡ + 1 → gcd-ℕ a b ≡ 1
bezout-1→coprime s t a b bz with gcd-divides-left a b | gcd-divides-right a b
... | divides qa a≡ | divides qb b≡ = ∣-one (unit-z z (gcd-ℕ a b) zg≡1)
  where
    z = (s *ℤ (+ qa)) +ℤ (t *ℤ (+ qb))
    zg≡1 : z *ℤ (+ gcd-ℕ a b) ≡ + 1
    zg≡1 = trans (*ℤ-distribʳ-+ (s *ℤ (+ qa)) (t *ℤ (+ qb)) (+ gcd-ℕ a b))
           (trans (cong₂ _+ℤ_
                     (trans (*ℤ-assoc s (+ qa) (+ gcd-ℕ a b)) (cong (λ x → s *ℤ (+ x)) (sym a≡)))
                     (trans (*ℤ-assoc t (+ qb) (+ gcd-ℕ a b)) (cong (λ x → t *ℤ (+ x)) (sym b≡))))
                  bz)
