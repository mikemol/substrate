------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.LambdaWitness
--
-- Defines: lambda-witness
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.LambdaWitness where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Category.FreeOverBasis
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.SKIWord
open import Substrate.Lambda.Fragment.LambdaFreeStructure



lambda-witness : LanguageWitness Combinator SKIWord
lambda-witness = mkWitness
  Lambda
  lambda-free-structure
  Free-CCC

------------------------------------------------------------------------
-- 5. The bridge note.
--
-- The substrate's R-arc lambda-VM ([[project-rarc-lambda-vm-recognition]])
-- IS the operational realisation of this Free CCC. The OpcodeAlgebra
-- primitive (Substrate.Category.OpcodeAlgebra) supplies the
-- categorical home; β-reduction is the Sequitur inline-rule
-- operation. C6's witness records that the Lambda/SKI cell of the
-- linguistic classification IS the same categorical object the
-- codec arc has been operating within. Per
-- [[feedback-categorical-name-first]]: "Free CCC" names what the
-- substrate's R-arc has been doing all along.
------------------------------------------------------------------------
