{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ShapeRegistryEntry — ⟡shape-registry-entry: cons
-- shape-backed (FoldRegistry, 172) onto the registry, the substrate's downstream cons
-- idiom (verdict-registry = bias-coeq-backed ∷ registry; mu-registry, 171; count-registry,
-- 178). shape-backed = the shape/CF fold registered as a BackedUP; consing it certifies it
-- as a registered solver by TYPING — the shape read joins μ, ν, the deferred list, count.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ShapeRegistryEntry where

open import Substrate.Foundation.List using (List; _∷_)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP)
open import Substrate.Category.UniversalProperty.Registry using (registry)
open import Substrate.Category.UniversalProperty.FoldRegistry using (shape-backed)

-- REGISTERED: consed onto the seed registry (compiling = the registration).
shape-registry : List BackedUP
shape-registry = shape-backed ∷ registry

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the shape fold registered): shape-backed (the CF/cost
-- fold as a BackedUP, 172) joins the registry by the SAME downstream cons idiom as
-- mu-registry (171), count-registry (178), and the deferred list (172-175). Registration
-- IS the proof (the fold's existence + non-vacuity) re-presented as a compiling entry;
-- the shape read — the quotient sequence, the cost — is now a registered solver alongside
-- μ, ν, free monoid, Z₂, units, F₂-module, limit, count. No either/or: the cons is the
-- one idiom, uniform across every registered solver.
------------------------------------------------------------------------
