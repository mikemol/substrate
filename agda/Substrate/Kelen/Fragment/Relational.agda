------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.Relational
--
-- Defines: Relational, jana, la, nā, pa
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.Relational where

open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. The 4 Kēlen relationals.
--
-- Each carries a place-structure arity (the number of NP slots);
-- in real Kēlen, the relationals have positional semantics tied
-- to their meaning.
------------------------------------------------------------------------

data Relational : Set where
  la    : Relational   -- "is in state of" (2-place: la NP-be NP-state)
  nā    : Relational   -- "happens / exists" (1-place existential)
  pa    : Relational   -- "consists of / has" (3-place possession)
  jana  : Relational   -- "moves toward / changes" (3-place motion)
