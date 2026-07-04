{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.DetValSign — ⟡S3-detval. Connects the ABSTRACT
-- chirality tracker det-sign : ℕ → F₂ (ChiralityBridge, ⟡S3) to the REAL
-- ℤ-valued det-after (Properties): the sign of the actual CF-determinant after
-- n steps IS det-sign n = parity n = the chirality ℤ/2.
--
-- ⟡H-overclaim CORRECTION: I flagged this "refl-ish". WRONG — det-sq's own
-- structure shows det-after is NOT a simple outer flip; the seed-parametric
-- lemma det-after n … ≡ (−1)ⁿ *ℤ det4 … is needed (det-flip at the step +
-- ℤ neg-mult lemmas). Filed as a mild overclaim; the real proof below.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.DetValSign where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙) renaming (_+_ to _+F_)
open import Substrate.Algebra.N-to-F2-Parity using (parity)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left)
open import Substrate.Algebra.Z.Properties.MulFull using (neg-*-right; *ℤ-identityˡ)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Properties using (det4; det-after; det-flip)

-- (−1)ⁿ as a ℤ tracker.
pow-neg : ℕ → ℤ
pow-neg zero    = 1ℤ
pow-neg (suc n) = -ℤ (pow-neg n)

------------------------------------------------------------------------
-- THE FOLD LEMMA (seed-parametric, NOT refl): det-after n of any state is
-- (−1)ⁿ times that state's det4. Proof: induction; the step uses det-flip
-- (the inner det4 flips) pulled out through the ℤ neg-mult lemmas.
------------------------------------------------------------------------
det-after-value :
  (n p₁ q₁ p₀ q₀ : ℕ) (r : RealTrace) →
  det-after n p₁ q₁ p₀ q₀ r ≡ (pow-neg n) *ℤ (det4 p₁ q₁ p₀ q₀)
det-after-value zero    p₁ q₁ p₀ q₀ r = sym (*ℤ-identityˡ (det4 p₁ q₁ p₀ q₀))
det-after-value (suc n) p₁ q₁ p₀ q₀ r =
  trans (det-after-value n (a * p₁ + p₀) (a * q₁ + q₀) p₁ q₁ (tail r))
        (trans (cong (pow-neg n *ℤ_) (det-flip a p₁ q₁ p₀ q₀))
               (trans (neg-*-right (pow-neg n) (det4 p₁ q₁ p₀ q₀))
                      (sym (neg-*-left (pow-neg n) (det4 p₁ q₁ p₀ q₀)))))
  where a = head r

-- at the seed (1,0,0,1), det4 = +1, so det-after n 1 0 0 1 r = (−1)ⁿ.
det-after-seed : (n : ℕ) (r : RealTrace)
               → det-after n 1 0 0 1 r ≡ pow-neg n
det-after-seed n r =
  trans (det-after-value n 1 0 0 1 r) (*ℤ-comm-1 (pow-neg n))
  where
    -- det4 1 0 0 1 = (1*1) ⊖ (0*0) = +1, so pow-neg n *ℤ (+1) = pow-neg n.
    open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-identityʳ)
    *ℤ-comm-1 : (x : ℤ) → x *ℤ (det4 1 0 0 1) ≡ x
    *ℤ-comm-1 x = *ℤ-identityʳ x

------------------------------------------------------------------------
-- sign : ℤ → F₂ (𝟘 = ≥0, 𝟙 = negative). On the units ±1 it is the ℤ/2 sign.
------------------------------------------------------------------------
sign : ℤ → F₂
sign (+ _)    = 𝟘
sign (-suc _) = 𝟙

-- det-sign, the abstract tracker (ChiralityBridge): seed 𝟘, flip per step.
det-sign : ℕ → F₂
det-sign zero    = 𝟘
det-sign (suc n) = 𝟙 +F det-sign n

-- sign of (−1)ⁿ IS det-sign n (= parity n). Induction: sign(-ℤ(pow-neg n))
-- flips. pow-neg n is ±1 (never 0), so the flip is exact.
sign-pow-neg : (n : ℕ) → sign (pow-neg n) ≡ det-sign n
sign-pow-neg zero    = refl
sign-pow-neg (suc n) = trans (sign-flip (pow-neg n) (pow-neg-unit n))
                             (cong (𝟙 +F_) (sign-pow-neg n))
  where
    -- pow-neg n is a unit: either +(suc _) or -suc _, never +0.
    data Unit : ℤ → Set where
      pos : (k : ℕ) → Unit (+ (suc k))
      neg : (k : ℕ) → Unit (-suc k)
    pow-neg-unit : (n : ℕ) → Unit (pow-neg n)
    pow-neg-unit zero    = pos zero
    pow-neg-unit (suc n) with pow-neg n | pow-neg-unit n
    ... | + (suc k)  | pos .k = neg k
    ... | -suc k     | neg .k = pos k
    sign-flip : (x : ℤ) → Unit x → sign (-ℤ x) ≡ 𝟙 +F sign x
    sign-flip (+ (suc k)) (pos .k) = refl
    sign-flip (-suc k)    (neg .k) = refl

------------------------------------------------------------------------
-- ⟡S3-detval: the sign of the REAL ℤ-valued det-after IS the chirality ℤ/2.
------------------------------------------------------------------------
det-after-sign-is-chirality :
  (n : ℕ) (r : RealTrace) → sign (det-after n 1 0 0 1 r) ≡ det-sign n
det-after-sign-is-chirality n r =
  trans (cong sign (det-after-seed n r)) (sign-pow-neg n)

-- and det-sign IS parity (ChiralityBridge's identity, reproved here for closure)
det-sign-is-parity : (n : ℕ) → det-sign n ≡ parity n
det-sign-is-parity zero    = refl
det-sign-is-parity (suc n) = cong (𝟙 +F_) (det-sign-is-parity n)
