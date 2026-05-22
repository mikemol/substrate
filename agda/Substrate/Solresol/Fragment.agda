------------------------------------------------------------------------
-- Substrate.Solresol.Fragment
--
-- C4 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Solresol as the Free cyclic group witness. File-per-lemma:
--
--   Fragment.Note            — 7 Solresol notes (do/re/mi/fa/sol/la/si)
--   Fragment.NoteIndex       — Note → Fin 7 embedding into Z/7
--   Fragment.Word            — SolresolWord = Word Note
--   Fragment.Examples        — illustrative multi-note words
--   Fragment.Transpose       — transpose-1 + transpose-7 + 7-id witness
--   Fragment.TransposeWord   — pointwise lift to SolresolWord
--   Fragment.Witness         — FreeOverBasis + LanguageWitness packaging
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment where

open import Substrate.Solresol.Fragment.Note          public
open import Substrate.Solresol.Fragment.NoteIndex     public
open import Substrate.Solresol.Fragment.Word          public
open import Substrate.Solresol.Fragment.Examples      public
open import Substrate.Solresol.Fragment.Transpose     public
open import Substrate.Solresol.Fragment.TransposeWord public
open import Substrate.Solresol.Fragment.Witness       public
