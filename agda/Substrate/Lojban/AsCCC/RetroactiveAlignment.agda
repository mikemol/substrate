------------------------------------------------------------------------
-- Substrate.Lojban.AsCCC.RetroactiveAlignment
--
-- D6 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Retroactive alignment: the Lojban L10 AsCCC.Bridge module's
-- "shared parent extraction deferred" status (line 30 of
-- Substrate.Lojban.AsCCC, written before the Classification arc)
-- is superseded — the parent primitive Substrate.Category.FreeOverBasis
-- now exists, and the Lojban Bridge is structurally an instance of
-- it via the lojban-witness from C2.
--
-- This slice provides:
--   1. Real Agda content: an alignment lemma showing the AsCCC
--      Bridge's `program` function agrees with the FreeOverBasis
--      η-coherence at single-symbol words (the basis-action).
--   2. A note connecting the Bridge module's underlying
--      construction to the lojban-witness FreeOverBasis record.
--
-- Per [[feedback-comments-dont-overclaim]]: the AsCCC file's
-- original prose is preserved (the slice doesn't edit it). The
-- alignment is supplied as fresh Agda content; future arcs can
-- choose to rewrite the AsCCC prose if needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsCCC.RetroactiveAlignment where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Coxeter.Word using ([])
open import Substrate.Lojban.Gismu using (Gismu)
open import Substrate.Lojban.Word Gismu using (LojbanWord; single)
open import Substrate.Lojban.AsCCC using (module Bridge)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness; lojban-free-structure)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; LanguageWitness; η;
         WitnessName; Lojban;
         FreeConstructionClass; Free-monoid;
         name; class)

------------------------------------------------------------------------
-- 1. η of the Lojban FreeOverBasis IS the `single` lift.
--
-- Connects the Classification arc's basis embedding to the L2
-- Word module's basis embedding.
------------------------------------------------------------------------

lojban-η-is-single :
  (g : Gismu) → η lojban-free-structure g ≡ single g
lojban-η-is-single _ = refl

------------------------------------------------------------------------
-- 2. The AsCCC Bridge's `program` agrees with the basis-action on
-- single-symbol words.
--
-- For any State + per-gismu operation op, the Bridge program
-- applied to a single-gismu word IS the basis operation. This is
-- the FreeOverBasis η-coherence at the program layer.
--
-- (The substantive program-execute-agree from L10 is the n-gismu
-- generalisation; this is the n=1 specialisation that ties
-- directly to the FreeOverBasis structure's η field.)
------------------------------------------------------------------------

program-on-single-is-op :
  (State : Set) (op : Gismu → State → State) →
  (g : Gismu) (s : State) →
  Bridge.program State op (single g) s ≡ op g s
program-on-single-is-op _ _ _ _ = refl

------------------------------------------------------------------------
-- 3. Witness identity.
--
-- The lojban-witness's classification, name, and η-map are exactly
-- those expected of the Free-monoid cell with Lojban as the
-- witness.
------------------------------------------------------------------------

lojban-witness-class : class lojban-witness ≡ Free-monoid
lojban-witness-class = refl

lojban-witness-name : name lojban-witness ≡ Lojban
lojban-witness-name = refl

------------------------------------------------------------------------
-- 4. Capstone.
--
-- The "shared parent extraction is deferred" note from L10 AsCCC
-- is SUPERSEDED. The parent primitive (FreeOverBasis) exists;
-- the Lojban Bridge is structurally an instance via lojban-witness;
-- the basis-action lifts through the L8 free-monoid universal
-- property (Substrate.Lojban.WordAlgebra) which the parent
-- primitive abstractly named.
--
-- D7 provides the sister retroactive alignment on the Toki Pona
-- side; D8 unifies both into a single substrate-internal record.
------------------------------------------------------------------------
