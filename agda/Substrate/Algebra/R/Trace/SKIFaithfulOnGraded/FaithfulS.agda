------------------------------------------------------------------------
-- ④ S (arity 3) applied to a length-3 arg-vector: reconstructed at grade 3.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulS where

open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulGraded
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm

faithful-S : faithful-graded gS (I ∷ K ∷ S ∷ []) ≡ (((S ∙ I) ∙ K) ∙ S)
faithful-S = refl
