------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.DivStr
--
-- The graded div-structure interface: a ℕ-graded carrier + a grade-raising
-- reconstruction from a base (grade n) and a digit (the remainder R n).
-- See dir README for the grading rationale.
--
-- Defines: GradedDivStr, recon
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.DivStr where

open import Substrate.Foundation.Nat.Nat

-- ⟡set1-paydown: C R are Set-valued families ⇒ module parameters, never
-- fields ([[set1-carrier-always-parameterize]]); GradedDivStr is Set.
module _ (C : ℕ → Set) (R : ℕ → Set) where

  record GradedDivStr : Set where
    field
      recon : (n : ℕ) → C n → R n → C (suc n)    -- the grade-raising reconstruction

  open GradedDivStr public
