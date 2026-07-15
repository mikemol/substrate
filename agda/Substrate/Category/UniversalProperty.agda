------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty
--
-- UP1 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Per the user's framing: "my favourite category is the category
-- that is an object in the category of arrow categories." A
-- UniversalProperty IS NATIVELY an arrow object — its three
-- components (source, target, proof-relevant witness) ARE the data
-- of an arrow in Span, the category of sets and spans.
--
-- This slice surfaces that structural reading:
--   UniversalProperty = UPArrow ⊆ Obj(Arr(Span))
--
-- The substrate's existing UP records (FreeOverBasis, Limit, Cone,
-- Adjunction, FreeBasisUniversal, ...) are all instances of UPArrow.
-- UP2 makes UP-morphisms commuting squares in Arr(Span). UP5-UP6
-- exhibit the arrow-of-arrow iteration + the fixed-point embedding.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty where

open import Substrate.Foundation.Unit using (⊤; tt)

------------------------------------------------------------------------
-- 1. UPArrow — the substrate's native presentation of a UP-as-arrow.
--
-- A UPArrow is an object of Arr(Span). Concretely:
--   * Source  : "Spec"        (what specification is being asked)
--   * Target  : "Inst"        (which inhabitant solves it)
--   * Witness : the proof-relevant span (Source ↛ Target)
--               = "the UP-witness relation"
--
-- Reading the Witness relation as a proof-relevant arrow makes
-- explicit that UniversalProperty is the data of a single arrow
-- in Arr(Span).
------------------------------------------------------------------------

-- ⟡UPArrow-dissolve C COMPLETE: the flat `record UPArrow : Set₁` (which fielded
-- Source/Target/Witness as Sets) is DELETED. Its whole consumer component migrated
-- to the carrier-parameterized UPArrowP below (telescope for quantifiers; field→index
-- for the object-of-arrows UPArrow²; carrier-families for object-storing records).

------------------------------------------------------------------------
-- 1a. UPArrowP — the CARRIER-PARAMETERIZED presentation (⟡UPArrow-dissolve).
--
-- The carriers are TYPE PARAMETERS, not fields, so the record lands in
-- Set₀ (it has no Set-valued field). A UPArrowP value carries no data —
-- all its content is in the params — so `mkUP` is the sole inhabitant and
-- the accessors read the params back. This is the Set₀ twin of UPArrow:
-- a term `x : UPArrowP S T W` is NOT Set₁-counted, whereas `x : UPArrow`
-- is. The object type moves out of a stored-value position (a field) into
-- an index/family position (the params) — the UPMorphism transform
-- (Morphism.agda already lands in Set₀ despite indexing by Set₁ UPArrow).
------------------------------------------------------------------------

record UPArrowP (Source : Set) (Target : Set)
                (Witness : Source → Target → Set) : Set where
  constructor mkUP

-- Accessor SHIMS: read the carriers off the type params, so migrated
-- consumers keep projection-style access `SourceP U` / `TargetP U` /
-- `WitnessP U` over a bound `{U : UPArrowP S T W}`.
SourceP : {S T : Set} {W : S → T → Set} → UPArrowP S T W → Set
SourceP {S = S} _ = S

TargetP : {S T : Set} {W : S → T → Set} → UPArrowP S T W → Set
TargetP {T = T} _ = T

WitnessP : {S T : Set} {W : S → T → Set}
           (U : UPArrowP S T W) → SourceP U → TargetP U → Set
WitnessP {W = W} _ = W


------------------------------------------------------------------------
-- 2. The trivial object.
------------------------------------------------------------------------

-- ⟡UPArrow-dissolve: the trivial Set₀ object (used by the re-indexed
-- Vacuity/Recognized leaf-cluster). Coexists with trivial-UP (which still
-- bridges the topos stack via Terminal) until the record is retired.
trivial-UPP : UPArrowP ⊤ ⊤ (λ _ _ → ⊤)
trivial-UPP = mkUP

------------------------------------------------------------------------
-- 4. Capstone for UP1.
--
-- UPArrow lands as a record-data object of Arr(Span). UP2 makes
-- UP-morphisms into commuting squares of UPArrows; UP4 supplies the
-- term-algebra; UP5 surfaces the arrow-of-arrow meta-level; UP6
-- exhibits the fixed-point canonical embedding.
------------------------------------------------------------------------
