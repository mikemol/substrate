------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.CY5
--
-- The CY-5 V₄-signature cocycle as an `IsomorphicCocycleStructure`
-- (catalog rule 11 strong):
--   * Invariant    = OrbitKey  (6 elements)
--   * Gauge        = V₄        (as a setoid)
--   * Fiber        = const V₄  (4 elements per orbit)
--   * fiber-torsor : every fiber is a V₄-torsor.
--
-- There are 6 × 4 = 24 elements in TotalSpace = Σ OrbitKey Fiber —
-- the 24 "signatures" derived as (orbit_key, v4_position) pairs.
-- Neither a primitive Signature record nor a canonical-relative
-- coordinate is expressible in this formulation; the catalog's
-- CY-5 Type-D rigidification (lex-min in v4_delta) is structurally
-- absent.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.CY5 where

open import Substrate.Cocycle using (IsomorphicCocycleStructure)
open import Substrate.Groups.V4 using (V₄)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Cocycles.V4Signature.OrbitKey.Type  using (OrbitKey)
open import Substrate.Cocycles.V4Signature.V4GroupSetoid  using (V₄-Group-Setoid)
open import Substrate.Cocycles.V4Signature.Fiber          using (Fiber; fiber-torsor)

-- ⟡set1-paydown: ICS carrier/family fields are now module params — they move into the type
-- annotation and leave the record literal.
CY5-V4Signature : IsomorphicCocycleStructure OrbitKey V₄ _≡_ V₄-Group-Setoid Fiber
CY5-V4Signature = record
  { fiber-torsor = fiber-torsor
  }
