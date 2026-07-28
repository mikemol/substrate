------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.TraceDivides
--
-- The mutually-recursive divisibility properties of an EEATrace:
--
--   trace-divides-left  : EEATrace a b g → g ∣ a
--   trace-divides-right : EEATrace a b g → g ∣ b
--
-- Pure structural induction on the trace's constructors.
-- (Mutual recursion forces these two lemmas into one file.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.TraceDivides where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Eq using (sym; subst)
open import Substrate.Algebra.Nat.Divides.Mul using (m∣m*n; n∣m*n)
open import Substrate.Algebra.Nat.Divides.Refl using (∣-refl)
open import Substrate.Algebra.Nat.Divides.Sum using (∣m∣n⇒∣m+n)
open import Substrate.Algebra.Nat.Divides.Trans using (∣-trans)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_)
open import Substrate.Algebra.Nat.Divides.Zero using (∣-zero)
open import Substrate.Algebra.Nat.GCD.Wedge
  using (quotient; remainder; wedge-eq)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)

mutual
  trace-divides-left : ∀ {a b g} → EEATrace a b g → g ∣ a
  trace-divides-left (base _)               = ∣-refl
  trace-divides-left {a} {.(suc b)} (step b w sub-trace) =
    let q     = quotient w
        r     = remainder w
        eq    = wedge-eq w
        g∣sb  = trace-divides-left  sub-trace
        g∣r   = trace-divides-right sub-trace
        g∣qsb = ∣-trans g∣sb (n∣m*n q)
        g∣sum = ∣m∣n⇒∣m+n g∣qsb g∣r
    in subst (_ ∣_) (sym eq) g∣sum

  trace-divides-right : ∀ {a b g} → EEATrace a b g → g ∣ b
  trace-divides-right (base a)              = ∣-zero _
  trace-divides-right (step b w sub-trace)  =
    trace-divides-left sub-trace
