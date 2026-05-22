------------------------------------------------------------------------
-- Substrate.Pedagogy.PageBundle
--
-- E3 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- PageBundle: a Word of Sections plus a page-level title symbol.
-- The unit of pedagogical output that external markdown renderers
-- consume.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.PageBundle where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Pedagogy.MarkdownToken using (TextSymbol)
open import Substrate.Pedagogy.Section using (Section)

------------------------------------------------------------------------
-- 1. The PageBundle record.
--
-- page-title : the page's overall heading
-- sections   : Word of Sections (in display order)
------------------------------------------------------------------------

record PageBundle : Set where
  constructor mkPage
  field
    page-title : TextSymbol
    sections   : Word Section

open PageBundle public

------------------------------------------------------------------------
-- 2. Empty page constructor.
------------------------------------------------------------------------

empty-page : TextSymbol → PageBundle
empty-page t = mkPage t []

------------------------------------------------------------------------
-- 3. Page concatenation.
--
-- Combine two pages by concatenating their sections (the second
-- page's title is dropped; the first's is kept).
------------------------------------------------------------------------

append-page-sections : PageBundle → PageBundle → PageBundle
append-page-sections p₁ p₂ = mkPage
  (page-title p₁)
  (_++_ (sections p₁) (sections p₂))

------------------------------------------------------------------------
-- 4. Capstone for E3.
--
-- PageBundle defined; E4-E6 build per-record generators that
-- produce Sections; E7-E8 assemble PageBundles; E9 creates the
-- top-level Index.
------------------------------------------------------------------------
