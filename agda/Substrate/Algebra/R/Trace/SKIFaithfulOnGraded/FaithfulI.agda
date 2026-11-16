------------------------------------------------------------------------
-- ④ I (arity 1) applied to a length-1 arg-vector: reconstructed at grade 1.
-- Context: Substrate/Algebra/R/Trace/SKIFaithfulOnGraded/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulI where

open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
open import Substrate.Algebra.R.Trace.SKIFaithfulOnGraded.FaithfulGraded
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm

faithful-I : faithful-graded gI (S ∷ []) ≡ (I ∙ S)
faithful-I = refl
