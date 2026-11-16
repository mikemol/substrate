------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.WHTCore
--
-- Defines: WHTCore, wht-core
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.WHTCore where




------------------------------------------------------------------------
-- The invariant: the WHT core, the architecturally-meaningful
-- structure shared by all 8 puncturings.
--
-- Singleton type — one inhabitant — since CY-4 has a single orbit.
-- Naming it `WHTCore` rather than ⊤ keeps the catalog's semantic
-- vocabulary visible at the type level.
------------------------------------------------------------------------

data WHTCore : Set where
  wht-core : WHTCore
