------------------------------------------------------------------------
-- Substrate.Pipeline.Brick
--
-- The base brick: a typed 2-cell in the substrate's three-axis
-- triangular witnessing structure (D = data, S = state, C = compute,
-- with six oriented morphisms among D/S/C each witnessed by the
-- third). File-per-lemma:
--
--   Brick.Witnessing      — the 6 oriented morphisms
--   Brick.Axis            — the 3 sort tags (𝔻 / 𝕊 / ℂ)
--   Brick.WitnessAxis     — Witnessing → Axis mapping
--   Brick.Type            — BrickType signature (4 typed edges)
--   Brick.Unit            — local ⊤ for trivial edges
--   Brick.Record          — Brick record (the main type)
--   Brick.PureBrick       — PureBrick + lifts into Brick
--   Brick.EdgeAccessors   — D-in-of / D-out-of / S-in-of / S-out-of
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick where

open import Substrate.Pipeline.Brick.Witnessing
open import Substrate.Pipeline.Brick.Axis
open import Substrate.Pipeline.Brick.WitnessAxis
open import Substrate.Pipeline.Brick.Type
open import Substrate.Pipeline.Brick.Unit
open import Substrate.Pipeline.Brick.Record
open import Substrate.Pipeline.Brick.PureBrick
open import Substrate.Pipeline.Brick.EdgeAccessors