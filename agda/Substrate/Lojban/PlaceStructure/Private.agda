------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.PlaceStructure; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure.Private where

-- ⚑ Ⓑ8: `Level` IS DEMAND FROM THE `variable` BLOCK BELOW, and the split that
-- emitted this leaf did not carry its provider.  The leaf's BODY never says
-- `Level` — only its variable declaration does — which is the same seed-too-small
-- shape Ⓑ6ᶜ²⁵ fixed in `split_telescoped` for `ℕ`: whatever the leaf will CONTAIN
-- must be in the import probe, not just what its definitions say.
-- `Foundation.Level` is the insulation boundary that re-exports `Agda.Primitive`.
open import Substrate.Foundation.Level
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq.Cong



variable
  ℓA ℓB ℓC ℓD : Level
  n : ℕ
