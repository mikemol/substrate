------------------------------------------------------------------------
-- Substrate.Solresol.FreeLinearTransposition.TransposeWord
--
-- Defines: transpose-word-ε
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Solresol.FreeLinearTransposition; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.FreeLinearTransposition.TransposeWord where

open import Substrate.Solresol.Fragment.TransposeWord
open import Substrate.Solresol.Fragment.Word
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 4. transpose-word respects ε.
------------------------------------------------------------------------

transpose-word-ε : transpose-word ε ≡ ε
transpose-word-ε = refl
