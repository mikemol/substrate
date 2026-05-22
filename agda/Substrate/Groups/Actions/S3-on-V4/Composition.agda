------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition
--
-- act-∙: the action's composition law (file-per-lemma):
--   Composition.Block00            — h₁ = h₂ = []  (pure rotations)
--   Composition.Block01            — h₁ = [], h₂ = [a]
--   Composition.Block10            — h₁ = [a], h₂ = [] (twist inverts n₂)
--   Composition.Block11            — h₁ = h₂ = [a]   (full dihedral)
--   Composition.ActDotCanonical    — 4-way dispatcher over (h₁, h₂)
--   Composition.ActDot             — full action via normalize-idem bridge
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition where

open import Substrate.Groups.Actions.S3-on-V4.Composition.Block00          public
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block01          public
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block10          public
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block11          public
open import Substrate.Groups.Actions.S3-on-V4.Composition.ActDotCanonical  public
open import Substrate.Groups.Actions.S3-on-V4.Composition.ActDot           public
