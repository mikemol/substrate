------------------------------------------------------------------------
-- Substrate.Lojban.AsCCC.RetroactiveAlignment.LojbanIsSingle
--
-- Defines: lojban-η-is-single
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.AsCCC.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsCCC.RetroactiveAlignment.LojbanIsSingle where

open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Word Gismu
open import Substrate.Lojban.AsFreeOverBasis.LojbanFreeStructure
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. η of the Lojban FreeOverBasis IS the `single` lift.
--
-- Connects the Classification arc's basis embedding to the L2
-- Word module's basis embedding.
------------------------------------------------------------------------

lojban-η-is-single :
  (g : Gismu) → η lojban-free-structure g ≡ single g
lojban-η-is-single _ = refl
