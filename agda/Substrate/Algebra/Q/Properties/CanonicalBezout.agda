------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.CanonicalBezout
--
-- The SECOND, redundant route to ℚ reduced-form uniqueness: Bézout/Euclid,
-- cross-navigating the CF-shape route (Q.Properties.Canonical).
--
-- Both routes prove the SAME proposition `canonical-respects-≈ : a ≈ℚ b →
-- reduce a ≡ reduce b`, share the SAME assembly (uniq-from-mag-den) and the
-- SAME reduce-is-reduced, and differ ONLY in how they pin the components:
--   * shape route:  cf-injective on coprime traces (KEYSTONE #1 + #2)
--   * Bézout route: Euclid's lemma (coprime + a∣b·c ⟹ a∣c) twice + ∣-antisym
-- giving denominator equality, then magnitude cancellation. "Convergence
-- without loss of demonstrable fluency": two independent witnesses, one type.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.CanonicalBezout where

open import Substrate.Foundation.Nat using (_*_)
open import Substrate.Foundation.Nat.Properties.Cancel using (*-cancelʳ-suc)
open import Substrate.Foundation.Eq using (_≡_; sym; subst)
open import Substrate.Algebra.Quotient using () renaming (Canonical to Canonical⟦30f92ad5⟧)
open import Substrate.Algebra.Q using (ℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-sym; ≈ℚ-trans; ℚ-Quotient)
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.Reduction using (is-reduced; abs-ℤ)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-canonical)
open import Substrate.Algebra.Q.Properties.Uniqueness using (mag-cross-of-≈; uniq-from-mag-den)
open import Substrate.Algebra.Q.Properties.Canonical using (reduce-is-reduced)
open import Substrate.Algebra.Nat.Divides using (_∣_; n∣m*n; ∣-antisym)
open import Substrate.Algebra.Z.Euclid using (euclid)

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

------------------------------------------------------------------------
-- The capstone obligation + instance, via the Bézout route. Same reduce,
-- same reduce-is-reduced, same ≈ℚ spine as the shape route.
------------------------------------------------------------------------

canonical-respects-≈-bezout : {a b : ℚ} → a ≈ℚ b → reduce a ≡ reduce b
canonical-respects-≈-bezout {a} {b} hab =
  reduced-≈⇒≡-bezout (reduce a) (reduce b) (reduce-is-reduced a) (reduce-is-reduced b)
    (≈ℚ-trans {reduce a} {a} {reduce b}
       (≈ℚ-sym {a} {reduce a} (≈-canonical a))
       (≈ℚ-trans {a} {b} {reduce b} hab (≈-canonical b)))

ℚ-Canonical-bezout : Canonical⟦30f92ad5⟧ ℚ-Quotient
ℚ-Canonical-bezout = record
  { canonical            = reduce
  ; canonical-idempotent = λ a → sym (canonical-respects-≈-bezout (≈-canonical a))
  ; canonical-respects-≈ = canonical-respects-≈-bezout
  ; ≈-canonical          = ≈-canonical
  }

private
  open import Substrate.Algebra.Q using (mkℚ)
  open import Substrate.Algebra.Z using (+_)
  open import Substrate.Foundation.Eq using (refl)
  -- The Bézout route agrees on the same closed witness (2/4 ≈ 1/2).
  _ : reduce (mkℚ (+ 2) 3) ≡ reduce (mkℚ (+ 1) 1)
  _ = canonical-respects-≈-bezout {mkℚ (+ 2) 3} {mkℚ (+ 1) 1} refl
