------------------------------------------------------------------------
-- Substrate.Lojban.Fragment
--
-- L9 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Capstone slice (file-per-example decomposition). Re-exports L1-L8
-- plus the worked-example submodules; each example is a self-contained
-- bridi + interpretation lemma in its own file. Mirrors the
-- TokiPona.Fragment shape so the contrastive-pedagogy alignment
-- (per [[project-linguistic-rosetta-arc]]) is structural.
--
--   Fragment.Carriers              — Sumti / Sem + WithDenotation/Tense/Negation
--   Fragment.Example1MiNelciDo     — "mi nelci do"
--   Fragment.Example2MiKlamaLeZarci — "mi klama le zarci"
--   Fragment.Example3MiPuTavlaDo   — "mi pu tavla do" (tense wrapper)
--   Fragment.Example4MiNaNelciDo   — "mi na nelci do" (negation wrapper)
--   Fragment.Example5Stacked       — stacked NA-of-PU + compose-coherence
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment where

-- Re-export the L1-L8 surface so consumers can `open import
-- Substrate.Lojban.Fragment` and get the whole arc.
open import Substrate.Lojban.PlaceStructure
open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Lujvo
  using (Lujvo; mkLujvo; lujvo-word; lujvo-arity;
         gismu-as-lujvo; prepend-modifiers; prepend-modifier)
open import Substrate.Lojban.Bridi
open import Substrate.Lojban.Cmavo
open import Substrate.Lojban.Functoriality
open import Substrate.Lojban.WordAlgebra
  using (MonoidLaws; LojbanWord-Monoid; module WithTarget)

-- Worked-example submodules.
open import Substrate.Lojban.Fragment.Carriers
open import Substrate.Lojban.Fragment.Example1MiNelciDo
open import Substrate.Lojban.Fragment.Example2MiKlamaLeZarci
open import Substrate.Lojban.Fragment.Example3MiPuTavlaDo
open import Substrate.Lojban.Fragment.Example4MiNaNelciDo
open import Substrate.Lojban.Fragment.Example5Stacked