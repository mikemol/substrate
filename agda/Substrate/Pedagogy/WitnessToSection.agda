------------------------------------------------------------------------
-- Substrate.Pedagogy.WitnessToSection
--
-- E4 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Generate a Section describing a LanguageWitness: heading +
-- witness name + cell classification + universal-property tag.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.WitnessToSection where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeOverBasis
  using (WitnessName;
         FreeConstructionClass; name; class;
         Lojban; TokiPona; Solresol; Kelen; Lambda; LieFrag;
         Free-monoid; Free-F2-module; Free-cyclic;
         Free-relation; Free-CCC; Free-Lie; Free-other)
open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Pedagogy.MarkdownToken
  using (MarkdownToken; TextSymbol;
         txt-Lojban; txt-TokiPona; txt-Solresol; txt-Kelen;
         txt-Lambda; txt-LieFrag;
         txt-Free-monoid; txt-Free-F2-module; txt-Free-cyclic;
         txt-Free-relation; txt-Free-CCC; txt-Free-Lie;
         txt-Free-other;
         txt-witness-summary; txt-name; txt-class;
         txt-universal-property;
         heading-2; paragraph; list-item-start; list-item-text;
         table-row; table-cell; blank-line)
open import Substrate.Pedagogy.Section using (Section; mkSection; SectionKind; witness-section)

------------------------------------------------------------------------
-- 1. WitnessName → TextSymbol.
------------------------------------------------------------------------

name→text : WitnessName → TextSymbol
name→text Lojban   = txt-Lojban
name→text TokiPona = txt-TokiPona
name→text Solresol = txt-Solresol
name→text Kelen    = txt-Kelen
name→text Lambda   = txt-Lambda
name→text LieFrag  = txt-LieFrag

------------------------------------------------------------------------
-- 2. FreeConstructionClass → TextSymbol.
------------------------------------------------------------------------

class→text : FreeConstructionClass → TextSymbol
class→text Free-monoid    = txt-Free-monoid
class→text Free-F2-module = txt-Free-F2-module
class→text Free-cyclic    = txt-Free-cyclic
class→text Free-relation  = txt-Free-relation
class→text Free-CCC       = txt-Free-CCC
class→text Free-Lie       = txt-Free-Lie
class→text Free-other     = txt-Free-other

------------------------------------------------------------------------
-- 3. The Section generator.
--
-- Produces a Section with:
--   * Title : the witness's name (as TextSymbol)
--   * Body  : a paragraph identifying the cell, and a table
--             showing the (name, class) pair
------------------------------------------------------------------------

witness→section : Lang → Section
witness→section l = mkSection
  (name→text (name (witness-of l)))
  body
  witness-section
  where
    body : Word MarkdownToken
    body =
      heading-2 (name→text (name (witness-of l))) ∷
      paragraph txt-universal-property ∷
      table-row ∷
        table-cell txt-name ∷
        table-cell (name→text (name (witness-of l))) ∷
      table-row ∷
        table-cell txt-class ∷
        table-cell (class→text (class (witness-of l))) ∷
      blank-line ∷
      []

------------------------------------------------------------------------
-- 4. Capstone for E4.
--
-- Witness → Section generator landed. E5 builds Rosetta → Section;
-- E6 builds Arc → Section.
------------------------------------------------------------------------
