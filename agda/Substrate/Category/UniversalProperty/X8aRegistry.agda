{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aRegistry — ⟡x8a-backed (registration): cons the
-- extruder onto the registry via the CANONICAL cons idiom (ADD 205: X ∷ registry, the
-- substrate's documented, deliberate extension mechanism — the non-vacuity proof stays local
-- to where the BackedUP is defined). x8a-registry registers the extruder as the THIRD solver
-- joining μ (MuBacked) and ν (NuBacked), certified by TYPING as a real, non-vacuous solver.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aRegistry where

open import Substrate.Foundation.List using (List; _∷_)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP)
open import Substrate.Category.UniversalProperty.Registry using (registry)
open import Substrate.Category.UniversalProperty.X8aBacked using (x8a-backed)

-- the extruder registered — the canonical cons (205), the third solver on the base seed.
x8a-registry : List BackedUP
x8a-registry = x8a-backed ∷ registry
