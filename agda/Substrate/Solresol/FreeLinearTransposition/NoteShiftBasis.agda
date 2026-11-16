------------------------------------------------------------------------
-- Substrate.Solresol.FreeLinearTransposition.NoteShiftBasis
--
-- Defines: note-shift-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Solresol.FreeLinearTransposition; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.FreeLinearTransposition.NoteShiftBasis where

open import Substrate.Solresol.Fragment.Note
open import Substrate.Solresol.Fragment.Transpose
open import Substrate.Solresol.Fragment.Word



------------------------------------------------------------------------
-- 1. The basis-map.
--
-- Each Note transposes by one semitone, lifted to a single-symbol
-- SolresolWord. This is the basis-image for the free-monoid
-- extension.
------------------------------------------------------------------------

note-shift-basis : Note → SolresolWord
note-shift-basis n = single (transpose-1 n)
