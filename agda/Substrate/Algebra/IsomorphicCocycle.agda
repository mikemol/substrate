------------------------------------------------------------------------
-- Substrate.Algebra.IsomorphicCocycle
--
-- Substrate-native IsomorphicCocycleStructure: the primary cocycle
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
open import Substrate.Algebra.Torsor using (IsTorsor)

------------------------------------------------------------------------
-- The substrate-native IsomorphicCocycleStructure record.
------------------------------------------------------------------------

record IsomorphicCocycleStructure : Set₁ where      -- ⟦shape:f0833aa8 Invariant,GaugeCarrier,Gauge⟧
  field
    Invariant    : Set
    -- Carrier of the gauge group.
    GaugeCarrier : Set
    Gauge        : Group GaugeCarrier
    Fiber        : Invariant → Set
    fiber-torsor : (i : Invariant) → IsTorsor Gauge (Fiber i)

  -- Total operational space = Σ Invariant Fiber.
  TotalSpace : Set
  TotalSpace = Σ Invariant Fiber

open IsomorphicCocycleStructure public
