------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.WitnessCount
--
-- Defines: witness-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.WitnessCount where

open import Substrate.Foundation.Nat.Nat



------------------------------------------------------------------------
-- 1. The catalogue of six witnesses.
--
-- One Lang value per occupied cell of the classification lattice.
-- The Vec-shaped collection lets C9 iterate over all pairs for
-- Rosetta-table generation. (⟡rc-lang, W5-L3: the Vec now carries
-- the Set₀ enum, not the witnesses directly — witness-of decodes.)
------------------------------------------------------------------------

witness-count : ℕ
witness-count = 6
