------------------------------------------------------------------------
-- Substrate.Lojban.AsCCC.RetroactiveAlignment.LojbanWitnessClass
--
-- Defines: lojban-witness-class
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.AsCCC.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsCCC.RetroactiveAlignment.LojbanWitnessClass where

open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 3. Witness identity.
--
-- The lojban-witness's classification, name, and η-map are exactly
-- those expected of the Free-monoid cell with Lojban as the
-- witness.
------------------------------------------------------------------------

lojban-witness-class : class lojban-witness ≡ Free-monoid
lojban-witness-class = refl
