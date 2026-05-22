------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example2Transitive
--
-- Worked example: "mi moku e kili" (I eat fruit).
--
--   Structure : transitive — subj=mi, pred=moku, obj=kili
--   Marker    : `e` between predicate and object (active)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example2Transitive where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)
open import Substrate.TokiPona.TokiSentence
open import Substrate.TokiPona.Particles
open import Substrate.TokiPona.LinearAlgebra

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
