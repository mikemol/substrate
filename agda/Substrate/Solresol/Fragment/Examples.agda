------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.Examples
--
-- Worked example Solresol words. Real Solresol vocabulary uses multi-
-- note words; the fragment demonstrates a few. Names are illustrative.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.Examples where

open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Solresol.Fragment.Note using (do₁; re₁; mi₁; sol; la₁)
open import Substrate.Solresol.Fragment.Word using (SolresolWord)

-- "doredo" — pronoun "I" in Solresol.
word-doredo : SolresolWord
word-doredo = do₁ ∷ re₁ ∷ do₁ ∷ []

-- "domi" — affirmation.
word-domi : SolresolWord
word-domi = do₁ ∷ mi₁ ∷ []

-- "soldorela" — illustrative 4-note word.
word-soldorela : SolresolWord
word-soldorela = sol ∷ do₁ ∷ re₁ ∷ la₁ ∷ []
