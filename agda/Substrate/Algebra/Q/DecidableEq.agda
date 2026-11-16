------------------------------------------------------------------------
-- Substrate.Algebra.Q.DecidableEq
--
-- Q3 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Syntactic decidable equality on ℚ. Two ℚ records are
-- propositionally equal iff their num and den-1 fields are equal.
-- Mathematical equivalence up to reduction (1/2 ≡ 2/4) is
-- handled at Q4 (Reduction) + a reduction-respecting equivalence
-- at Q5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.DecidableEq where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec

open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.NatDec
open import Substrate.Algebra.Q.Rat
open import Substrate.Foundation.Eq

------------------------------------------------------------------------
-- 1. Syntactic decidable equality.
--
-- Reduces to decidable equality on ℤ (num field) and ℕ (den-1
-- field) componentwise.
------------------------------------------------------------------------

_≟ℚ_ : (p q : ℚ) → Dec (p ≡ q)
mkℚ n₁ d₁ ≟ℚ mkℚ n₂ d₂ with n₁ ≟ℤ n₂ | ℕ-≟ d₁ d₂
... | yes refl | yes refl = yes refl
... | yes _    | no ¬eq   = no (λ { refl → ¬eq refl })
... | no ¬eq   | _        = no (λ { refl → ¬eq refl })

------------------------------------------------------------------------
-- 2. Capstone for Q3.
--
-- Syntactic ≟ℚ landed. Q4 adds the gcd-reduction to canonical
-- form, after which two ℚ values represent the SAME rational iff
-- their reduced forms are syntactically equal.
------------------------------------------------------------------------
