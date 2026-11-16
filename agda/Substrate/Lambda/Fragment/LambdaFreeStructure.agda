------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.LambdaFreeStructure
--
-- Defines: lambda-free-structure
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.LambdaFreeStructure where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Category.FreeOverBasis
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.SKIWord
open import Substrate.Lambda.Fragment.Single



------------------------------------------------------------------------
-- 4. The FreeOverBasis instance.
------------------------------------------------------------------------

lambda-free-structure : FreeOverBasis Combinator SKIWord
lambda-free-structure = mkFreeOverBasis single
