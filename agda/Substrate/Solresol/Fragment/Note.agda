------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.Note
--
-- The 7 Solresol notes (do, re, mi, fa, sol, la, si) — the Western
-- diatonic scale used by Sudre's 1827 musical-syllable conlang.
-- Note index in Z/7 captures the cyclic transposition structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.Note where

data Note : Set where
  do₁ : Note   -- C
  re₁ : Note   -- D
  mi₁ : Note   -- E
  fa₁ : Note   -- F
  sol : Note   -- G
  la₁ : Note   -- A
  si₁ : Note   -- B
