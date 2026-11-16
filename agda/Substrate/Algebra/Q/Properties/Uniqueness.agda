------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Uniqueness
--
-- The SHARED scaffolding of ℚ reduced-form uniqueness, factored so the two
-- routes (CF-shape injectivity; Bézout/Euclid) converge on one assembly and
-- differ ONLY in how they derive the (magnitude, denominator) components.
--
--   mag-cross-of-≈   : p ≈ℚ q ⟹ |num p|·den q ≡ |num q|·den p  (sign-stripped)
--   uniq-from-mag-den: equal magnitude + equal denominator + p ≈ℚ q ⟹ p ≡ q
--                      (sign agreement from ℤ-sign-mag; denominators by suc-inj)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Uniqueness where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Cancel using (suc-injective)
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Properties.Abs using (abs-*ℤ-pos; ℤ-sign-mag)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.Q.JacobianEvalCD
open import Substrate.Foundation.Nat.SucInjective

mag-cross-of-≈ : (p q : ℚ) → p ≈ℚ q →
                 abs-ℤ (num p) * denominator q ≡ abs-ℤ (num q) * denominator p
mag-cross-of-≈ p q pq = trans (sym (abs-*ℤ-pos (num p) (den-1 q)))
                        (trans (cong abs-ℤ pq) (abs-*ℤ-pos (num q) (den-1 p)))

uniq-from-mag-den : (p q : ℚ) →
                    abs-ℤ (num p) ≡ abs-ℤ (num q) → denominator p ≡ denominator q →
                    p ≈ℚ q → p ≡ q
uniq-from-mag-den p q mag-eq den-eq pq =
  cong₂ mkℚ (ℤ-sign-mag (num p) (num q) (den-1 q) (den-1 p) pq mag-eq)
            (suc-injective den-eq)
