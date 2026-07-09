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

-- ⟡set1-paydown: parameterize BOTH carriers (Invariant, GaugeCarrier), the gauge Group, AND the
-- Fiber family. Invariant/GaugeCarrier are Set-valued CARRIER fields and Fiber : Invariant → Set is
-- an indexed FAMILY — all three force Set₁. Moving them (and Gauge, which depends on GaugeCarrier)
-- to module parameters leaves only fiber-torsor as a Set-valued field, so the record lives in Set.
-- Consumers write `IsomorphicCocycleStructureᴳ Invariant GaugeCarrier Gauge Fiber`.
module _ (Invariant : Set)
         (GaugeCarrier : Set)
         (Gauge : Group GaugeCarrier)
         (Fiber : Invariant → Set) where
  record IsomorphicCocycleStructureᴳ : Set where      -- ⟦shape:157a673b Invariant,GaugeCarrier,Gauge⟧
    field
      fiber-torsor : (i : Invariant) → IsTorsorᴳ Gauge (Fiber i)

    -- Total operational space = Σ Invariant Fiber.
    TotalSpace : Set
    TotalSpace = Σ Invariant Fiber

open IsomorphicCocycleStructureᴳ public
