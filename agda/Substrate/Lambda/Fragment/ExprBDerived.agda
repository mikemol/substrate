------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.ExprBDerived
--
-- Defines: expr-B-derived
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.ExprBDerived where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.SKIWord



-- B as a composed expression: S(KS)K — when applied to the basis,
-- this performs function composition.
expr-B-derived : SKIWord
expr-B-derived = S ∷ K ∷ S ∷ K ∷ []
