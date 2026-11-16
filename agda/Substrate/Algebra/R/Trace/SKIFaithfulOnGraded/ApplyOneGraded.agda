------------------------------------------------------------------------
-- A grade-raising step IS applying (consing) one argument — recon is cons.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.ApplyOneGraded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecStep
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.ArgGraded

apply-one-graded : (n : ℕ) (v : Vec Tm n) (a : Tm) → GradedWedge arg-graded n (a ∷ v) v
apply-one-graded = vec-step Tm
