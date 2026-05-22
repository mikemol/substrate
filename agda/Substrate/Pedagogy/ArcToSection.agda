------------------------------------------------------------------------
-- Substrate.Pedagogy.ArcToSection
--
-- E6 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Generate a Section describing an arc: arc name + slice count +
-- contribution summary. Used by the cross-arc Index (E9) to
-- describe each substrate arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.ArcToSection where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Pedagogy.MarkdownToken
  using (MarkdownToken; TextSymbol;
         txt-arc-summary;
         heading-2; paragraph; inline; blank-line;
         table-row; table-cell)
open import Substrate.Pedagogy.Section
  using (Section; mkSection; SectionKind; arc-summary-section)

------------------------------------------------------------------------
-- 1. ArcDescription record.
--
-- A substrate-internal description of an arc that can be rendered.
------------------------------------------------------------------------

record ArcDescription : Set where
  constructor mkArcDescription
  field
    arc-name        : TextSymbol
    slice-count     : ℕ
    summary-text    : TextSymbol

open ArcDescription public

------------------------------------------------------------------------
-- 2. Generator: ArcDescription → Section.
------------------------------------------------------------------------

arc→section : ArcDescription → Section
arc→section a = mkSection
  (arc-name a)
  body
  arc-summary-section
  where
    body : Word MarkdownToken
    body =
      heading-2 (arc-name a) ∷
      paragraph (summary-text a) ∷
      blank-line ∷
      []

------------------------------------------------------------------------
-- 3. Capstone for E6.
--
-- Arc → Section generator. E7-E8 assemble PageBundles using
-- the three generators (witness, rosetta, arc).
------------------------------------------------------------------------
