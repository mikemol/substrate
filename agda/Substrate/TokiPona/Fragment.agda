------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment
--
-- T9 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]]. Capstone slice: top-level
-- re-export plus worked example sentences with explicit witnesses.
--
-- Sister slice to Lojban L9 Fragment. Both arcs use the SAME
-- contrastive-pedagogy presentation per [[user-rosetta-code-contrastive-pedagogy]]:
-- each example presents the Toki Pona string, the Agda term, and
-- the semantic interpretation in three columns.
--
-- The four worked examples span:
--   1. intransitive (soweli li suli — the animal is big)
--   2. transitive (mi moku e kili — I eat fruit)
--   3. subject-modifier (jan pona li toki e ijo — good-people
--      speak about things; modifier-chain on subject)
--   4. pi-regrouping (tomo lili pi soweli wawa — small house of
--      strong animals; demonstrates `pi`'s right-grouping)
--
-- Plus one particle-stacking example demonstrating T7 coherence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

-- Re-export T1-T8 publicly so consumers get the whole arc.
open import Substrate.TokiPona.SemanticSpace public
open import Substrate.TokiPona.Nimi public
open import Substrate.TokiPona.NimiSpace public
  using (nimi-as-vector; nimi-from-index; from-index∘index)
open import Substrate.TokiPona.ModifierBilinear public
  using (modify; modifier-chain;
         modify-identityˡ; modify-identityʳ;
         modify-comm; modify-assoc; modify-self-inverse)
open import Substrate.TokiPona.TokiSentence public
open import Substrate.TokiPona.Particles public
open import Substrate.TokiPona.Linearity public
open import Substrate.TokiPona.LinearAlgebra public

------------------------------------------------------------------------
-- 1. Worked example 1 — "soweli li suli" (the animal is big).
--
--   Toki Pona  : soweli li suli
--   Structure  : intransitive — subject=soweli, predicate=suli
--   Agda term  : intransitive (nimi-as-vector soweli) (nimi-as-vector suli)
--   Semantics  : basis(soweli) ⊕ basis(suli)  via feature-bag pooling
------------------------------------------------------------------------

example-soweli-li-suli : TokiSentence nimi-count
example-soweli-li-suli =
  intransitive (nimi-as-vector soweli) (nimi-as-vector suli)

example-1-interp :
  interpret example-soweli-li-suli
    ≡ (nimi-as-vector soweli ⊕ nimi-as-vector suli) ⊕ ∅
example-1-interp = refl

------------------------------------------------------------------------
-- 2. Worked example 2 — "mi moku e kili" (I eat fruit).
--
--   Toki Pona  : mi moku e kili
--   Structure  : transitive — subj=mi, pred=moku, obj=kili
--   Marker     : `e` between predicate and object (active)
------------------------------------------------------------------------

example-mi-moku-e-kili : TokiSentence nimi-count
example-mi-moku-e-kili =
  transitive (nimi-as-vector mi) (nimi-as-vector moku) (nimi-as-vector kili)

example-2-interp :
  interpret example-mi-moku-e-kili
    ≡ (nimi-as-vector mi ⊕ nimi-as-vector moku) ⊕ nimi-as-vector kili
example-2-interp = refl

-- The marked version with `e` particle active:
example-2-marked : MarkedSentence nimi-count
example-2-marked = with-particle e (mark example-mi-moku-e-kili)

------------------------------------------------------------------------
-- 3. Worked example 3 — "jan pona li toki e ijo"
--                       (good people speak about things).
--
--   Toki Pona  : jan pona li toki e ijo
--   Structure  : transitive, with subject modifier (jan + pona)
--   Subject    : modify (jan) (pona)  — modifier-chain on subject
------------------------------------------------------------------------

subject-jan-pona : SemVec nimi-count
subject-jan-pona = modify (nimi-as-vector jan) (nimi-as-vector pona)

example-jan-pona-toki-ijo : TokiSentence nimi-count
example-jan-pona-toki-ijo =
  transitive subject-jan-pona (nimi-as-vector toki) (nimi-as-vector ijo)

example-3-interp :
  interpret example-jan-pona-toki-ijo
    ≡ (subject-jan-pona ⊕ nimi-as-vector toki) ⊕ nimi-as-vector ijo
example-3-interp = refl

-- The modifier-chain on the subject can also be expressed as a
-- Coxeter-Word fold, demonstrating T4's modifier-chain primitive:
subject-jan-pona-via-chain : SemVec nimi-count
subject-jan-pona-via-chain =
  modifier-chain (nimi-as-vector jan) (nimi-as-vector pona ∷ [])

example-3-chain-equiv : subject-jan-pona ≡ subject-jan-pona-via-chain
example-3-chain-equiv = refl

------------------------------------------------------------------------
-- 4. Worked example 4 — "tomo lili pi soweli wawa"
--                       (small house of strong animals; pi-regrouping).
--
--   Toki Pona  : tomo lili pi soweli wawa
--   Structure  : head=tomo modified by (lili) at left, AND by
--                the right-group (soweli wawa) — that's `pi`'s role:
--                it regroups subsequent modifiers as a unit.
--   Agda term  : modifier-chain over a structured Word.
--   Coherence  : modify-assoc + T7's chain-++ ensure the grouping
--                gives the same semantic vector either way.
------------------------------------------------------------------------

-- The right group "soweli wawa" as a sub-modifier (composed via
-- modifier-chain).
right-group-soweli-wawa : SemVec nimi-count
right-group-soweli-wawa =
  modifier-chain (nimi-as-vector soweli) (nimi-as-vector wawa ∷ [])

-- The full sentence's head: tomo modified by lili then by the right-
-- group.
head-tomo-lili-pi-soweli-wawa : SemVec nimi-count
head-tomo-lili-pi-soweli-wawa =
  modifier-chain (nimi-as-vector tomo)
    (nimi-as-vector lili ∷ right-group-soweli-wawa ∷ [])

example-tomo-lili-pi-soweli-wawa : TokiSentence nimi-count
example-tomo-lili-pi-soweli-wawa =
  intransitive head-tomo-lili-pi-soweli-wawa ∅

-- Demonstrate `pi`-regrouping invariance: the same vector arises
-- whether we group as (tomo (lili (soweli wawa))) or
-- ((tomo lili) (soweli wawa)) etc., because modify-assoc collapses
-- the parentheses.
example-4-regrouping :
  modify (modify (nimi-as-vector tomo) (nimi-as-vector lili))
         (modify (nimi-as-vector soweli) (nimi-as-vector wawa))
    ≡ modify (nimi-as-vector tomo)
             (modify (nimi-as-vector lili)
                     (modify (nimi-as-vector soweli) (nimi-as-vector wawa)))
example-4-regrouping =
  modify-assoc (nimi-as-vector tomo) (nimi-as-vector lili)
               (modify (nimi-as-vector soweli) (nimi-as-vector wawa))

-- The marked version with `pi` particle active:
example-4-marked : MarkedSentence nimi-count
example-4-marked = with-particle pi (mark example-tomo-lili-pi-soweli-wawa)

------------------------------------------------------------------------
-- 5. Worked example 5 — particle-stacking coherence.
--
--   Demonstrates T7's `mod-assoc` + the linearity coherence record's
--   `chain-++` law: combining particles via with-particle composes
--   their marker bits via merge-markers.
------------------------------------------------------------------------

-- A sentence with both `e` and `la` particles active:
example-5-stacked : MarkedSentence nimi-count
example-5-stacked =
  with-particle la (with-particle e (mark example-mi-moku-e-kili))

-- Compose markers directly:
example-5-direct-markers : MarkerSet
example-5-direct-markers =
  merge-markers (set-particle e) (set-particle la)

-- The composed marker matches the post-stacked one:
example-5-coherence :
  markers example-5-stacked ≡ example-5-direct-markers
example-5-coherence = refl

------------------------------------------------------------------------
-- 6. The TokiLinearity record is in scope, witnessing T7's
-- coherence laws for any consumer of this fragment.
------------------------------------------------------------------------

linearity-witness : TokiLinearity nimi-count
linearity-witness = canonical-linearity

------------------------------------------------------------------------
-- 7. The free-linear universal property is in scope via T8, ready
-- for T10's bridge to consume.
------------------------------------------------------------------------

free-witness : NimiFreeLinearization nimi-count
free-witness = canonical-nimi-free
