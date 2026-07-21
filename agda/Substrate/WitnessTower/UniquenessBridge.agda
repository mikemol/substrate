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
-- ⚑ THE DUAL HALF — NOT A THIRD INSTANCE (⟡sppf-quotient-coapex). The
-- interner's effectivity (Shape.Double.InternedEffectivity.corr⇔addr: equal
-- shapes ⟺ equal addresses on a NoDupᴿ heap) is recorded here, but
-- it is EXPRESSLY NOT a third instance of the uniqueness shape above, and it
-- is deliberately NOT named `*-uniqueness`. The two legs above are about maps
-- OUT of a free/initial object (what a homomorphism is DETERMINED by); the
-- interner leg is about which inputs get IDENTIFIED (that the address map's
-- kernel is exactly the intended relation). It is therefore NOT a third
-- `*-uniqueness`, and naming it one would be the false equality.
--
-- ⚑ BUT THEY ARE NOT UNRELATED — THE UNIFIER EXISTS AND IS NAMED. An earlier
-- draft of this paragraph said "no term unifies them and none is claimed."
-- That was wrong. Determination and identification are the μ and ν halves of
-- ONE adjoint structure:
--   * `R.Trace.Final` (:16-21) — initial algebra (constructors, induction,
--     Free⊣Forgetful) and terminal coalgebra (observations, coinduction) "are
--     one adjoint structure hinged by Lawvere; bisimilarity `_~_` is EQUALITY"
--     in the terminal coalgebra.
--   * `WitnessTower.CofreeDual` names both halves in one place —
--     `cata-uniqueness = eea-fold-unique` (μ, `≡`) and
--     `cofree-uniqueness = ana-unique` (ν, `~`), over the same functor.
--   * `Algebra.Wedge.NuShapeIso` closes it for THIS leg: the finite
--     shape-projection (`Wedge.Shape.shape`, a List) and the infinite one (the
--     RealTrace stream) are the SAME projection at two grades, and its
--     canonicity `shape-is-canonical` IS `ana-unique` applied to the quotient
--     coalgebra.
-- Since `Corr t₁ t₂ = shape t₁ ≡ shape t₂` is precisely the KERNEL of that
-- finite shape-projection, `quotient-effectivity` below is the ν-side reading
-- at finite grade, and the two legs above are its μ-side. The interner leg is
-- carried into that pairing in `CofreeDual`; this file records the naming
-- boundary (why it is not a `*-uniqueness`), not an absence of connection.
--
-- HONEST BOUNDARY (not forced into this bridge): the SKI
-- ExtrudeSelfInterpUniversal.carries-confluence is a RELATED but DISTINCT
-- flavor — it CARRIES confluence from the system's CR (carries-confluence
-- cr = cr), a passthrough, not a free/initial-object uniqueness. It belongs
-- to the same telos family (self-interpretation) but is not an instance of
-- THIS uniqueness shape. Recorded here as a cross-reference, not co-apexed
-- by a false equality. (Its own closure is ⟡ski-cr-port.)
--
-- This file imports all three legs so the edges are in the import graph
-- (compaction-safe), and re-exports them under searchable names. Note the
-- import list is where the SPPF side and the interner side finally meet in
-- the dependency graph — previously they were tied only in prose, in two
-- files that did not import each other.
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

-- (INTERNER) the DUAL half — quotient effectivity, NOT a uniqueness instance.
open import Substrate.Algebra.Wedge.Shape.Double.InternedEffectivity
  using (corr⇔addr)

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

-- Interner leg (DUAL half, not a third instance): the address map identifies
-- exactly the corresponding traces — no splitting (⟹, needs NoDupᴿ), no
-- collapse (⟸). Determination's counterpart, not another determination.
quotient-effectivity = corr⇔addr
