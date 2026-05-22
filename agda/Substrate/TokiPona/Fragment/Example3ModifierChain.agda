------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example3ModifierChain
--
-- Worked example: "jan pona li toki e ijo" (good people speak about things).
--
--   Structure : transitive, with subject modifier (jan + pona)
--   Subject   : modify (jan) (pona) — modifier-chain on subject
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example3ModifierChain where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)
open import Substrate.TokiPona.ModifierBilinear using (modify; modifier-chain)
open import Substrate.TokiPona.TokiSentence
open import Substrate.TokiPona.LinearAlgebra

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
