------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.PrimeDividesProduct
--
-- Defines: prime-divides-product
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.PrimeDividesProduct where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.GCD.GcdPos.GcdPos
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Algebra.Z.Euclid
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 7. UNIQUENESS kernel (Ⓝ.u): Euclid's lemma for PRIMES. The coprime-form
--    `euclid` rides on `bezout-ℤ` (the EEA trace's residue, never-discarded);
--    a prime is coprime to anything it does not divide (its only divisors are 1
--    and itself), so it LIFTS to: p ∣ a·b ⟹ p∣a or p∣b — the heart of FTA
--    uniqueness (the multiset of primes is forced).
------------------------------------------------------------------------

prime-divides-product : ∀ {p} → IsPrime p → (a b : ℕ) → p ∣ (a * b) → (p ∣ a) ⊎ (p ∣ b)
prime-divides-product {zero}    pp _ _ _    with proj₁ pp
... | ()
prime-divides-product {suc zero} pp _ _ _   with proj₁ pp
... | (s≤s ())
prime-divides-product {suc (suc m'')} pp a b p∣ab with gcd-pos a (suc m'')
... | (zero    , gcd≡1) = inj₂ (euclid a (suc m'') b gcd≡1 p∣ab)
... | (suc g'' , gcd≡g) = inj₁ (subst (λ x → x ∣ a) g≡p g∣a)
  where
    g∣a : suc (suc g'') ∣ a
    g∣a = subst (λ x → x ∣ a) gcd≡g (gcd-divides-left a (suc (suc m'')))
    g∣p : suc (suc g'') ∣ suc (suc m'')
    g∣p = subst (λ x → x ∣ suc (suc m'')) gcd≡g (gcd-divides-right a (suc (suc m'')))
    g≡p : suc (suc g'') ≡ suc (suc m'')
    g≡p = proj₂ pp (suc (suc g'')) g∣p (s≤s (s≤s z≤n))
