------------------------------------------------------------------------
-- Substrate.Pedagogy.RosettaToSection
--
-- E5 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Generate a Section displaying a RosettaEntry's cross-language
-- alignment: the two witnesses + their respective classes + the
-- same-class? distinction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.RosettaToSection where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; name; class)
open import Substrate.Linguistic.RosettaTable
  using (RosettaEntry)
open RosettaEntry public
open import Substrate.Linguistic.Classification
  using (_⊎-OR_; here; there)
open import Substrate.Pedagogy.MarkdownToken
  using (MarkdownToken; TextSymbol;
         txt-rosetta-table; txt-name; txt-class; txt-vs;
         txt-same-class; txt-different-class;
         heading-3; paragraph; inline;
         table-row; table-cell; table-header;
         blank-line)
open import Substrate.Pedagogy.Section
  using (Section; mkSection; SectionKind; rosetta-section)
open import Substrate.Pedagogy.WitnessToSection
  using (name→text; class→text)

------------------------------------------------------------------------
-- 1. Decode the same-class? witness to a TextSymbol verdict.
------------------------------------------------------------------------

verdict→text :
  ∀ {A B : Set} → A ⊎-OR B → TextSymbol
verdict→text (here _)  = txt-same-class
verdict→text (there _) = txt-different-class

------------------------------------------------------------------------
-- 2. RosettaEntry → Section.
--
-- Produces a section with a table comparing the two witnesses
-- on name and class, plus the same-class verdict.
------------------------------------------------------------------------

rosetta→section : RosettaEntry → Section
rosetta→section r = mkSection
  txt-rosetta-table
  body
  rosetta-section
  where
    L = left r
    R = right r
    body : Word MarkdownToken
    body =
      heading-3 txt-rosetta-table ∷
      table-row ∷
        table-cell (name→text (name L)) ∷
        table-cell txt-vs ∷
        table-cell (name→text (name R)) ∷
      table-row ∷
        table-cell (class→text (class L)) ∷
        table-cell (verdict→text (same-class r)) ∷
        table-cell (class→text (class R)) ∷
      blank-line ∷
      []

------------------------------------------------------------------------
-- 3. Capstone for E5.
--
-- Rosetta → Section generator landed. E6 builds Arc → Section;
-- E7-E8 assemble PageBundles.
------------------------------------------------------------------------
