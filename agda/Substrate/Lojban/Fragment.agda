------------------------------------------------------------------------
-- Substrate.Lojban.Fragment
--
-- L9 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Capstone slice: top-level re-export plus worked example sentences
-- with explicit well-typed witnesses. Three example bridi are built
-- and their interpretations are pinned via `_≡_` smoke tests; the
-- tests are `refl` because the entailment from L7+L8 reduces them
-- definitionally.
--
-- Per [[feedback-comments-dont-overclaim]]: the worked sentences
-- are illustrative, not exhaustive — real Lojban has place-
-- structure conversions, sumti articles, attitudinals, and dozens
-- of additional cmavo, all deferred per the arc plan.
--
-- Per [[project-linguistic-rosetta-arc]]'s contrastive-pedagogy
-- aim: each example is presented in three layers (Lojban string in
-- comment, Agda term with explicit selbri+args, semantic
-- interpretation) so a reader can compare them column-by-column.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

-- Re-export the L1-L8 surface so consumers can `open import
-- Substrate.Lojban.Fragment` and get the whole arc.
open import Substrate.Lojban.PlaceStructure public
open import Substrate.Lojban.Gismu public
open import Substrate.Lojban.Lujvo public
  using (Lujvo; mkLujvo; lujvo-word; lujvo-arity;
         gismu-as-lujvo; prepend-modifiers; prepend-modifier)
open import Substrate.Lojban.Bridi public
open import Substrate.Lojban.Cmavo public
open import Substrate.Lojban.Functoriality public
open import Substrate.Lojban.WordAlgebra public
  using (MonoidLaws; LojbanWord-Monoid; module WithTarget)

------------------------------------------------------------------------
-- 1. A concrete Sumti carrier for the worked examples.
--
-- Names + descriptors. Real Lojban has richer sumti construction
-- (le/lo/la articles, descriptions, sub-bridi); the fragment uses
-- atomic descriptors as Sumti directly.
------------------------------------------------------------------------

data Sumti : Set where
  mi       : Sumti  -- I, me
  do-pn    : Sumti  -- you  (named with -pn suffix since `do` is reserved)
  ti       : Sumti  -- this
  ta       : Sumti  -- that
  zo-e     : Sumti  -- unspecified (Lojban zo'e)
  le-zarci : Sumti  -- the market
  le-prenu : Sumti  -- the person
  le-gerku : Sumti  -- the dog
  le-pendo : Sumti  -- the friend

------------------------------------------------------------------------
-- 2. A concrete Sem (semantic) carrier.
--
-- Records the gismu and its actual argument vector, plus tense/
-- negation wrappers. The dependent type Vec Sumti (arity g) encodes
-- well-typedness: a `fact` can only be constructed when the
-- argument count matches the gismu's arity.
------------------------------------------------------------------------

data Sem : Set where
  fact   : (g : Gismu) → Vec Sumti (arity g) → Sem
  pu-of  : Sem → Sem
  ca-of  : Sem → Sem
  ba-of  : Sem → Sem
  na-of  : Sem → Sem

------------------------------------------------------------------------
-- 3. Canonical denotation: each gismu denotes its `fact` constructor.
------------------------------------------------------------------------

denote : (g : Gismu) → Vec Sumti (arity g) → Sem
denote = fact

------------------------------------------------------------------------
-- 4. Tense / negation semantic operations for the cmavo wrappers.
------------------------------------------------------------------------

tense-sem : TenseMarker → Sem → Sem
tense-sem pu = pu-of
tense-sem ca = ca-of
tense-sem ba = ba-of

negate : Sem → Sem
negate = na-of

------------------------------------------------------------------------
-- 5. Instantiate the Gismu-side WithDenotation submodule.
------------------------------------------------------------------------

open Substrate.Lojban.Gismu.WithDenotation Sumti Sem denote
  using (gismu-to-selbri)

open Substrate.Lojban.Cmavo.WithTense Sumti Sem tense-sem
  using (PU)
open Substrate.Lojban.Cmavo.WithNegation Sumti Sem negate
  using (NA)

------------------------------------------------------------------------
-- 6. Worked example 1 — "mi nelci do" (I like you).
--
--   Lojban string : mi nelci do
--   Place structure : nelci is 2-place (x₁ likes x₂)
--   Agda term : a 2-place bridi with selbri = nelci, args = (mi, do-pn)
------------------------------------------------------------------------

example-mi-nelci-do : Bridi 2 Sumti Sem
example-mi-nelci-do = make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ [])

