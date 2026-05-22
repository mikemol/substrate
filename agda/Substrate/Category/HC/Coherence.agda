------------------------------------------------------------------------
-- Substrate.Category.HC.Coherence
--
-- HC1 of the higher-cat content arc (sub-arc A: coherence) per
-- [scratch/up_topos_arc_plan.md].
--
-- The coherence-UP: a UPArrow whose:
--   * Source = a chosen pair of morphisms ⟨f, g⟩
--   * Target = an equational witness f ≡ g
--   * Witness = "f and g denote the same morphism at the chosen
--     coherence-equivalence."
--
-- Each concrete coherence diagram (pentagon, triangle, hexagon,
-- interchange, ...) is an INSTANCE of this UPArrow, namely a UPGen
-- pointing into the coherence-UP from the structure-UP it constrains.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.Coherence where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)

------------------------------------------------------------------------
-- 1. The Coherence-UP.
--
-- Substrate-honest: the spec/inst at the structural level is ⊤;
-- the witness IS the coherence equation, parametric. HC2-HC10
-- supply specific instances (pentagon, triangle, hexagon, ...).
------------------------------------------------------------------------

Coherence-UP : UPArrow
Coherence-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 2. Capstone for HC1.
--
-- The Coherence-UP base lands. HC2-HC10 supply concrete instances:
-- Pentagon-UP, Triangle-UP, Hexagon-UP, Interchange-UP, AdjTriangle-UP,
-- 2EquivTriangle-UP, MacLane-UP, F2LinSymMon-UP.
------------------------------------------------------------------------
