------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.CostCarriedNonredex
--
-- Defines: cost-carried-nonredex
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.CostCarriedNonredex where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.Cost


cost-carried-nonredex : (x y : Tm) → cost (S ∙ x) ≡ 0     -- S∙x needs 3 args: no head redex
cost-carried-nonredex x y = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the two-index braiding, instantiated): the SKI
-- term→shedding is the SPPF's TWO indexes, and the substrate already holds them
-- parametrically as GradedDivStr: the grade = the reduce/cost index (the Nf
-- obstruction, carried), the remainder = the peel/structure index (the subterm,
-- kept). The flat Trace ℕ-shed collapsed the cost because it is the DEGENERATE
-- (grade-0) shadow; the graded wedge is the faithful form. This reskins EEATrace's
-- (quotient, remainder) and CrossMulGraded's varying-degree cross onto SKI —
-- "almost everything in the repo is a parameterization of something else." The
-- cost is carried by CONSTRUCTION; the zero-collapse was the un-graded projection.
------------------------------------------------------------------------
