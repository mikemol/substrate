------------------------------------------------------------------------
-- eval-args ON THE GENERATOR is faithful-rb via the graded vector — the antilog at
-- the grade. The generator is KEPT (that is what faithful means here).
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulGraded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.EvalArgs

faithful-graded : (g : Gen) {n : ℕ} → Vec Tm n → Tm
faithful-graded g v = eval-args (gen→tm g) v
