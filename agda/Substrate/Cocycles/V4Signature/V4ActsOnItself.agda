------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4ActsOnItself
--
-- V₄ acts on itself by left translation (regular representation).
-- This is the action whose torsor witness underwrites the CY-5
-- cocycle's fiber structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4ActsOnItself where
open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Groups.V4.Bijection using (V₄)

open import Substrate.Algebra.SetoidGroup.Action using (Action)
import Substrate.Groups.V4.Operations as V4
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Cocycles.V4Signature.V4GroupSetoid using (V₄-Group-Setoid)

V4-acts-on-itself : Action V₄ _≡_ V₄-Group-Setoid V₄
V4-acts-on-itself = record
  { act    = _·_
  ; act-id = ε-left
  ; act-∙  = λ g h b → ·-assoc g h b
  }
