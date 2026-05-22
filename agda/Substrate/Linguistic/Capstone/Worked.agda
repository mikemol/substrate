------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone.Worked
--
-- Worked Rosetta entries — the contrastive-pedagogy payoff.
-- A handful of cross-language alignments demonstrating the
-- structural-contrast IS pedagogy claim.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone.Worked where

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)
open import Substrate.Linguistic.RosettaTable using (RosettaEntry; pair-entry)

-- The original anchor pair: Free-monoid vs Free-F2-module.
worked-lojban-tokipona : RosettaEntry
worked-lojban-tokipona = pair-entry lojban-witness tokipona-witness

-- CCC-adjacent: Lojban (monoid, CCC-approximation) vs Lambda (pure CCC).
worked-lojban-lambda : RosettaEntry
worked-lojban-lambda = pair-entry lojban-witness lambda-witness

-- Structural-contrast: Kelen (relations) vs Lambda (functions).
worked-kelen-lambda : RosettaEntry
worked-kelen-lambda = pair-entry kelen-witness lambda-witness

-- Cyclic-flavour: TokiPona (F₂ self-inverse) vs Solresol (Z/7 cyclic basis).
worked-tokipona-solresol : RosettaEntry
worked-tokipona-solresol = pair-entry tokipona-witness solresol-witness

-- Fringe-cell: LieFrag (substrate-invented Lie cell) vs Lambda (CCC).
worked-lie-lambda : RosettaEntry
worked-lie-lambda = pair-entry lie-witness lambda-witness
