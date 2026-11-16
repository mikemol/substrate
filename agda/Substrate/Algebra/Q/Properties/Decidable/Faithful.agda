------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.Faithful
--
-- KEYSTONE #2: for REDUCED p,q, equal shape key ⟹ equal magnitude AND
-- equal denominator (cf-injective, via subst-shape).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.Faithful where

open import Substrate.Foundation.Product using (_×_)
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.IsReduced
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace; coprime-trace)
open import Substrate.Algebra.Nat.GCD.CFInjective.CfInjective
open import Substrate.Algebra.Q.Properties.Decidable.Key
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans

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
