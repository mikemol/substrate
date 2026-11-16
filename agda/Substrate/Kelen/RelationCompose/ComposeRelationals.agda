------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.ComposeRelationals
--
-- Defines: compose-relationals
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.ComposeRelationals where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.Single
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp



------------------------------------------------------------------------
-- 4. Lifting basic relationals to words via single + composition.
--
-- A common pattern: build a composed relation from two atomic
-- relationals. E.g., (la ∘ᴿ pa) = la-then-pa-composed.
------------------------------------------------------------------------

compose-relationals : Relational → Relational → KelenWord
compose-relationals r₁ r₂ = single r₁ ∘ᴿ single r₂
