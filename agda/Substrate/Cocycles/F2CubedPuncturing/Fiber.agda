------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.Fiber
--
-- Defines: Fiber
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.Fiber where

open import Substrate.Groups.F2Cubed
open import Substrate.Cocycles.F2CubedPuncturing.WHTCore
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex



------------------------------------------------------------------------
-- The fiber over the unique invariant.
--
-- For CY-4 the orbit-decomposition is trivial (1 orbit), so the fiber
-- over `wht-core` is the entire PunctureIndex space.
------------------------------------------------------------------------

Fiber : WHTCore → Set
Fiber wht-core = PunctureIndex
