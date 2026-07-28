------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.Faithful
--
-- KEYSTONE #2: for REDUCED p,q, equal shape key ⟹ equal magnitude AND
-- equal denominator (cf-injective, via subst-shape).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.Faithful where

open import Substrate.Foundation.Eq using (_≡_; sym; trans)
open import Substrate.Foundation.Product using (_×_)
open import Substrate.Algebra.Q using (ℚ; num; denominator)
open import Substrate.Algebra.Q.Reduction using (is-reduced; abs-ℤ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace; coprime-trace)
open import Substrate.Algebra.Nat.GCD.CFInjective using (cf-injective)
open import Substrate.Algebra.Q.Properties.Decidable.Key

opaque
  unfolding q-key

  key-faithful : (p q : ℚ) → is-reduced p → is-reduced q → q-key p ≡ q-key q →
                 (abs-ℤ (num p) ≡ abs-ℤ (num q)) × (denominator p ≡ denominator q)
  key-faithful p q rp rq key-eq =
    cf-injective (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
                 (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
                 (trans (subst-shape rp (gcd-trace (abs-ℤ (num p)) (denominator p)))
                 (trans key-eq
                        (sym (subst-shape rq (gcd-trace (abs-ℤ (num q)) (denominator q))))))
