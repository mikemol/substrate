------------------------------------------------------------------------
-- Substrate.Pedagogy.MarkdownToken
--
-- E1 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Substrate-native enum of markdown atoms + a TextSymbol enum
-- of pre-known text entries that an external markdown renderer
-- maps to concrete strings.
--
-- Per [[feedback-minimize-stdlib-deps]]-strengthened: avoids
-- Data.String entirely. Prose content is symbolic (enumerated);
-- the external renderer handles string materialisation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.MarkdownToken where

------------------------------------------------------------------------
-- 1. TextSymbol: pre-known text entries.
--
-- The external markdown renderer has a lookup table mapping each
-- TextSymbol to a concrete string. New text entries are added by
-- extending this enum.
------------------------------------------------------------------------

data TextSymbol : Set where
  -- Witness names (one per language)
  txt-Lojban       : TextSymbol
  txt-TokiPona     : TextSymbol
  txt-Solresol     : TextSymbol
  txt-Kelen        : TextSymbol
  txt-Lambda       : TextSymbol
  txt-LieFrag      : TextSymbol
  -- Free-construction-class names
  txt-Free-monoid    : TextSymbol
  txt-Free-F2-module : TextSymbol
  txt-Free-cyclic    : TextSymbol
  txt-Free-relation  : TextSymbol
  txt-Free-CCC       : TextSymbol
  txt-Free-Lie       : TextSymbol
  txt-Free-other     : TextSymbol
  -- Section headings
  txt-classification         : TextSymbol
  txt-rosetta-table          : TextSymbol
  txt-witness-summary        : TextSymbol
  txt-arc-summary            : TextSymbol
  txt-bicategorical-lift     : TextSymbol
  txt-yoneda-lemma           : TextSymbol
  txt-language-page          : TextSymbol
  txt-index                  : TextSymbol
  -- Common labels
  txt-name                   : TextSymbol
  txt-class                  : TextSymbol
  txt-basis                  : TextSymbol
  txt-free-carrier           : TextSymbol
  txt-universal-property     : TextSymbol
  txt-vs                     : TextSymbol     -- "vs"
  txt-same-class             : TextSymbol
  txt-different-class        : TextSymbol

------------------------------------------------------------------------
-- 2. MarkdownToken: structural atoms.
--
-- Each token carries a TextSymbol payload (or none, for purely
-- structural atoms like row-separator).
------------------------------------------------------------------------

data MarkdownToken : Set where
  -- Headings
  heading-1 : TextSymbol → MarkdownToken
  heading-2 : TextSymbol → MarkdownToken
  heading-3 : TextSymbol → MarkdownToken
  -- Content
  paragraph : TextSymbol → MarkdownToken
  inline    : TextSymbol → MarkdownToken
  -- Code
  code-line : TextSymbol → MarkdownToken
  -- Tables
  table-row    : MarkdownToken
  table-cell   : TextSymbol → MarkdownToken
  table-header : MarkdownToken
  -- Lists
  list-item-start : MarkdownToken
  list-item-text  : TextSymbol → MarkdownToken
  -- Links
  link : TextSymbol → TextSymbol → MarkdownToken  -- (label, target)
  -- Separators / spacing
  blank-line    : MarkdownToken
  horizontal-rule : MarkdownToken

------------------------------------------------------------------------
-- 3. Capstone for E1.
--
-- MarkdownToken + TextSymbol enumerations provided. E2 builds
-- Section records using these.
------------------------------------------------------------------------
