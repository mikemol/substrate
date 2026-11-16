------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.Preamble
--
-- Defines: Preamble
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.Preamble where




------------------------------------------------------------------------
-- 1. Relation composition at the word level.
--
-- R₁ ∘ᴿ R₂ = R₁ then R₂ (categorical-convention: read right-to-left
-- as relation composition; here we use the FREE convention where
-- word concatenation IS the composition, so the left operand goes
-- first in the resulting word).
------------------------------------------------------------------------
