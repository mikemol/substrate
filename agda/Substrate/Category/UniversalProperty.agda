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

record UPArrow : Set₁ where
  field
    Source  : Set
    Target  : Set
    Witness : Source → Target → Set

open UPArrow public

------------------------------------------------------------------------
-- 2. The canonical alias: UniversalProperty = UPArrow.
--
-- Downstream callers continue to use the older name for narrative
-- continuity with the substrate's catalogue of UPs. Spec / Inst /
-- solves are exported as projection synonyms.
------------------------------------------------------------------------

UniversalProperty : Set₁
UniversalProperty = UPArrow

Spec : UPArrow → Set
Spec = Source

Inst : UPArrow → Set
Inst = Target

solves : (U : UPArrow) → Source U → Target U → Set
solves = Witness

------------------------------------------------------------------------
-- 3. The trivial UPArrow.
--
-- Source = Target = ⊤, Witness ≡ ⊤; the canonical terminal in
-- UPCategory (UP9).
------------------------------------------------------------------------

trivial-UP : UPArrow
trivial-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 4. Capstone for UP1.
--
-- UPArrow lands as a record-data object of Arr(Span). UP2 makes
-- UP-morphisms into commuting squares of UPArrows; UP4 supplies the
-- term-algebra; UP5 surfaces the arrow-of-arrow meta-level; UP6
-- exhibits the fixed-point canonical embedding.
------------------------------------------------------------------------
