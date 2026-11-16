------------------------------------------------------------------------
-- Substrate.Algebra.F1.AsModule.F1Module
--
-- Defines: F₁-Module
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.AsModule; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.AsModule.F1Module where

open import Substrate.Algebra.PointedSet



------------------------------------------------------------------------
-- 1. The categorical identification.
------------------------------------------------------------------------

-- ⟡set1-paydown: PointedSet is now the carrier-indexed family; F₁-Module and its
-- Hom / id / compose thread the carrier(s).
F₁-Module : Set → Set
F₁-Module = PointedSet
