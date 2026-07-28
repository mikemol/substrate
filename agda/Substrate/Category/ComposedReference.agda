------------------------------------------------------------------------
-- Substrate.Category.ComposedReference
--
-- AA-arc: unifies the codec's emission primitives — reference source
-- (Z-arc), action algebra (U-arc), basis interpretation (V-arc),
-- chamber binding (X-arc) — into ONE categorical primitive with
-- product-composable axes.
--
-- File-per-lemma decomposition:
--
--   ComposedReference.EmissionSource    — Rule / Recent tag
--   ComposedReference.V4                — local V₄ data
--   ComposedReference.ActionAlgebra     — V₄ residue + affine projection
--   ComposedReference.BasisLabel        — basis-binding tags
--   ComposedReference.Record            — the unified record type
--   ComposedReference.QuotOrbit         — rule-body-slice emission
--   ComposedReference.Z1BackrefOrbit    — LZ77-style backref
--   ComposedReference.Aa2ResidueBackref — backref + V₄ residue
--   ComposedReference.Aa6AffineBackref  — backref + phase shift
--   ComposedReference.IdentityEmission  — monoid identity
--   ComposedReference.MonoidLaws        — placeholder for composition laws
--
-- Stdlib audit: Data.Maybe → Substrate.Foundation.Maybe.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference where

open import Substrate.Category.ComposedReference.EmissionSource
open import Substrate.Category.ComposedReference.V4
open import Substrate.Category.ComposedReference.ActionAlgebra
open import Substrate.Category.ComposedReference.BasisLabel
open import Substrate.Category.ComposedReference.Record
open import Substrate.Category.ComposedReference.QuotOrbit
open import Substrate.Category.ComposedReference.Z1BackrefOrbit
open import Substrate.Category.ComposedReference.Aa2ResidueBackref
open import Substrate.Category.ComposedReference.Aa6AffineBackref
open import Substrate.Category.ComposedReference.IdentityEmission
open import Substrate.Category.ComposedReference.MonoidLaws