------------------------------------------------------------------------
-- Substrate.Algebra.IsomorphicCocycle
--
-- Substrate-native IsomorphicCocycleStructureᴳ: the primary cocycle
-- abstraction (per Substrate.Cocycle's narrative) built over
-- substrate-native Group + Torsor + Action.
--
-- The "base" type is DERIVED: Σ Invariant Fiber, with each Fiber a
-- G-torsor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.IsomorphicCocycle where

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.Torsor using (IsTorsorᴳ)

------------------------------------------------------------------------
-- The substrate-native IsomorphicCocycleStructureᴳ record.
------------------------------------------------------------------------

record IsomorphicCocycleStructureᴳ : Set₁ where      -- ⟦shape:157a673b Invariant,GaugeCarrier,Gauge⟧
  field
    Invariant    : Set
    -- Carrier of the gauge group.
    GaugeCarrier : Set
    Gauge        : Group GaugeCarrier
    Fiber        : Invariant → Set
    fiber-torsor : (i : Invariant) → IsTorsorᴳ Gauge (Fiber i)

  -- Total operational space = Σ Invariant Fiber.
  TotalSpace : Set
  TotalSpace = Σ Invariant Fiber

open IsomorphicCocycleStructureᴳ public
