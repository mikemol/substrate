------------------------------------------------------------------------
-- Substrate.Pedagogy.RosettaPage
--
-- E8 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Assemble the full cross-language Rosetta-table PageBundle: all
-- 6×6 = 36 RosettaEntries rendered as Sections, organised in
-- row order (Lojban × everything, then TokiPona × everything, ...).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.RosettaPage where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)

open import Substrate.Linguistic.Roster
  using (Lang; lojban; tokipona; solresol; kelen; lambda-lang; lie-lang)
open import Substrate.Linguistic.RosettaTable using (pair-entry)

open import Substrate.Pedagogy.MarkdownToken using (txt-rosetta-table)
open import Substrate.Pedagogy.Section using (Section)
open import Substrate.Pedagogy.PageBundle using (PageBundle; mkPage)
open import Substrate.Pedagogy.RosettaToSection using (rosetta→section)

------------------------------------------------------------------------
-- 1. Row builder: 6 Rosetta sections for one focal witness paired
-- with all six.
------------------------------------------------------------------------

rosetta-row : Lang → Word Section
rosetta-row L =
  rosetta→section (pair-entry L lojban)      ∷
  rosetta→section (pair-entry L tokipona)    ∷
  rosetta→section (pair-entry L solresol)    ∷
  rosetta→section (pair-entry L kelen)       ∷
  rosetta→section (pair-entry L lambda-lang) ∷
  rosetta→section (pair-entry L lie-lang)    ∷
  []

------------------------------------------------------------------------
-- 2. The full 36-entry Rosetta cross-table.
--
-- Six rows × six columns = 36 sections, concatenated in row order.
------------------------------------------------------------------------

rosetta-full-table : Word Section
rosetta-full-table =
  rosetta-row lojban      ++
  rosetta-row tokipona    ++
  rosetta-row solresol    ++
  rosetta-row kelen       ++
  rosetta-row lambda-lang ++
  rosetta-row lie-lang

------------------------------------------------------------------------
-- 3. The Rosetta PageBundle.
------------------------------------------------------------------------

rosetta-page : PageBundle
rosetta-page = mkPage txt-rosetta-table rosetta-full-table

------------------------------------------------------------------------
-- 4. Capstone for E8.
--
-- The 36-entry Rosetta page assembled. E9 builds the top-level
-- Index; E10 the capstone.
------------------------------------------------------------------------
