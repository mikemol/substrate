------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.ExampleLaSkeleton
--
-- Defines: example-la-skeleton
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.ExampleLaSkeleton where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.KelenWord



------------------------------------------------------------------------
-- 3. Worked example: a small Kēlen sentence skeleton.
--
-- "la NP NP" — a state-of-being assertion. In real Kēlen this
-- requires Sumti-like noun-phrase arguments; here we represent
-- just the relational skeleton.
------------------------------------------------------------------------

example-la-skeleton : KelenWord
example-la-skeleton = la ∷ []
