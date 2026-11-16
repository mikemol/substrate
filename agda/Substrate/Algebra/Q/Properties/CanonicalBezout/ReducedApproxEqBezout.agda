------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.CanonicalBezout.ReducedApproxEqBezout
--
-- Defines: reduced-≈⇒≡-bezout
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.CanonicalBezout; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.CanonicalBezout.ReducedApproxEqBezout where

open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Cancel
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.IsReduced
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Uniqueness
open import Substrate.Algebra.Nat.Divides.Antisym
open import Substrate.Algebra.Nat.Divides.Mul
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Z.Euclid
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.JacobianEvalCD



------------------------------------------------------------------------
-- Route 2 (Bézout/Euclid): denominators divide each other (Euclid, both ways)
-- hence are equal (∣-antisym); then magnitudes cancel.
------------------------------------------------------------------------

reduced-≈⇒≡-bezout : (p q : ℚ) → is-reduced p → is-reduced q → p ≈ℚ q → p ≡ q
reduced-≈⇒≡-bezout p q rp rq pq = uniq-from-mag-den p q mag-eq den-eq pq
  where
    mag-cross : abs-ℤ (num p) * denominator q ≡ abs-ℤ (num q) * denominator p
    mag-cross = mag-cross-of-≈ p q pq
    dp∣dq : denominator p ∣ denominator q
    dp∣dq = euclid (abs-ℤ (num p)) (den-1 p) (denominator q) rp
              (subst (denominator p ∣_) (sym mag-cross)
                     (n∣m*n (abs-ℤ (num q)) {denominator p}))
    dq∣dp : denominator q ∣ denominator p
    dq∣dp = euclid (abs-ℤ (num q)) (den-1 q) (denominator p) rq
              (subst (denominator q ∣_) mag-cross
                     (n∣m*n (abs-ℤ (num p)) {denominator q}))
    den-eq : denominator p ≡ denominator q
    den-eq = ∣-antisym dp∣dq dq∣dp
    mag-eq : abs-ℤ (num p) ≡ abs-ℤ (num q)
    mag-eq = *-cancelʳ-suc (abs-ℤ (num p)) (abs-ℤ (num q)) (den-1 p)
               (subst (λ d → abs-ℤ (num p) * d ≡ abs-ℤ (num q) * denominator p)
                      (sym den-eq) mag-cross)
