------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdPos
--
-- gcd with a positive second argument is positive:
--   gcd-pos : (n d) → Σ g′ → gcd-ℕ n (suc d) ≡ suc g′
--
-- (Returned in `suc` form so callers can cancel the gcd as a positive ℤ
-- factor via *ℤ-cancelʳ-pos.) gcd-ℕ n (suc d) divides suc d; were it 0 it
-- would force suc d ≡ 0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdPos where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; s≤s; z≤n)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; subst)
open import Substrate.Foundation.Product using (Σ; _,_; proj₂)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Nat.Properties.Mul using (*-zeroʳ)
open import Substrate.Algebra.Nat.Divides using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)

private
  zero∤suc : {m : ℕ} → zero ∣ suc m → ⊥
  zero∤suc (divides q eq) with trans eq (*-zeroʳ q)
  ... | ()

gcd-pos : (n d : ℕ) → Σ ℕ (λ g′ → gcd-ℕ n (suc d) ≡ suc g′)
gcd-pos n d with gcd-ℕ n (suc d) | gcd-divides-right n (suc d)
... | zero  | z∣sd = ⊥-elim (zero∤suc z∣sd)
... | suc g | _    = g , refl

-- The order form (positivity), for callers that want `0 < gcd` directly.
gcd-suc-pos : (n d : ℕ) → 0 < gcd-ℕ n (suc d)
gcd-suc-pos n d = subst (0 <_) (sym (proj₂ (gcd-pos n d))) (s≤s z≤n)
