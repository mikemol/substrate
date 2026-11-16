------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.SkiGraded
--
-- Defines: ski-graded
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.SkiGraded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.Cost



------------------------------------------------------------------------
-- 2. THE TWO-INDEX GRADED CARRIER (the SPPF braiding, reskinned onto GradedDivStr).
--   C n  = a term whose reduce-index (accumulated cost) is n — the grade IS the cost.
--   R n  = the peeled subterm digit shed at grade n (the structure/peel index).
--   recon = grade-raising: attach the peeled digit, carrying the cost up by one grade.
-- We keep C and R as plain Tm at every grade (the grade tracks the cost separately),
-- so recon is the structure-peel's inverse — app-rebuild — exactly FUSepQSKI's rcn.
------------------------------------------------------------------------
-- ⟡set1-paydown: the graded families (const Tm carrier, const Tm digit) are now params.
ski-graded : GradedDivStr (λ _ → Tm) (λ _ → Tm)
ski-graded = record
  { recon = λ _ f a → f ∙ a                -- grade-raising = app-rebuild (rcn, invertible)
  }
