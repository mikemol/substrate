------------------------------------------------------------------------
-- Substrate.WitnessTower.UniquenessBridge
--
-- A DISCOVERABILITY / CO-APEX bridge for the substrate's recurring
-- UNIQUENESS PRINCIPLE: "the canonical map is the UNIQUE structure-
-- respecting homomorphism out of the free / initial object." This shape
-- appears under several unlinked names; the author repeatedly proposed
-- "unbuilt" uniqueness facts that were already present as one of these.
-- Search "unique fold" / "initiality" / "unique hom" / "self-parse" /
-- "inside-unique" / "fold-unique" and land here.
--
-- The genuine instances co-apexed (same shape, distinct carriers):
--   (SPPF)  Algebra.Semiring.SPPFUP.inside-unique
--       `inside S v` is the UNIQUE semiring hom SPPF G → A agreeing with v
--       on generators and respecting one/⊗/⊕. [free semiring term algebra]
--   (TOWER) WitnessTower.Wedge.OrientationRigInitial.foldR-initial
--       = fold-unique (alg R): `fold` is THE UNIQUE ◂-algebra map out of
--       LehmerPath (which carries the rig structure for free). [initial
--       rig-carrying algebra]
--
-- These are the SAME universal-property shape at two sites — free-object
-- uniqueness (SPPF) and initial-algebra uniqueness (tower). My
-- Metacircular.agda is the SELF-APPLICATION of the SPPF leg (G := R, the
-- grammar's own rules), so its "self-parse is the unique fold" telos is
-- inside-unique instantiated — NOT a separate grounding to dedup, but this
-- shape self-applied. That answers ⟡metacircular-dedup by IDENTIFICATION.
--
-- HONEST BOUNDARY (not forced into this bridge): the SKI
-- ExtrudeSelfInterpUniversal.carries-confluence is a RELATED but DISTINCT
-- flavor — it CARRIES confluence from the system's CR (carries-confluence
-- cr = cr), a passthrough, not a free/initial-object uniqueness. It belongs
-- to the same telos family (self-interpretation) but is not an instance of
-- THIS uniqueness shape. Recorded here as a cross-reference, not co-apexed
-- by a false equality. (Its own closure is ⟡ski-cr-port.)
--
-- This file imports both genuine instances so the edge is in the import
-- graph (compaction-safe), and re-exports them under searchable names.
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.UniquenessBridge where

open import Substrate.Foundation.Eq using (_≡_)

-- (SPPF) free-semiring-term uniqueness.
open import Substrate.Algebra.Semiring.SPPF using (SPPF; inside)
open import Substrate.Algebra.Semiring.SPPFUP using (inside-unique)

-- (TOWER) initial-rig-algebra uniqueness.
open import Substrate.WitnessTower.Wedge.OrientationRigInitial
  using (foldR; foldR-initial)

------------------------------------------------------------------------
-- Searchable re-exports. Both are "the canonical map is unique among
-- structure-respecting maps out of the free/initial object". Importing +
-- naming them here is the co-apex: one place records that SPPF free-object
-- uniqueness and tower initial-algebra uniqueness are the SAME shape.
------------------------------------------------------------------------

-- SPPF leg: the unique semiring homomorphism out of the free term algebra.
free-object-uniqueness = inside-unique

-- Tower leg: the unique ◂-algebra map out of the initial LehmerPath.
initial-algebra-uniqueness = foldR-initial
