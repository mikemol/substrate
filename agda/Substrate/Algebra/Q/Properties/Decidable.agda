------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable
--
-- Decidable ℚ semantic equality, routed through the SPPF shape interning —
-- the finite-domain decision that converges with the propositional uniqueness.
--
--   q-key       : the CF shape of |num|/den (the interned canonical key)
--   key-faithful: for REDUCED p,q, equal key ⟹ equal magnitude AND denominator
--                 (cf-injective, KEYSTONE #2; via subst-shape to relate the
--                 gcd-trace key to the coprime trace)
--   _≈ℚ?_       : Dec (a ≈ℚ b), deciding reduce a ≡ reduce b by comparing the
--                 reduced shape keys with the Register's `_≟ˢ_` (short-circuit
--                 on shape mismatch) and the numerators with `_≟ℤ_`
--
-- This de-orphans Register: `_≟ˢ_` is now a load-bearing decision step proven
-- to agree with `canonical-respects-≈` (≈ℚ ⟺ reduce a ≡ reduce b). Two views —
-- the propositional uniqueness proof and the operational shape comparison —
-- decide the same relation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Nat.Properties.Cancel using (suc-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.List using (List)
open import Substrate.Algebra.Z using (ℤ; _≟ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.Reduction using (is-reduced; abs-ℤ)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-canonical)
open import Substrate.Algebra.Q.Properties.Canonical using (canonical-respects-≈; reduce-is-reduced)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace; coprime-trace)
open import Substrate.Algebra.Nat.GCD.CFInjective using (cf-injective)
open import Substrate.Algebra.Wedge.Shape using (ℕ-shape; WedgeShape)
open import Substrate.Algebra.Wedge.Shape.Register using (_≟ˢ_)

------------------------------------------------------------------------
-- 1. The shape key (the interned CF of |num|/den) and its faithfulness.
------------------------------------------------------------------------

q-key : ℚ → WedgeShape
q-key q = ℕ-shape (gcd-trace (abs-ℤ (num q)) (denominator q))

-- ℕ-shape ignores the gcd index, so transporting it (coprime-trace = subst on
-- gcd-trace) does not change the shape.
private
  subst-shape : {a b g g′ : ℕ} (eq : g ≡ g′) (t : EEATrace a b g) →
                ℕ-shape (subst (EEATrace a b) eq t) ≡ ℕ-shape t
  subst-shape refl t = refl

key-faithful : (p q : ℚ) → is-reduced p → is-reduced q → q-key p ≡ q-key q →
               (abs-ℤ (num p) ≡ abs-ℤ (num q)) × (denominator p ≡ denominator q)
key-faithful p q rp rq key-eq =
  cf-injective (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
               (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
               (trans (subst-shape rp (gcd-trace (abs-ℤ (num p)) (denominator p)))
               (trans key-eq
                      (sym (subst-shape rq (gcd-trace (abs-ℤ (num q)) (denominator q))))))

------------------------------------------------------------------------
-- 2. ≈ℚ ⟺ reduce a ≡ reduce b (the bridge to the canonical form).
------------------------------------------------------------------------

private
  re→≈ : {a b : ℚ} → reduce a ≡ reduce b → a ≈ℚ b
  re→≈ {a} {b} re =
    ≈ℚ-trans {a} {reduce a} {b} (≈-canonical a)
      (subst (λ r → r ≈ℚ b) (sym re) (≈ℚ-sym {b} {reduce b} (≈-canonical b)))

------------------------------------------------------------------------
-- 3. The decision: compare reduced shape keys (Register) + numerators.
------------------------------------------------------------------------

reduce-eq? : (a b : ℚ) → Dec (reduce a ≡ reduce b)
reduce-eq? a b with q-key (reduce a) ≟ˢ q-key (reduce b)
... | no  key≢ = no (λ re → key≢ (cong q-key re))
... | yes key≡ with num (reduce a) ≟ℤ num (reduce b)
...   | no  num≢ = no (λ re → num≢ (cong num re))
...   | yes num≡ =
          yes (cong₂ mkℚ num≡
                 (suc-injective
                   (proj₂ (key-faithful (reduce a) (reduce b)
                            (reduce-is-reduced a) (reduce-is-reduced b) key≡))))

_≈ℚ?_ : (a b : ℚ) → Dec (a ≈ℚ b)
a ≈ℚ? b with reduce-eq? a b
... | yes re = yes (re→≈ re)
... | no ¬re = no (λ a≈b → ¬re (canonical-respects-≈ a≈b))

private
  open import Substrate.Algebra.Z using (+_)
  open import Substrate.Foundation.Bool using (Bool; true; false)

  isYes : {A : Set} → Dec A → Bool
  isYes (yes _) = true
  isYes (no  _) = false

  -- The decision actually FIRES on closed inputs (forces _≟ˢ_ to compute):
  -- 2/4 ≈ℚ 1/2 ⟹ YES; 1/2 ≈ℚ 1/3 ⟹ NO (the reduced shape keys differ).
  _ : isYes ((mkℚ (+ 2) 3) ≈ℚ? (mkℚ (+ 1) 1)) ≡ true
  _ = refl
  _ : isYes ((mkℚ (+ 1) 1) ≈ℚ? (mkℚ (+ 1) 2)) ≡ false
  _ = refl
