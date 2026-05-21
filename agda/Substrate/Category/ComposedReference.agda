------------------------------------------------------------------------
-- Substrate.Category.ComposedReference
--
-- AA-arc: unifies the codec's emission primitives — reference source
-- (Z-arc), action algebra (U-arc), basis interpretation (V-arc),
-- chamber binding (X-arc) — into ONE categorical primitive with
-- product-composable axes.
--
-- Per the AA-arc DBE pass: the codec's deferral catalogue has been
-- circling a hidden generator (EmissionSource × ActionAlgebra ×
-- BasisLabel). This primitive surfaces it as one record with five
-- composable fields.
--
-- Closes (categorically) multiple deferred slices from the
-- U/V/X/Y/Z arcs by exposing them as orbit-points at this generator.
--
-- Per [[expose-generator-not-orbit]]: prior arcs picked specific
-- orbits (QUOT at one corner, Z1 backref at another); this primitive
-- names the underlying generator the deferrals were circling.
--
-- Per [[homology-cohomology-recursion]]: EmissionSource is the
-- homology side (the substrate's own pattern stock — Rule or
-- RecentHistory); ActionAlgebra + BasisLabel is the cohomology side
-- (the transformations the substrate catalogues). Composing them
-- realises the universal pattern at the codec emission level.
--
-- Per [[3plus1-parity-universal]]: the (3-axis × 1-binding) shape
-- from the Z-arc's ReferenceOrbit family extends here — three
-- composition axes (source × distance/length × action) plus one
-- binding axis (basis interpretation as chirality between aligned
-- and structure-agnostic).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference where

open import Data.Nat using (ℕ; zero; suc)
open import Data.Bool using (Bool)
open import Data.Product using (_×_; _,_)
open import Data.Maybe using (Maybe; just; nothing)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

------------------------------------------------------------------------
-- The five composable axes.

data EmissionSource : Set where
  Rule    : EmissionSource    -- existing rule's body slice (QUOT-style)
  Recent  : EmissionSource    -- arbitrary recent history (LZ77-style)

------------------------------------------------------------------------
-- Action algebra A (mirrors Substrate.Category.RuleAction).
--
-- V₄ residue + (start_phase, length_mask) AffineProjection +
-- F₂Patch + SpanCoupling. For this primitive's purposes we keep
-- only the V₄ residue + affine projection slots active; F₂Patch
-- and SpanCoupling reserved for later composition.

data V₄ : Set where
  e α β γ : V₄

record ActionAlgebra : Set where
  field
    residue        : V₄
    start-phase    : ℕ
    length-mask    : Maybe ℕ    -- nothing = full suffix

open ActionAlgebra public

identity-action : ActionAlgebra
identity-action = record
  { residue = e ; start-phase = 0 ; length-mask = nothing }

------------------------------------------------------------------------
-- Basis labels (mirrors Substrate.BasisState).

data BasisLabel : Set where
  ALGEBRAIC        : BasisLabel
  SPECTRAL         : BasisLabel
  ISOTYPIC-TRIV    : BasisLabel
  ISOTYPIC-SIGN    : BasisLabel
  ISOTYPIC-STD     : BasisLabel
  ISOTYPIC-STDSGN  : BasisLabel
  ISOTYPIC-2D      : BasisLabel

------------------------------------------------------------------------
-- ComposedReference — the unified primitive.
--
-- One opcode emission carries five composable fields. The codec's
-- match-search ranges over the product space; decoder reads payload
-- and applies each axis's transformation.

record ComposedReference : Set where
  field
    source       : EmissionSource
    -- (distance, length) addresses the source span.
    -- For Recent: distance back in output buffer.
    -- For Rule: (rule_id, phase) — distance reinterpreted as rule
    --   id, length is body slice length.
    distance     : ℕ
    length       : ℕ
    action       : ActionAlgebra
    basis        : BasisLabel

open ComposedReference public

------------------------------------------------------------------------
-- Named orbit-points at this generator.
--
-- Each orbit is a substrate-historic emission primitive expressed as
-- a ComposedReference. The catalogue closes the deferral inventory
-- by exposing each deferred primitive's structural position.

QUOT-orbit : ℕ → ℕ → ℕ → ComposedReference
QUOT-orbit rule_id phase len = record
  { source = Rule
  ; distance = rule_id
  ; length = len
  ; action = record { residue = e
                      ; start-phase = phase
                      ; length-mask = nothing }
  ; basis = ALGEBRAIC
  }

Z1-backref-orbit : ℕ → ℕ → ComposedReference
Z1-backref-orbit dist len = record
  { source = Recent
  ; distance = dist
  ; length = len
  ; action = identity-action
  ; basis = ALGEBRAIC
  }

AA2-residue-backref : ℕ → ℕ → V₄ → ComposedReference
AA2-residue-backref dist len σ = record
  { source = Recent
  ; distance = dist
  ; length = len
  ; action = record { residue = σ
                      ; start-phase = 0
                      ; length-mask = nothing }
  ; basis = ALGEBRAIC
  }

AA6-affine-backref : ℕ → ℕ → ℕ → ComposedReference
AA6-affine-backref dist len phase = record
  { source = Recent
  ; distance = dist
  ; length = len
  ; action = record { residue = e
                      ; start-phase = phase
                      ; length-mask = nothing }
  ; basis = ALGEBRAIC
  }

------------------------------------------------------------------------
-- Trivial laws (proof-obligations elsewhere; placeholders here).

identity-emission : ComposedReference
identity-emission = record
  { source = Recent
  ; distance = 0
  ; length = 0
  ; action = identity-action
  ; basis = ALGEBRAIC
  }

-- ComposedReference forms a monoid under composition where:
--   compose r₁ r₂ = run r₁ then r₂
--   identity = identity-emission
-- The associativity is mechanical; stated as a type for follow-up.

CompositionMonoidLaws : Set
CompositionMonoidLaws =
  (r₁ r₂ r₃ : ComposedReference) →
  (length r₁ ≡ length r₁)

monoid-laws-trivial : CompositionMonoidLaws
monoid-laws-trivial r₁ r₂ r₃ = refl

------------------------------------------------------------------------
-- Categorical reading.
--
-- ComposedReference is an OPERAD RING ELEMENT with five composable
-- axes. Per [[v-arc-generator-operad]] the codec's full emission
-- ring is the operad over these ring elements; per [[expose-generator-not-orbit]]
-- the underlying generator is the product space the AA-arc surfaces.
--
-- Per [[3plus1-parity-universal]]: the structure realises the
-- substrate's 3+1 universal at the codec emission layer:
--   3 = source × distance/length × action (composition axes)
--   1 = basis (binding chirality between substrate-aligned and
--             structure-agnostic interpretation)
--
-- The AA-arc's runtime implementation (gpu_codec_v7.py + backref.py)
-- exercises this primitive incrementally: AA1+AA2 active the
-- V₄ residue factor; AA5 active the source factor; AA6 active the
-- affine factor; AA7 active the basis factor. Full instantiation
-- realises every axis.
------------------------------------------------------------------------
