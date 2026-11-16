------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.SKIWord
--
-- Defines: SKIWord
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.SKIWord where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Lambda.Fragment.Combinator



------------------------------------------------------------------------
-- 2. SKI expressions as Coxeter words over combinators.
--
-- A linear "applicative" sequence; richer expression trees (with
-- explicit branching) are deferred to the substrate's existing
-- OpcodeAlgebra / lambda-VM infrastructure where the R-arc
-- already provides the CCC structure.
------------------------------------------------------------------------

SKIWord : Set
SKIWord = Word Combinator
