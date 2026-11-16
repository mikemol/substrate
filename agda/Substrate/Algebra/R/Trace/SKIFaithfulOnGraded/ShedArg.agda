------------------------------------------------------------------------
-- ③ The shed head (gcell) IS the applied argument — the digit at this grade.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.ShedArg where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecCell
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.ApplyOneGraded
open import Substrate.Foundation.Eq

shed-arg : (n : ℕ) (v : Vec Tm n) (a : Tm) → gcell (apply-one-graded n v a) ≡ a
shed-arg = vec-cell Tm