example-1-interp :
  interpret example-mi-nelci-do ≡ fact nelci (mi ∷ do-pn ∷ [])
example-1-interp = refl

------------------------------------------------------------------------
-- 7. Worked example 2 — "mi klama le zarci" (I go to the market).
--
--   Lojban string : mi klama le zarci
--   Place structure : klama is 5-place (x₁ goes to x₂ from x₃ via x₄
--                     using x₅) — unfilled slots take zo'e
--   Agda term : 5-place bridi (mi, le-zarci, zo-e, zo-e, zo-e)
------------------------------------------------------------------------

example-mi-klama-le-zarci : Bridi 5 Sumti Sem
example-mi-klama-le-zarci =
  make-bridi (gismu-to-selbri klama)
             (mi ∷ le-zarci ∷ zo-e ∷ zo-e ∷ zo-e ∷ [])

example-2-interp :
  interpret example-mi-klama-le-zarci
    ≡ fact klama (mi ∷ le-zarci ∷ zo-e ∷ zo-e ∷ zo-e ∷ [])
example-2-interp = refl

------------------------------------------------------------------------
-- 8. Worked example 3 — "mi pu tavla do" (I talked to you).
--
--   Lojban string : mi pu tavla do
--   Place structure : tavla is 4-place (x₁ talks to x₂ about x₃ in
--                     language x₄) under past-tense (pu) wrapper
--   Agda term : apply-cmavo (PU pu) of the base 4-place bridi
------------------------------------------------------------------------

example-mi-pu-tavla-do : Bridi 4 Sumti Sem
example-mi-pu-tavla-do =
  apply-cmavo (PU pu)
    (make-bridi (gismu-to-selbri tavla)
                (mi ∷ do-pn ∷ zo-e ∷ zo-e ∷ []))

example-3-interp :
  interpret example-mi-pu-tavla-do
    ≡ pu-of (fact tavla (mi ∷ do-pn ∷ zo-e ∷ zo-e ∷ []))
example-3-interp = refl

------------------------------------------------------------------------
-- 9. Worked example 4 — "mi na nelci do" (I do not like you).
--
--   Demonstrates NA negation as a cmavo wrapper. With L7's
--   `cmavo-compose-coherent`, stacking PU and NA composes their
--   semantic operations — see example-5 below.
------------------------------------------------------------------------

example-mi-na-nelci-do : Bridi 2 Sumti Sem
example-mi-na-nelci-do =
  apply-cmavo NA
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ []))

example-4-interp :
  interpret example-mi-na-nelci-do
    ≡ na-of (fact nelci (mi ∷ do-pn ∷ []))
example-4-interp = refl

------------------------------------------------------------------------
-- 10. Worked example 5 — stacked cmavo (NA after PU).
--
--   Demonstrates the [[feedback-grothendieck-coherence-rule]]
--   compose-coherence from L7: applying NA after PU yields the
--   same semantic value as applying their composed wrapper.
------------------------------------------------------------------------

example-stacked : Bridi 2 Sumti Sem
example-stacked =
  apply-cmavo NA (apply-cmavo (PU pu)
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ [])))

example-5-interp :
  interpret example-stacked
    ≡ na-of (pu-of (fact nelci (mi ∷ do-pn ∷ [])))
example-5-interp = refl

-- The compose-coherence path (citing L7) gives the same interpretation:
example-stacked-via-compose : Bridi 2 Sumti Sem
example-stacked-via-compose =
  apply-cmavo (NA ∘-cmavo PU pu)
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ []))

example-5-coherent :
  interpret example-stacked ≡ interpret example-stacked-via-compose
example-5-coherent =
  cmavo-compose-coherent NA (PU pu)
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ []))
