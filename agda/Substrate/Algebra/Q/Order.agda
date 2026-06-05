------------------------------------------------------------------------
-- Substrate.Algebra.Q.Order
--
-- Q6 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Ordering on ℚ. For p = a/b and q = c/d (with b, d > 0):
--   p ≤ q  ⟺  a*d ≤ c*b   (cross-multiplication; valid because
--                          both denominators are positive)
--
-- Reduces to ℤ ordering, which case-splits on signs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Order where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; _*_)
  renaming (z≤n to ℕ-z≤n; s≤s to ℕ-s≤s)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)

------------------------------------------------------------------------
-- 1. ℤ ordering.
--
-- Four cases based on the signs of the two operands.
------------------------------------------------------------------------

data _≤ℤ_ : ℤ → ℤ → Set where
  +≤+ : ∀ {m n} → m ≤ n → (+ m) ≤ℤ (+ n)
  -≤+ : ∀ {m n} → (-suc m) ≤ℤ (+ n)
  -≤- : ∀ {m n} → n ≤ m → (-suc m) ≤ℤ (-suc n)

-- Reflexivity at ℤ.
≤ℤ-refl : (z : ℤ) → z ≤ℤ z
≤ℤ-refl (+ zero)    = +≤+ ℕ-z≤n
≤ℤ-refl (+ suc n)   = +≤+ (≤ℤ-refl-ℕ (suc n))
  where
    ≤ℤ-refl-ℕ : (n : ℕ) → n ≤ n
    ≤ℤ-refl-ℕ zero    = ℕ-z≤n
    ≤ℤ-refl-ℕ (suc n) = ℕ-s≤s (≤ℤ-refl-ℕ n)
≤ℤ-refl (-suc n) = -≤- (≤ℤ-refl-helper n)
  where
    ≤ℤ-refl-helper : (n : ℕ) → n ≤ n
    ≤ℤ-refl-helper zero    = ℕ-z≤n
    ≤ℤ-refl-helper (suc n) = ℕ-s≤s (≤ℤ-refl-helper n)

------------------------------------------------------------------------
-- 2. ℚ ordering via cross-multiplication.
--
-- p = a/b ≤ q = c/d iff a*d ≤ c*b (when b, d > 0).
-- Stored as a*d ≤ℤ c*b on the cross-products.
------------------------------------------------------------------------

_≤ℚ_ : ℚ → ℚ → Set
p ≤ℚ q =
  let a = num p
      b₋ = den-1 p
      c = num q
      d₋ = den-1 q
      b = suc b₋
      d = suc d₋
  in (a *ℤ (+ d)) ≤ℤ (c *ℤ (+ b))

------------------------------------------------------------------------
-- 3. Reflexivity at ℚ (modulo the cross-product reduction).
--
-- For p = a/b: p ≤ p iff a*b ≤ a*b, which is ≤ℤ-refl on (a*b).
------------------------------------------------------------------------

≤ℚ-refl : (p : ℚ) → p ≤ℚ p
≤ℚ-refl p = ≤ℤ-refl _

------------------------------------------------------------------------
-- 4. Capstone for Q6.
--
-- ℚ ordering via cross-multiplication. Q7 supplies ℕ → ℚ and
-- ℤ → ℚ embeddings; Q8 + Q9 build the ℚ-Vector + ℚ-Linear
-- sister structures.
------------------------------------------------------------------------
