------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical
--
-- CAPSTONE: the `Canonical ℚ-Quotient` instance, with reduced-form
-- uniqueness supplied by the continued-fraction shape (the SPPF/EEA route).
--
-- The whole arc collapses to `canonical-respects-≈ : a ≈ℚ b → reduce a ≡
-- reduce b`. We discharge it through the `reduced-≈⇒≡` spine:
--   reduce a ≈ℚ a ≈ℚ b ≈ℚ reduce b   (≈-canonical + the ℚ setoid)
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
open import Substrate.Algebra.Quotient using () renaming (Canonical to Canonical⟦30f92ad5⟧)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-sym; ≈ℚ-trans; ℚ-Quotient)
open import Substrate.Algebra.Q.Reduce using (reduce; reduce-build; sign-of)
open import Substrate.Algebra.Q.Reduction using (is-reduced; abs-ℤ)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-canonical)
open import Substrate.Algebra.Q.Properties.Abs using (abs-sign-of; abs-*ℤ-pos; ℤ-sign-mag)
open import Substrate.Algebra.Nat.Divides using (_∣_; divides)
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

reduced-≈⇒≡ : (p q : ℚ) → is-reduced p → is-reduced q → p ≈ℚ q → p ≡ q
reduced-≈⇒≡ p q rp rq pq = cong₂ mkℚ num-eq (suc-injective den-eq)
  where
    -- magnitude cross-equation (sign-stripped p ≈ℚ q)
    mag-cross : abs-ℤ (num p) * denominator q ≡ abs-ℤ (num q) * denominator p
    mag-cross = trans (sym (abs-*ℤ-pos (num p) (den-1 q)))
                (trans (cong abs-ℤ pq) (abs-*ℤ-pos (num q) (den-1 p)))
    -- coprime traces of the two reduced fractions, compared directly
    inj : (abs-ℤ (num p) ≡ abs-ℤ (num q)) × (denominator p ≡ denominator q)
    inj = cf-injective
            (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
            (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
            (shape-value-invariance
              (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
              (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
              (s≤s z≤n) (s≤s z≤n) mag-cross)
    den-eq : denominator p ≡ denominator q
    den-eq = proj₂ inj
    num-eq : num p ≡ num q
    num-eq = ℤ-sign-mag (num p) (num q) (den-1 q) (den-1 p) pq (proj₁ inj)

------------------------------------------------------------------------
-- 3. The capstone obligation + the instance.
------------------------------------------------------------------------

canonical-respects-≈ : {a b : ℚ} → a ≈ℚ b → reduce a ≡ reduce b
canonical-respects-≈ {a} {b} hab =
  reduced-≈⇒≡ (reduce a) (reduce b) (reduce-is-reduced a) (reduce-is-reduced b)
    (≈ℚ-trans {reduce a} {a} {reduce b}
       (≈ℚ-sym {a} {reduce a} (≈-canonical a))
       (≈ℚ-trans {a} {b} {reduce b} hab (≈-canonical b)))

ℚ-Canonical : Canonical⟦30f92ad5⟧ ℚ-Quotient
ℚ-Canonical = record
  { canonical            = reduce
  ; canonical-idempotent = λ a → sym (canonical-respects-≈ (≈-canonical a))
  ; canonical-respects-≈ = canonical-respects-≈
  ; ≈-canonical          = ≈-canonical
  }

------------------------------------------------------------------------
-- 4. Worked examples: respect-≈ computes on closed witnesses (2/4 ≈ 1/2).
------------------------------------------------------------------------

private
  open import Substrate.Algebra.Z using (+_)
  -- 2/4 ≈ℚ 1/2 (both reduce to 1/2); respect-≈ applies on the closed witness.
  _ : reduce (mkℚ (+ 2) 3) ≡ reduce (mkℚ (+ 1) 1)
  _ = canonical-respects-≈ {mkℚ (+ 2) 3} {mkℚ (+ 1) 1} refl
