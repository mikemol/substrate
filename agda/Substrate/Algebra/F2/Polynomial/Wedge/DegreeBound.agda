------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound  (AI-17 B-DIVc)
--
-- The canonicality bound for division remainders: a `Polynomial n` has degree
-- `< n` (it has only n coefficient slots). So a division remainder `r-div a :
-- Polynomial (suc d)` (from `Graded.Div`, by a divisor of degree suc d) has
-- `degree (r-div a) < suc d = deg b` — strictly smaller than the divisor, the
-- refinement that makes the Euclidean algorithm (B-EEA) terminate.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _≤_; _<_; z≤n; s≤s)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong; subst)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Polynomial using (Polynomial)
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
  using (leading-position; leading-position-acc)
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeLt using (degree-lt)

private
  +-suc : (m n : ℕ) → m + suc n ≡ suc (m + n)
  +-suc zero    n = refl
  +-suc (suc m) n = cong suc (+-suc m n)
  ≤-refl : (n : ℕ) → n ≤ n
  ≤-refl zero    = z≤n
  ≤-refl (suc n) = s≤s (≤-refl n)
  ≤-trans : {a b c : ℕ} → a ≤ b → b ≤ c → a ≤ c
  ≤-trans z≤n     _       = z≤n
  ≤-trans (s≤s p) (s≤s q) = s≤s (≤-trans p q)
  m≤m+n : (m n : ℕ) → m ≤ m + n
  m≤m+n zero    n = z≤n
  m≤m+n (suc m) n = s≤s (m≤m+n m n)
  -- leading-position-acc [] reduces to best (forced here, where refl typechecks).
  lp-empty : (pos : ℕ) (best : Maybe ℕ) → leading-position-acc {0} [] pos best ≡ best
  lp-empty pos best = refl

-- the leading position counted from `pos` over a length-n tail is < pos+n ≤ N.
lp-acc-bound : ∀ {n} (v : Polynomial n) (pos : ℕ) (best : Maybe ℕ) (N : ℕ)
             → pos + n ≤ N → degree-lt best (just N)
             → degree-lt (leading-position-acc v pos best) (just N)
lp-acc-bound {zero}  [] pos best N h1 h2 =
  subst (λ z → degree-lt z (just N)) (sym (lp-empty pos best)) h2
lp-acc-bound (𝟘 ∷ p) pos best N h1 h2 =
  lp-acc-bound p (suc pos) best N (subst (_≤ N) (+-suc pos _) h1) h2
lp-acc-bound (𝟙 ∷ p) pos best N h1 h2 =
  lp-acc-bound p (suc pos) (just pos) N (subst (_≤ N) (+-suc pos _) h1)
               (≤-trans (s≤s (m≤m+n pos _)) (subst (_≤ N) (+-suc pos _) h1))

-- a Polynomial n has degree < n — the canonicality bound (applied to r-div a : Poly (suc d)).
lp-bound : ∀ {n} (v : Polynomial n) → degree-lt (leading-position v) (just n)
lp-bound {n} v = lp-acc-bound v 0 nothing n (≤-refl n) tt
