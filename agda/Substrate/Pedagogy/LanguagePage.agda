------------------------------------------------------------------------
-- Substrate.Pedagogy.LanguagePage
--
-- E7 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Assemble a PageBundle for a specific language: title + the
-- witness's own section + cross-references to its sibling cells via
-- RosettaEntries to each other witness.
--
-- The focal language is a `Lang` value now (⟡rc-lang) — the Set₀
-- object-alphabet enumeration; the underlying LanguageWitness is
-- reached via `witness-of` where name/class projections are needed.
-- The witness collection is still enumerated inline (six named
-- Lang constants) rather than folded over a Word Lang.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.LanguagePage where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

open import Substrate.Category.FreeOverBasis
  using (name)
open import Substrate.Linguistic.Roster
  using (Lang; witness-of; lojban; tokipona; solresol; kelen; lambda-lang; lie-lang)
open import Substrate.Linguistic.RosettaTable
  using (RosettaEntry; pair-entry)

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
-- Witness collection inlined (six named Lang constants).
------------------------------------------------------------------------

rosetta-sections-for : Lang → Word Section
rosetta-sections-for L =
  rosetta→section (pair-entry L lojban)      ∷
  rosetta→section (pair-entry L tokipona)    ∷
  rosetta→section (pair-entry L solresol)    ∷
  rosetta→section (pair-entry L kelen)       ∷
  rosetta→section (pair-entry L lambda-lang) ∷
  rosetta→section (pair-entry L lie-lang)    ∷
  []

------------------------------------------------------------------------
-- 2. Per-language section bundle.
--
-- The focal witness's own section + 6 rosetta-sections (one per
-- pair with each cell, including the self-diagonal).
------------------------------------------------------------------------

language-sections : Lang → Word Section
language-sections L =
  witness→section L ∷ rosetta-sections-for L

------------------------------------------------------------------------
-- 3. The language page assembler.
------------------------------------------------------------------------

language-page : Lang → PageBundle
language-page L = mkPage (name→text (name (witness-of L))) (language-sections L)

------------------------------------------------------------------------
-- 4. Capstone for E7.
--
-- Per-language pages assembled. E8 builds the cross-language
-- Rosetta page; E9 the Index; E10 the capstone.
------------------------------------------------------------------------
