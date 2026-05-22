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

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.RosettaTable using (pair-entry)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)

open import Substrate.Pedagogy.MarkdownToken using (txt-rosetta-table)
open import Substrate.Pedagogy.Section using (Section)
open import Substrate.Pedagogy.PageBundle using (PageBundle; mkPage)
open import Substrate.Pedagogy.RosettaToSection using (rosetta→section)

------------------------------------------------------------------------
-- 1. Row builder: 6 Rosetta sections for one focal witness paired
-- with all six.
------------------------------------------------------------------------

rosetta-row : LanguageWitness → Word Section
rosetta-row L =
  rosetta→section (pair-entry L lojban-witness)   ∷
  rosetta→section (pair-entry L tokipona-witness) ∷
  rosetta→section (pair-entry L solresol-witness) ∷
  rosetta→section (pair-entry L kelen-witness)    ∷
  rosetta→section (pair-entry L lambda-witness)   ∷
  rosetta→section (pair-entry L lie-witness)      ∷
  []

------------------------------------------------------------------------
-- 2. The full 36-entry Rosetta cross-table.
--
-- Six rows × six columns = 36 sections, concatenated in row order.
------------------------------------------------------------------------

rosetta-full-table : Word Section
rosetta-full-table =
  rosetta-row lojban-witness   ++
  rosetta-row tokipona-witness ++
  rosetta-row solresol-witness ++
  rosetta-row kelen-witness    ++
  rosetta-row lambda-witness   ++
  rosetta-row lie-witness

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
