------------------------------------------------------------------------
-- Substrate.Solresol.FreeLinearTransposition.TransposeWordOnBasis
--
-- Defines: transpose-word-on-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Solresol.FreeLinearTransposition; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.FreeLinearTransposition.TransposeWordOnBasis where

open import Substrate.Solresol.Fragment.Note
open import Substrate.Solresol.Fragment.Transpose
open import Substrate.Solresol.Fragment.TransposeWord
open import Substrate.Solresol.Fragment.Word
open import Substrate.Foundation.Eq
open import Substrate.Solresol.FreeLinearTransposition.NoteShiftBasis



------------------------------------------------------------------------
-- 2. transpose-word agrees with the basis-map on basis vectors.
--
-- The free-extension property's "extension on basis" half:
-- transpose-word applied to a single-Note word IS the basis-map.
------------------------------------------------------------------------

transpose-word-on-basis :
  (n : Note) → transpose-word (single n) ≡ note-shift-basis n
transpose-word-on-basis _ = refl
