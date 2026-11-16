------------------------------------------------------------------------
-- ① THE ARITY-GRADED CARRIER: VecGraded at the SKI argument type. A combinator's
-- argument list is a graded Vec Tm; its LENGTH is the arity — grade = arity BY THE TYPE.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.ArgGraded where

open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecGraded
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm

arg-graded : GradedDivStr (Vec Tm) (λ _ → Tm)
arg-graded = vec-graded Tm
