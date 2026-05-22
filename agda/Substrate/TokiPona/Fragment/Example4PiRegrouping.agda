------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example4PiRegrouping
--
-- Worked example: "tomo lili pi soweli wawa"
-- (small house of strong animals; pi-regrouping).
--
--   Structure : head=tomo modified by (lili) at left AND by the
--               right-group (soweli wawa) — that's `pi`'s role:
--               it regroups subsequent modifiers as a unit.
--   Agda term : modifier-chain over a structured Word.
--   Coherence : modify-assoc + T7's chain-++ ensure the grouping
--               gives the same semantic vector either way.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example4PiRegrouping where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)
open import Substrate.TokiPona.ModifierBilinear
  using (modify; modifier-chain; modify-assoc)
open import Substrate.TokiPona.TokiSentence
open import Substrate.TokiPona.Particles
open import Substrate.TokiPona.LinearAlgebra

-- The right group "soweli wawa" as a sub-modifier.
right-group-soweli-wawa : SemVec nimi-count
right-group-soweli-wawa =
  modifier-chain (nimi-as-vector soweli) (nimi-as-vector wawa ∷ [])

-- tomo modified by lili then by the right-group.
head-tomo-lili-pi-soweli-wawa : SemVec nimi-count
head-tomo-lili-pi-soweli-wawa =
  modifier-chain (nimi-as-vector tomo)
    (nimi-as-vector lili ∷ right-group-soweli-wawa ∷ [])

example-tomo-lili-pi-soweli-wawa : TokiSentence nimi-count
example-tomo-lili-pi-soweli-wawa =
  intransitive head-tomo-lili-pi-soweli-wawa ∅

-- Demonstrate `pi`-regrouping invariance via modify-assoc.
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
