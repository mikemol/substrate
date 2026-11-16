------------------------------------------------------------------------
-- Substrate.Solresol.FreeLinearTransposition.TransposeWordAppend
--
-- Defines: transpose-word-++
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Solresol.FreeLinearTransposition; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.FreeLinearTransposition.TransposeWordAppend where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Solresol.Fragment.Transpose
open import Substrate.Solresol.Fragment.TransposeWord
open import Substrate.Solresol.Fragment.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- 3. transpose-word is a monoid homomorphism.
--
-- The free-extension property's "preserves composition" half:
-- transpose-word respects word concatenation.
------------------------------------------------------------------------

transpose-word-++ :
  (w₁ w₂ : SolresolWord) →
  transpose-word (w₁ ++ w₂) ≡ transpose-word w₁ ++ transpose-word w₂
transpose-word-++ []      w₂ = refl
transpose-word-++ (n ∷ w₁) w₂ =
  cong (transpose-1 n ∷_) (transpose-word-++ w₁ w₂)
