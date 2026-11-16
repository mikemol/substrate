------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.Power
--
-- Modular exponentiation ℕ+ the Euler–Fermat engine: exponential periodicity.
-- If aᵈ ≡ 1 (mod M) — i.e. the order of a divides d — then a^(n·d) ≡ 1
-- (mod M). This is the mechanism of Euler/Fermat: once a power returns to 1,
-- every multiple of that exponent does too. Euler's theorem is the case
-- d = φ(M) (needs ord a | φ, i.e. Lagrange); Fermat's is M prime, d = M−1.
-- Proven on the modular ring-homomorphism (mod-mult-hom).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.Power where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-mult-hom)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

------------------------------------------------------------------------
-- 1. ℕ exponentiation and the exponent-addition law.
------------------------------------------------------------------------

pow : ℕ → ℕ → ℕ
pow a zero    = 1
pow a (suc k) = a * pow a k

pow-add : (a j k : ℕ) → pow a (j ℕ+ k) ≡ pow a j * pow a k
pow-add a zero    k = sym (+ℕ-identityʳ (pow a k))
pow-add a (suc j) k =
  trans (cong (a *_) (pow-add a j k)) (sym (*-assoc a (pow a j) (pow a k)))

------------------------------------------------------------------------
-- 2. Exponential periodicity: aᵈ ≡ 1 ⟹ a^(n·d) ≡ 1 (mod M).
------------------------------------------------------------------------

euler-periodic :
  {m : ℕ} (a d : ℕ) → (pow a d) mod-suc m ≡ 1 mod-suc m →
  (n : ℕ) → (pow a (n * d)) mod-suc m ≡ 1 mod-suc m
euler-periodic a d hyp zero     = refl
euler-periodic {m} a d hyp (suc n) =
  trans (cong (_mod-suc m) (pow-add a d (n * d)))
  (trans (mod-mult-hom (pow a d) (pow a (n * d)) m)
  (trans (cong₂ (λ u v → (u * v) mod-suc m) hyp (euler-periodic a d hyp n))
         (sym (mod-mult-hom 1 1 m))))

------------------------------------------------------------------------
-- Oracle: 2² ≡ 1 (mod 3), so 2^(2n) ≡ 1 (mod 3) for all n.
------------------------------------------------------------------------

two-sq-mod-3 : (pow 2 2) mod-suc 2 ≡ 1 mod-suc 2
two-sq-mod-3 = refl

two-even-pow-mod-3 : (n : ℕ) → (pow 2 (n * 2)) mod-suc 2 ≡ 1 mod-suc 2
two-even-pow-mod-3 = euler-periodic 2 2 two-sq-mod-3
