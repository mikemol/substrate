------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SameCanonical.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.SameCanonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.SameCanonical.Private where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- Word-level decidable equality, parametric in Gen.
--
-- This IS the single generic fact: from decidable Gen, derive
-- decidable Word Gen. Each Zₙ-Coxeter same-canonical reduces to
-- calling this with the group's Gen-decidable-equality.
------------------------------------------------------------------------

-- ∷-injection: head + tail equality from cons equality.
