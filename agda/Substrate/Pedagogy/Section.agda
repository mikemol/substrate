------------------------------------------------------------------------
-- Substrate.Pedagogy.Section
--
-- E2 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- The Section record: a self-describing pedagogical unit bundling
-- a title (TextSymbol) with a body (Word of MarkdownTokens) and
-- a SectionKind classifier.
--
-- Per [[feedback-prefer-coxeter-backed]]: body uses
-- Substrate.Groups.Coxeter.Word, not Data.List.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.Section where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Pedagogy.MarkdownToken using (MarkdownToken; TextSymbol)

------------------------------------------------------------------------
-- 1. SectionKind: classifies what a section is about.
--
-- Useful for downstream tools that want to filter / reorganise
-- sections by type.
------------------------------------------------------------------------

data SectionKind : Set where
  witness-section     : SectionKind
  rosetta-section     : SectionKind
  arc-summary-section : SectionKind
  index-section       : SectionKind
  free-form-section   : SectionKind

------------------------------------------------------------------------
-- 2. The Section record.
--
-- title : the heading symbol
-- body  : a Word of MarkdownTokens (the rendered content)
-- kind  : classification
------------------------------------------------------------------------

record Section : Set where      -- ⟦shape:940c0ab1 title,body,kind⟧
  constructor mkSection
  field
    title : TextSymbol
    body  : Word MarkdownToken
    kind  : SectionKind

open Section public

------------------------------------------------------------------------
-- 3. Empty-body section constructor (just a heading).
------------------------------------------------------------------------

empty-section : TextSymbol → SectionKind → Section
empty-section t k = mkSection t [] k

------------------------------------------------------------------------
-- 4. Capstone for E2.
--
-- Section record defined; SectionKind classifies. E3 bundles
-- multiple Sections into a PageBundle.
------------------------------------------------------------------------
