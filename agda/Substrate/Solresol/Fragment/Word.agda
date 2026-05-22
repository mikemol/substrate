------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.Word
--
-- SolresolWord = free monoid over Note via Coxeter.Word.
-- Includes the empty word ε and the single-note lift.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.Word where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Solresol.Fragment.Note using (Note)

SolresolWord : Set
SolresolWord = Word Note

ε : SolresolWord
ε = []

single : Note → SolresolWord
single n = n ∷ []
