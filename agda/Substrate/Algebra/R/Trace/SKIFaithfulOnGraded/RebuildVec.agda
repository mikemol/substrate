------------------------------------------------------------------------
-- ③ The forgetful read rebuilds the consed vector — the grade-(suc n) carrier.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.RebuildVec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecForget
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.ApplyOneGraded
open import Substrate.Foundation.Eq

rebuild-vec : (n : ℕ) (v : Vec Tm n) (a : Tm) → gforget (apply-one-graded n v a) ≡ (a ∷ v)
rebuild-vec = vec-forget Tm
