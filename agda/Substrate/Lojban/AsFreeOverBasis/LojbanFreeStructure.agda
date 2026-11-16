------------------------------------------------------------------------
-- Substrate.Lojban.AsFreeOverBasis.LojbanFreeStructure
--
-- Defines: lojban-free-structure
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.AsFreeOverBasis; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsFreeOverBasis.LojbanFreeStructure where

open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Word Gismu
open import Substrate.Category.FreeOverBasis



------------------------------------------------------------------------
-- 1. The FreeOverBasis instance for Lojban.
--
-- Basis: Gismu (the vocabulary basis from L3).
-- Free carrier: LojbanWord (the Coxeter-Word-backed free monoid).
-- Unit: single — each gismu lifts to a one-symbol word.
--
-- The substantive universal property (free-monoid extension via
-- WordAlgebra.WithTarget; homomorphism law via WordAlgebra.extend-
-- merge) is unchanged from L8.
------------------------------------------------------------------------

lojban-free-structure : FreeOverBasis Gismu LojbanWord
lojban-free-structure = mkFreeOverBasis single
