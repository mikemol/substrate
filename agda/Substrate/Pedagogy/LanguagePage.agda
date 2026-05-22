------------------------------------------------------------------------
-- Substrate.Pedagogy.LanguagePage
--
-- E7 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Assemble a PageBundle for a specific LanguageWitness: title +
-- the witness's own section + cross-references to its sibling
-- cells via RosettaEntries to each other witness.
--
-- Note: LanguageWitness lives at Set₁; substrate Coxeter Word
-- requires Set; so the witness collection is enumerated inline
-- rather than processed via a Word LanguageWitness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.LanguagePage where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; name)
open import Substrate.Linguistic.RosettaTable
  using (RosettaEntry; pair-entry)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)

open import Substrate.Pedagogy.MarkdownToken
  using (TextSymbol; txt-language-page)
open import Substrate.Pedagogy.Section using (Section)
open import Substrate.Pedagogy.PageBundle using (PageBundle; mkPage)
open import Substrate.Pedagogy.WitnessToSection
  using (witness→section; name→text)
open import Substrate.Pedagogy.RosettaToSection
  using (rosetta→section)

------------------------------------------------------------------------
-- 1. Rosetta-sections for a focal witness paired with all six.
--
-- Witness collection inlined (since LanguageWitness : Set₁).
------------------------------------------------------------------------

rosetta-sections-for : LanguageWitness → Word Section
rosetta-sections-for L =
  rosetta→section (pair-entry L lojban-witness)   ∷
  rosetta→section (pair-entry L tokipona-witness) ∷
  rosetta→section (pair-entry L solresol-witness) ∷
  rosetta→section (pair-entry L kelen-witness)    ∷
  rosetta→section (pair-entry L lambda-witness)   ∷
  rosetta→section (pair-entry L lie-witness)      ∷
  []

------------------------------------------------------------------------
-- 2. Per-language section bundle.
--
-- The focal witness's own section + 6 rosetta-sections (one per
-- pair with each cell, including the self-diagonal).
------------------------------------------------------------------------

language-sections : LanguageWitness → Word Section
language-sections L =
  witness→section L ∷ rosetta-sections-for L

------------------------------------------------------------------------
-- 3. The language page assembler.
------------------------------------------------------------------------

language-page : LanguageWitness → PageBundle
language-page L = mkPage (name→text (name L)) (language-sections L)

------------------------------------------------------------------------
-- 4. Capstone for E7.
--
-- Per-language pages assembled. E8 builds the cross-language
-- Rosetta page; E9 the Index; E10 the capstone.
------------------------------------------------------------------------
