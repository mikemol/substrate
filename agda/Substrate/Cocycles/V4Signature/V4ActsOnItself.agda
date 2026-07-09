------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4ActsOnItself
--
-- V₄ acts on itself by left translation (regular representation).
-- This is the action whose torsor witness underwrites the CY-5
-- cocycle's fiber structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4ActsOnItself where

open import Substrate.Cocycle using (Action)
open import Substrate.Groups.V4 as V4 using (V₄)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Cocycles.V4Signature.V4GroupSetoid using (V₄-Group-Setoid)

V4-acts-on-itself : Action V₄ _≡_ V₄-Group-Setoid V₄
V4-acts-on-itself = record
  { act    = V4._·_
  ; act-id = V4.ε-left
  ; act-∙  = λ g h b → V4.·-assoc g h b
  }
