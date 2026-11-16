------------------------------------------------------------------------
-- ④ K (arity 2) applied to a length-2 arg-vector: reconstructed at grade 2.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulK where

open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulGraded
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm

faithful-K : faithful-graded gK (K ∷ I ∷ []) ≡ ((K ∙ K) ∙ I)
faithful-K = refl
