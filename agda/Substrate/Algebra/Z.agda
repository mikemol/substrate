------------------------------------------------------------------------
-- Substrate.Algebra.Z
--
-- Q1 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Substrate-native ℤ via two-constructor canonical-form encoding:
-- non-negative ints are `+ n` (where n : ℕ); strictly-negative
-- ints are `-suc n` (representing -(suc n) = -1, -2, ...).
-- This avoids the double-zero pitfall: each integer has exactly
-- one constructor pattern.
--
-- Per [[feedback-minimize-stdlib-deps]]-strengthened: substrate-
-- native to avoid Data.Integer's broader ecosystem. The encoding
-- mirrors stdlib's representation but stays in the substrate's
-- namespace.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)

------------------------------------------------------------------------
-- 1. The ℤ data type.
--
-- Two constructors:
--   * `+ n` for n ≥ 0 (so + 0 is the unique zero, + 1 = 1, etc.)
--   * `-suc n` for the negative integer -(suc n) (so -suc 0 = -1,
--     -suc 1 = -2, etc.)
------------------------------------------------------------------------

data ℤ : Set where
  +_    : ℕ → ℤ
  -suc_ : ℕ → ℤ

------------------------------------------------------------------------
-- 2. Named constants.
------------------------------------------------------------------------

0ℤ : ℤ
0ℤ = + 0

1ℤ : ℤ
1ℤ = + 1

-1ℤ : ℤ
-1ℤ = -suc 0

------------------------------------------------------------------------
-- 3. Negation.
--
-- - (+ 0)      = + 0           (zero is self-negating)
-- - (+ suc n)  = -suc n
-- - (-suc n)   = + suc n
------------------------------------------------------------------------

-ℤ_ : ℤ → ℤ
-ℤ (+ zero)    = + zero
-ℤ (+ suc n)   = -suc n
-ℤ (-suc n)    = + suc n

------------------------------------------------------------------------
-- 4. Decidable equality.
--
-- ℤ has decidable equality (both ℕ-indexed branches are
-- injective constructors). Useful for the ℚ canonical-form
-- comparisons in Q3.
------------------------------------------------------------------------

ℕ-≟ : (m n : ℕ) → Dec (m ≡ n)
ℕ-≟ zero    zero    = yes refl
ℕ-≟ zero    (suc _) = no (λ ())
ℕ-≟ (suc _) zero    = no (λ ())
ℕ-≟ (suc m) (suc n) with ℕ-≟ m n
... | yes refl = yes refl
... | no  ¬eq  = no (λ { refl → ¬eq refl })

_≟ℤ_ : (a b : ℤ) → Dec (a ≡ b)
(+ m)    ≟ℤ (+ n)    with ℕ-≟ m n
... | yes refl = yes refl
... | no  ¬eq  = no (λ { refl → ¬eq refl })
(+ _)    ≟ℤ (-suc _) = no (λ ())
(-suc _) ≟ℤ (+ _)    = no (λ ())
(-suc m) ≟ℤ (-suc n) with ℕ-≟ m n
... | yes refl = yes refl
... | no  ¬eq  = no (λ { refl → ¬eq refl })

------------------------------------------------------------------------
-- 5. Double negation: -ℤ (-ℤ z) ≡ z.
------------------------------------------------------------------------

-ℤ-involutive : (z : ℤ) → -ℤ (-ℤ z) ≡ z
-ℤ-involutive (+ zero)  = refl
-ℤ-involutive (+ suc _) = refl
-ℤ-involutive (-suc _)  = refl

------------------------------------------------------------------------
-- 6. Capstone for Q1.
--
-- Substrate-native ℤ with negation + decidable equality + double-
-- negation involution. Q2 builds ℚ on top.
------------------------------------------------------------------------
