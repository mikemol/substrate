------------------------------------------------------------------------
-- ② THE FAITHFUL RECONSTRUCTION IS THE GRADED FOLD: fold apply (∙) over a grade-n
-- argument vector. The result's grade is n = the arity (args applied left-to-right).
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.EvalArgs where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
-- ⚑ `Tm` AND `_∙_` HAD NO PROVIDER — `[NotInScope]` at 14.18-20. Unlike the
-- `Fin/Op2`/`Op3` failures (a horizontal split that dropped a `renaming` and left
-- the body naming `<ℕ`), this file was simply missing an import: nothing it opened
-- supplied the SKI term type or its application operator.
-- ⚑ ONE LEAF SUPPLIES BOTH, so there is no ambiguity to arbitrate — `--provides`
-- on it reports exactly `I K S Tm _∙_ ∙`, which is the bare-import shape the ban
-- wants (a consumer takes all of a small leaf rather than filtering a barrel).
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm

eval-args : (f : Tm) {n : ℕ} → Vec Tm n → Tm
eval-args f []       = f
eval-args f (a ∷ v)  = eval-args (f ∙ a) v
