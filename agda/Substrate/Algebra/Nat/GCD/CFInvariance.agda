------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInvariance
--
-- KEYSTONE #1 of the ℚ-Canonical shape route: the continued-fraction shape
-- of a Euclidean trace depends only on the VALUE of the fraction.
--
--   shape-value-invariance :
--     (t₁ : EEATrace a b g₁)(t₂ : EEATrace c d g₂) →
--     0 < g₁ → 0 < g₂ → a * d ≡ c * b → ℕ-shape t₁ ≡ ℕ-shape t₂
--
-- Proven by structural induction on BOTH traces (no contact with the Acc
-- recursion). The 0 < g hypotheses exclude the degenerate `base 0`
-- (= the value 0/0), the one place shape-equality would otherwise fail;
-- g is the gcd index, which the `step` constructor preserves, so positivity
-- threads unchanged into the recursion. At the ℚ top level g = gcd(|num|, den)
-- with den > 0, so g > 0 always.
--
-- The head step (`divmod-cross`) multiplies the two reconstruction equations
-- into a single division-by-(suc b' · suc d') and applies divmod-unique:
-- same value ⟹ same leading quotient AND a cross-equation for the tails.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInvariance where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _<_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-comm; *-zeroʳ; *-distribʳ-+)
open import Substrate.Foundation.Nat.Properties.Order
  using (<-irrefl; ≤-<-trans; n≤m+n; *-monoˡ-≤)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.List using (_∷_)
open import Substrate.Algebra.Nat.GCD.Wedge using (quotient; remainder; wedge-eq; r<b)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Algebra.Nat.DivMod.Unique using (divmod-unique)
open import Substrate.Algebra.Wedge.Shape using (ℕ-shape)

private
  -- A positive times a positive is positive (the value 0/0 detector).
  pos-*-pos : (m n : ℕ) → 0 < m → 0 < m * suc n
  pos-*-pos zero    n ()
  pos-*-pos (suc m) n _ = s≤s z≤n

  -- Multiplying a strict bound by a positive preserves it.
  mul-mono-strict : (r b n : ℕ) → r < suc b → r * suc n < suc b * suc n
  mul-mono-strict r b n (s≤s r≤b) =
    ≤-<-trans (*-monoˡ-≤ (suc n) r≤b) (s≤s (n≤m+n n (b * suc n)))

------------------------------------------------------------------------
-- L3: the head step. Same value ⟹ same leading quotient + tail cross-eq.
------------------------------------------------------------------------

divmod-cross :
  (q₁ q₂ r₁ r₂ b' d' : ℕ) →
  r₁ < suc b' → r₂ < suc d' →
  (q₁ * suc b' + r₁) * suc d' ≡ (q₂ * suc d' + r₂) * suc b' →
  (q₁ ≡ q₂) × (r₁ * suc d' ≡ r₂ * suc b')
divmod-cross q₁ q₂ r₁ r₂ b' d' lt₁ lt₂ eq =
  divmod-unique q₁ q₂ (r₁ * suc d') (r₂ * suc b') (d' + b' * suc d')
    (mul-mono-strict r₁ b' d' lt₁)
    (subst (r₂ * suc b' <_) (*-comm (suc d') (suc b')) (mul-mono-strict r₂ d' b' lt₂))
    eq'
  where
    lhs : (q₁ * suc b' + r₁) * suc d' ≡ q₁ * (suc b' * suc d') + r₁ * suc d'
    lhs = trans (*-distribʳ-+ (suc d') (q₁ * suc b') r₁)
                (cong (_+ r₁ * suc d') (*-assoc q₁ (suc b') (suc d')))
    rhs : (q₂ * suc d' + r₂) * suc b' ≡ q₂ * (suc b' * suc d') + r₂ * suc b'
    rhs = trans (*-distribʳ-+ (suc b') (q₂ * suc d') r₂)
                (cong (_+ r₂ * suc b')
                      (trans (*-assoc q₂ (suc d') (suc b'))
                             (cong (q₂ *_) (*-comm (suc d') (suc b')))))
    eq' : q₁ * (suc b' * suc d') + r₁ * suc d' ≡ q₂ * (suc b' * suc d') + r₂ * suc b'
    eq' = trans (sym lhs) (trans eq rhs)

------------------------------------------------------------------------
-- L4: continued-fraction value-invariance (KEYSTONE #1).
------------------------------------------------------------------------

shape-value-invariance :
  {a b c d g₁ g₂ : ℕ} (t₁ : EEATrace a b g₁) (t₂ : EEATrace c d g₂) →
  0 < g₁ → 0 < g₂ → a * d ≡ c * b → ℕ-shape t₁ ≡ ℕ-shape t₂
shape-value-invariance (base a)          (base c)          _    _    _   = refl
shape-value-invariance {c = c} (base a)  (step d' w₂ sub₂) pos₁ _    hyp =
  ⊥-elim (<-irrefl 0 (subst (0 <_) (trans hyp (*-zeroʳ c)) (pos-*-pos a d' pos₁)))
shape-value-invariance {a = a} (step b' w₁ sub₁) (base c)  _    pos₂ hyp =
  ⊥-elim (<-irrefl 0 (subst (0 <_) (trans (sym hyp) (*-zeroʳ a)) (pos-*-pos c b' pos₂)))
shape-value-invariance (step b' w₁ sub₁) (step d' w₂ sub₂) pos₁ pos₂ hyp =
  cong₂ _∷_ (proj₁ cross)
            (shape-value-invariance sub₁ sub₂ pos₁ pos₂ rec-hyp)
  where
    cross : (quotient w₁ ≡ quotient w₂)
          × (remainder w₁ * suc d' ≡ remainder w₂ * suc b')
    cross = divmod-cross (quotient w₁) (quotient w₂) (remainder w₁) (remainder w₂)
              b' d' (r<b w₁) (r<b w₂)
              (trans (cong (_* suc d') (sym (wedge-eq w₁)))
                     (trans hyp (cong (_* suc b') (wedge-eq w₂))))
    rec-hyp : suc b' * remainder w₂ ≡ suc d' * remainder w₁
    rec-hyp = trans (*-comm (suc b') (remainder w₂))
                    (trans (sym (proj₂ cross)) (*-comm (remainder w₁) (suc d')))
