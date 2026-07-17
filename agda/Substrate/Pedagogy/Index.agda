------------------------------------------------------------------------
-- Substrate.Pedagogy.Index
--
-- E9 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- The top-level Index PageBundle: catalogue of all language
-- witnesses + arc summaries + Rosetta-table reference. The
-- substrate's "table of contents" for the pedagogical surface.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.Index where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

open import Substrate.Linguistic.Roster
  using (Lang; lojban; tokipona; solresol; kelen; lambda-lang; lie-lang)

open import Substrate.Pedagogy.MarkdownToken
  using (TextSymbol;
         txt-index; txt-classification; txt-arc-summary;
         txt-bicategorical-lift; txt-yoneda-lemma;
         txt-rosetta-table)
open import Substrate.Pedagogy.Section using (Section; mkSection; SectionKind; index-section; arc-summary-section)
open import Substrate.Pedagogy.PageBundle using (PageBundle; mkPage)
open import Substrate.Pedagogy.WitnessToSection using (witness→section)
open import Substrate.Pedagogy.ArcToSection
  using (ArcDescription; mkArcDescription; arc→section)

------------------------------------------------------------------------
-- 1. Per-arc descriptions.
--
-- A short list of the major arcs landed so far. Slice counts
-- approximate (some closure / sprint arcs had varying counts).
------------------------------------------------------------------------

classification-arc : ArcDescription
classification-arc = mkArcDescription
  txt-classification 10 txt-arc-summary

yoneda-arc : ArcDescription
yoneda-arc = mkArcDescription
  txt-yoneda-lemma 10 txt-arc-summary

bicategorical-arc : ArcDescription
bicategorical-arc = mkArcDescription
  txt-bicategorical-lift 10 txt-arc-summary

------------------------------------------------------------------------
-- 2. The Index sections.
--
-- Index → witness sections (one per language) + arc summaries
-- (one per major arc).
------------------------------------------------------------------------

index-sections : Word Section
index-sections =
  witness→section lojban      ∷
  witness→section tokipona    ∷
  witness→section solresol    ∷
  witness→section kelen       ∷
  witness→section lambda-lang ∷
  witness→section lie-lang    ∷
  arc→section classification-arc   ∷
  arc→section yoneda-arc           ∷
  arc→section bicategorical-arc    ∷
  []

------------------------------------------------------------------------
-- 3. The Index PageBundle.
------------------------------------------------------------------------

index-page : PageBundle
index-page = mkPage txt-index index-sections

------------------------------------------------------------------------
-- 4. Capstone for E9.
--
-- The Index is the entry point for an external renderer. E10
-- caps the arc with re-exports and a worked Lojban-page example.
------------------------------------------------------------------------
