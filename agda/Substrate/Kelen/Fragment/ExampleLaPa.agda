------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.ExampleLaPa
--
-- Defines: example-la-pa
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.ExampleLaPa where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.KelenWord



-- A composed sentence skeleton: "la ... pa ..." — being-state
-- followed by composition-of (relation composition).
example-la-pa : KelenWord
example-la-pa = la ∷ pa ∷ []
