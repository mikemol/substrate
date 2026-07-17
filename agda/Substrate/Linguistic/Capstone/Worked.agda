------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone.Worked
--
-- Worked Rosetta entries — the contrastive-pedagogy payoff.
-- A handful of cross-language alignments demonstrating the
-- structural-contrast IS pedagogy claim.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone.Worked where

open import Substrate.Linguistic.Roster
  using (lojban; tokipona; solresol; kelen; lambda-lang; lie-lang)
open import Substrate.Linguistic.RosettaTable using (RosettaEntry; pair-entry)

-- The original anchor pair: Free-monoid vs Free-F2-module.
worked-lojban-tokipona : RosettaEntry
worked-lojban-tokipona = pair-entry lojban tokipona

-- CCC-adjacent: Lojban (monoid, CCC-approximation) vs Lambda (pure CCC).
worked-lojban-lambda : RosettaEntry
worked-lojban-lambda = pair-entry lojban lambda-lang

-- Structural-contrast: Kelen (relations) vs Lambda (functions).
worked-kelen-lambda : RosettaEntry
worked-kelen-lambda = pair-entry kelen lambda-lang

-- Cyclic-flavour: TokiPona (F₂ self-inverse) vs Solresol (Z/7 cyclic basis).
worked-tokipona-solresol : RosettaEntry
worked-tokipona-solresol = pair-entry tokipona solresol

-- Fringe-cell: LieFrag (substrate-invented Lie cell) vs Lambda (CCC).
worked-lie-lambda : RosettaEntry
worked-lie-lambda = pair-entry lie-lang lambda-lang
