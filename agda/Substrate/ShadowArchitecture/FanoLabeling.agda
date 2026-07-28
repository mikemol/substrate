------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.FanoLabeling
--
-- Slice 1.1 of the shadow-architecture arc per
-- `scratch/shadow_architecture_agda_arc_plan.md`.
--
-- The shadow-architecture document (`scratch/shadow-architecture.md`)
-- names Fano points by their F₂³ bit-patterns (100, 010, 001, 110,
-- 101, 011, 111) and Fano lines by a sequential index L₁..L₇. The
-- substrate's existing `Substrate.Algebra.F2.FanoPlane` names points
-- by basis-sum signatures (e₁, e₂, e₃, e₁₂, e₁₃, e₂₃, e₁₂₃) and
-- lines by point-pair signatures (L₁₂, L₁₃, L₂₃, L₁-₂₃, L₂-₁₃,
-- L₃-₁₂, L₁₂-₁₃).
--
-- This file installs pattern-synonym aliases so the document's naming
-- can be used directly in subsequent slices without re-deriving the
-- mapping. Pattern synonyms are bidirectional, so `p₁₁₀` and `e₁₂`
-- are interchangeable in both expressions and patterns.
--
-- Mapping (point: bit-pattern ↔ substrate name):
--   100 = e₁     (basis 0)
--   010 = e₂     (basis 1)
--   001 = e₃     (basis 2)
--   110 = e₁₂    (basis 0 + basis 1)
--   101 = e₁₃    (basis 0 + basis 2)
--   011 = e₂₃   (basis 1 + basis 2)
--   111 = e₁₂₃  (basis 0 + basis 1 + basis 2)
--
-- Mapping (line: document index ↔ substrate name ↔ point triple):
--   L₁ = L₁₂     = {100, 010, 110}  — "positive-closure"
--   L₂ = L₁₃     = {100, 001, 101}  — "GS-guard-coverage"
--   L₃ = L₂₃    = {010, 001, 011}  — "SA-guard-coverage"
--   L₄ = L₁-₂₃  = {100, 011, 111}  — "GS-triadic-completion"
--   L₅ = L₂-₁₃  = {010, 101, 111}  — "SA-triadic-completion"
--   L₆ = L₃-₁₂  = {001, 110, 111}  — "guard-reconstitution"   ★
--   L₇ = L₁₂-₁₃ = {110, 101, 011}  — "pure-composite-diagonal" ★
--
-- The two ★ lines (L₆, L₇) are load-bearing for the architecture and
-- are surfaced as named facts in `Substrate.ShadowArchitecture.SelfReference`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.FanoLabeling where

open import Substrate.Algebra.F2.FanoPlane
  using (Point; FanoLine;
         e₁; e₂; e₃; e₁₂; e₁₃; e₂₃; e₁₂₃;
         L₁₂; L₁₃; L₂₃; L₁-₂₃; L₂-₁₃; L₃-₁₂; L₁₂-₁₃;
         point-to-vec; line-points)

------------------------------------------------------------------------
-- Bit-pattern point aliases.
--
-- Three-digit binary form: pₐᵦc where (a,b,c) ∈ {0,1}³, with the
-- substrate's basis ordering (a = bit 0 = e₁-coordinate).
------------------------------------------------------------------------

pattern p₁₀₀ = e₁
pattern p₀₁₀ = e₂
pattern p₀₀₁ = e₃
pattern p₁₁₀ = e₁₂
pattern p₁₀₁ = e₁₃
pattern p₀₁₁ = e₂₃
pattern p₁₁₁ = e₁₂₃

------------------------------------------------------------------------
-- Sequential line aliases (document's L₁..L₇).
------------------------------------------------------------------------

pattern L₁ = L₁₂
pattern L₂ = L₁₃
pattern L₃ = L₂₃
pattern L₄ = L₁-₂₃
pattern L₅ = L₂-₁₃
pattern L₆ = L₃-₁₂
pattern L₇ = L₁₂-₁₃
