------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.NoteIndex
--
-- note-count + note-index : the Note → Fin 7 embedding into Z/7.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.NoteIndex where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Solresol.Fragment.Note
  using (Note; do₁; re₁; mi₁; fa₁; sol; la₁; si₁)

note-count : ℕ
note-count = 7

note-index : Note → Fin note-count
note-index do₁ = zero
note-index re₁ = suc zero
note-index mi₁ = suc ₁
note-index fa₁ = suc ₂
note-index sol = suc ₃
note-index la₁ = suc ₄
note-index si₁ = suc ₅
