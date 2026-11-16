------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.ExampleLaThenPa
--
-- Defines: example-la-then-pa
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.ExampleLaThenPa where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.Single
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp
open import Substrate.Kelen.RelationCompose.ComposeRelationals



------------------------------------------------------------------------
-- 5. Worked examples.
--
-- Two atomic relationals composed; demonstrates the operation works.
------------------------------------------------------------------------


-- la then pa (composed): la ∘ᴿ pa
example-la-then-pa : KelenWord
example-la-then-pa = compose-relationals la pa
