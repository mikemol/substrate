------------------------------------------------------------------------
-- Substrate.Linguistic.Roster.Lang
--
-- Defines: Lang, kelen, lambda-lang, lie-lang, lojban, solresol, tokipona
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Roster; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Roster.Lang where




------------------------------------------------------------------------
-- 1. The enumeration: one constructor per witness instance.
------------------------------------------------------------------------

data Lang : Set where
  lojban      : Lang
  tokipona    : Lang
  solresol    : Lang
  kelen       : Lang
  lambda-lang : Lang
  lie-lang    : Lang
