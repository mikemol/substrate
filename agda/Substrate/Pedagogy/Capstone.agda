------------------------------------------------------------------------
-- Substrate.Pedagogy.Capstone
--
-- E10 of the Pedagogical Export arc per [scratch/e_arc_plan.md].
--
-- Capstone: re-export of E1-E9 + a worked Lojban-page example
-- demonstrating end-to-end Section assembly from substrate data.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pedagogy.Capstone where

-- Re-export the E-arc slices publicly.
open import Substrate.Pedagogy.MarkdownToken public
open import Substrate.Pedagogy.Section public
open import Substrate.Pedagogy.PageBundle public
open import Substrate.Pedagogy.WitnessToSection public
open import Substrate.Pedagogy.RosettaToSection public
open import Substrate.Pedagogy.ArcToSection public
open import Substrate.Pedagogy.LanguagePage public
open import Substrate.Pedagogy.RosettaPage public
open import Substrate.Pedagogy.Index public

-- Bring in the substrate witnesses for the worked example.
open import Substrate.Linguistic.Roster using (lojban; tokipona)

------------------------------------------------------------------------
-- 1. Worked example: the Lojban PageBundle.
--
-- Assembled from substrate data using language-page (E7).
------------------------------------------------------------------------

lojban-page : PageBundle
lojban-page = language-page lojban

------------------------------------------------------------------------
-- 2. Worked example: the Toki Pona PageBundle.
------------------------------------------------------------------------

tokipona-page : PageBundle
tokipona-page = language-page tokipona

------------------------------------------------------------------------
-- 3. Top-level outputs: the three primary PageBundles ready for
-- an external renderer.
------------------------------------------------------------------------

substrate-index-output : PageBundle
substrate-index-output = index-page

substrate-rosetta-output : PageBundle
substrate-rosetta-output = rosetta-page

------------------------------------------------------------------------
-- 4. Capstone for the E-arc.
--
-- The substrate now has:
--   * MarkdownToken + TextSymbol enums (E1) — substrate-native
--     pedagogical atoms
--   * Section + PageBundle records (E2-E3) — the rendering units
--   * Per-record generators (E4-E6) — Witness, Rosetta, Arc → Section
--   * Page assemblers (E7-E8) — LanguagePage, RosettaPage
--   * Index (E9) — top-level table of contents
--   * Worked examples (E10) — lojban-page, tokipona-page,
--     substrate-index-output, substrate-rosetta-output
--
-- An external markdown renderer (Python / shell — out of Agda
-- --safe scope) ingests these PageBundles + a TextSymbol→string
-- lookup table and produces the contrastive-pedagogy Rosetta-
-- style markdown the user wanted from the start.
--
-- Future arcs:
--   * The external renderer itself (Python/shell companion arc)
--   * Cross-link manifest (rich navigation between pages)
--   * Search index / typed cross-references at the substrate-
--     internal level
--   * Per-arc deeper section content (currently each is just a
--     heading + summary stub; could include slice-by-slice
--     descriptions)
--   * HTML / web renderer extensions
--   * Pedagogy for the Q-arc (numeric carrier pages)
--
-- 20-slice sprint Q-arc + E-arc closes; substrate now has both
-- richer numeric carriers and a pedagogical export surface.
------------------------------------------------------------------------
