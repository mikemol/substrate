------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example1Intransitive
--
-- Worked example: "soweli li suli" (the animal is big).
--
--   Toki Pona  : soweli li suli
--   Structure  : intransitive — subject=soweli, predicate=suli
--   Semantics  : basis(soweli) ⊕ basis(suli)  via feature-bag pooling
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example1Intransitive where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)
open import Substrate.TokiPona.TokiSentence
open import Substrate.TokiPona.LinearAlgebra

example-soweli-li-suli : TokiSentence nimi-count
example-soweli-li-suli =
  intransitive (nimi-as-vector soweli) (nimi-as-vector suli)

example-1-interp :
  interpret example-soweli-li-suli
    ≡ (nimi-as-vector soweli ⊕ nimi-as-vector suli) ⊕ ∅
example-1-interp = refl
