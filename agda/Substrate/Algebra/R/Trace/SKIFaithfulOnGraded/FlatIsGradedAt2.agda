------------------------------------------------------------------------
-- ⑤ THE BRIDGE: the flat fixed-3 recon (q∙b)∙r IS the graded fold at grade 2 —
-- the flat form is the grade-COLLAPSED shadow frozen at one shape.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FlatIsGradedAt2 where

open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.EvalArgs
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm

flat-is-graded-at-2 : (q b r : Tm) → eval-args q (b ∷ r ∷ []) ≡ ((q ∙ b) ∙ r)
flat-is-graded-at-2 q b r = refl
