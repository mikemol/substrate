------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical
--
-- CAPSTONE: the `Canonical ℚ-Quotient` instance, with reduced-form
-- uniqueness supplied by the continued-fraction shape (the SPPF/EEA route).
--
-- The whole arc collapses to `reduce-respects-≈ : a ≈ℚ b → reduce a ≡
-- reduce b`. We discharge it through the `reduced-≈⇒≡` spine:
--   reduce a ≈ℚ a ≈ℚ b ≈ℚ reduce b   (≈-reduce + the ℚ setoid)
-- gives `reduce a ≈ℚ reduce b` for free, leaving "two REDUCED, ≈ℚ-equal ℚ
-- are propositionally ≡". That is the shape uniqueness cashed out: both
-- reduced fractions have coprime traces (reduce-is-reduced), equal value ⟹
-- equal shape (shape-value-invariance, KEYSTONE #1), and equal shape + coprime
-- ⟹ equal (num,den) (cf-injective, KEYSTONE #2). Because both sides are
-- already reduced, the traces are compared DIRECTLY — no scale-invariance step.
--
-- `Register`/`intern`/`PackedTree` are the address-interning realization of
-- the same shape-as-canonical-key principle; the propositional half (KEYSTONE
-- #1 + #2) is what this proof consumes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Cancel using (suc-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Z using (ℤ)
open import Substrate.Algebra.Quotient
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-sym; ≈ℚ-trans; ℚ-Quotient)
open import Substrate.Algebra.Q.Reduce using (reduce; reduce-build; sign-of)
open import Substrate.Algebra.Q.Reduction using (is-reduced; abs-ℤ)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-reduce)
open import Substrate.Algebra.Q.Properties.Abs using (abs-sign-of)
open import Substrate.Algebra.Q.Properties.Uniqueness using (mag-cross-of-≈; uniq-from-mag-den)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft using (gcd-divides-left)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (coprime-trace)
open import Substrate.Algebra.Nat.GCD.CFInvariance using (shape-value-invariance)
open import Substrate.Algebra.Nat.GCD.CFInjective using (cf-injective)
open import Substrate.Algebra.Z.Coprime using (cofactor-coprime)

------------------------------------------------------------------------
-- 1. reduce produces a reduced fraction (cofactor coprimality, lifted to ℚ).
--    Worker over reduce-build's witnesses (so it reduces transparently).
------------------------------------------------------------------------

reduced-build :
  (sgn : ℤ) (na d : ℕ)
  (dl : gcd-ℕ na (suc d) ∣ na) (dr : gcd-ℕ na (suc d) ∣ suc d) →
  gcd-ℕ (abs-ℤ (num (reduce-build sgn dl dr))) (denominator (reduce-build sgn dl dr)) ≡ 1
reduced-build sgn na d (divides qn eqn) (divides (suc qd′) eqd) =
  subst (λ x → gcd-ℕ x (suc qd′) ≡ 1) (sym (abs-sign-of sgn qn))
        (cofactor-coprime na d qn (suc qd′) eqn eqd)
reduced-build sgn na d (divides qn eqn) (divides zero ())

reduce-is-reduced : (q : ℚ) → is-reduced (reduce q)
reduce-is-reduced q =
  reduced-build (num q) (abs-ℤ (num q)) (den-1 q)
    (gcd-divides-left  (abs-ℤ (num q)) (denominator q))
    (gcd-divides-right (abs-ℤ (num q)) (denominator q))

------------------------------------------------------------------------
-- 2. Two REDUCED, ≈ℚ-equal ℚ are propositionally equal (shape uniqueness).
------------------------------------------------------------------------

-- Route 1 (CF shape): the components come from cf-injective on the two coprime
-- traces, compared DIRECTLY (KEYSTONE #1 value-invariance feeds KEYSTONE #2).
reduced-≈⇒≡ : (p q : ℚ) → is-reduced p → is-reduced q → p ≈ℚ q → p ≡ q
reduced-≈⇒≡ p q rp rq pq = uniq-from-mag-den p q (proj₁ inj) (proj₂ inj) pq
  where
    inj : (abs-ℤ (num p) ≡ abs-ℤ (num q)) × (denominator p ≡ denominator q)
    inj = cf-injective
            (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
            (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
            (shape-value-invariance
              (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
              (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
              (s≤s z≤n) (s≤s z≤n) (mag-cross-of-≈ p q pq))

------------------------------------------------------------------------
-- 3. The capstone obligation + the instance.
------------------------------------------------------------------------

reduce-respects-≈ : {a b : ℚ} → a ≈ℚ b → reduce a ≡ reduce b
reduce-respects-≈ {a} {b} hab =
  reduced-≈⇒≡ (reduce a) (reduce b) (reduce-is-reduced a) (reduce-is-reduced b)
    (≈ℚ-trans {reduce a} {a} {reduce b}
       (≈ℚ-sym {a} {reduce a} (≈-reduce a))
       (≈ℚ-trans {a} {b} {reduce b} hab (≈-reduce b)))

ℚ-Canonical : Canonical ℚ-Quotient
ℚ-Canonical = record
  { canonical            = reduce
  ; canonical-idempotent = λ a → sym (reduce-respects-≈ (≈-reduce a))
  ; canonical-respects-≈ = reduce-respects-≈
  ; ≈-canonical          = ≈-reduce
  }

------------------------------------------------------------------------
-- 4. Worked examples: respect-≈ computes on closed witnesses (2/4 ≈ 1/2).
------------------------------------------------------------------------

private
  open import Substrate.Algebra.Z using (+_)
  -- 2/4 ≈ℚ 1/2 (both reduce to 1/2); respect-≈ applies on the closed witness.
  _ : reduce (mkℚ (+ 2) 3) ≡ reduce (mkℚ (+ 1) 1)
  _ = reduce-respects-≈ {mkℚ (+ 2) 3} {mkℚ (+ 1) 1} refl
