------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4
--
-- Slice 11b: Live → Permutation, constructed combinatorially from
-- the V_4 ⋊ Stab(D) ≅ S_4 primitives (slices 2, 3, 4, 9) rather
-- than by 24-case enumeration.
--
-- The insight: the 24 permutations of S_4 are NOT 24 independent
-- entities to be hand-listed; they ARE the orbit of (V_4, Stab(D))
-- under semidirect-product composition. By exposing the generator,
-- the structure constructs itself.
--
-- Reading 2 (this module): interpret the Live codeword's (axis,
-- selector) decomposition (slice 11a) as (v, s) ∈ V_4 × Stab(D)
-- where v = v-of-axis(axis) and s is the Stab(D) element identified
-- by the selector. Then σ = embed v · s ∈ S_4 by composition.
--
-- This complements slice 10's Reading 1 (Reserved ↔ Axis × Bool)
-- and slice 11a's structural decoding (Live ↔ Axis × Selector). Per
-- the multi-reading discipline ([[feedback-multi-reading-ambient-
-- discipline]]), neither reading is privileged: Reading 1 is for
-- Reserved, Reading 2 is for Live, both factor through the same
-- ambient Codeword.
--
-- See: catalog/cocycles.md § CY-5 "24 ARE S_4";
--      Substrate.Cocycles.V4Signature.Codeword (ambient);
--      Substrate.Cocycles.V4Signature.Codeword.Live (slice 11a).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4 where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Cocycles.V4Signature.S4Iso.StabElements

open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct
  using (v-of-axis)
open import Substrate.Cocycles.V4Signature.S4Iso
  using (stab-id; stab-sw; stab-cs; stab-cw; stab-csw; stab-cws)
open import Substrate.Cocycles.V4Signature.Codeword
  using (Live)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt;
         live-to-axis-selector)
open import Substrate.Groups.Symmetric.Permutation.Compose Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Groups.Symmetric.Identity Axis
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Axes.VOfAxis

------------------------------------------------------------------------
-- The 6-element selector ↔ Stab(D) bijection.
--
-- Each selector names one of the 6 Stab(D) elements defined in
-- Substrate.Cocycles.V4Signature.S4Iso (slice 4). The choice of
-- which selector names which element is a CONVENTION — multiple
-- bijections are valid; we pick one.
------------------------------------------------------------------------

stab-from-selector : Selector → Permutation
stab-from-selector sel-fft = stab-id
stab-from-selector sel-tft = stab-sw
stab-from-selector sel-ftf = stab-cs
stab-from-selector sel-ttf = stab-cw
stab-from-selector sel-ftt = stab-csw
stab-from-selector sel-ttt = stab-cws

------------------------------------------------------------------------
-- The main map: Live → Permutation.
--
-- Live ─decode→ (Axis × Selector)
--      ─v-of-axis × stab-from-selector→ (V_4 × Stab(D))
--      ─composition→ Permutation
--
-- No 24-case enumeration: the 24 permutations emerge from
-- 4 × 6 combinatorial composition of pre-existing primitives.
------------------------------------------------------------------------

live-to-permutation : Live → Permutation
live-to-permutation lv with live-to-axis-selector lv
... | a , sel = embed (v-of-axis a) · stab-from-selector sel

------------------------------------------------------------------------
-- Sanity checks: a few concrete cases.
--
-- These verify by `refl` that the combinatorial composition produces
-- specific named permutations on specific Live codewords. Useful as
-- regression checks and as documentation of the encoding.
------------------------------------------------------------------------

-- Reading the codeword (false, false, false, true, false) as Live:
--   IsReserved would require b₃ = b₄ = false. Here b₃ = true ≠ false,
--   so the proof needs ¬ IsReserved.

private
  -- The (axis=D, selector=sel-ftf) Live codeword gives
  --   embed (v-of-axis D) · stab-from-selector sel-ftf
  --     = embed e · stab-cs
  -- Applied to D this is D, since v-of-axis D = e (identity on axes)
  -- and stab-cs fixes D.
  example-σD-fixed :
    apply (embed (v-of-axis D) · stab-from-selector sel-ftf) D ≡ D
  example-σD-fixed = refl

------------------------------------------------------------------------
-- Notes
--
-- 1. The forward map live-to-permutation IS the catalog's "24 ARE
--    S_4" claim at the codeword layer, made constructive via
--    composition. The reverse map (Permutation → Live) and the
--    Iso bundling come in slice 11c.
--
-- 2. The combinatorial-construction approach replaces what would
--    have been 24 × ~12 = ~290 lines of explicit Permutation record
--    literals with 6 lines of stab-from-selector + 2 lines of
--    composition. The savings come from exposing the V_4 ⋊ Stab(D)
--    generator that S_4 already has.
--
-- 3. Cross-references:
--    - V_4 ⋊ S_3 ≅ S_4 factorisation: Substrate.Groups.SemidirectProduct
--      (slice 3) provides v-of-axis, v-for, s-for, and the
--      factorisation theorem.
--    - Stab(D) elements: Substrate.Cocycles.V4Signature.S4Iso (slice 4)
--      provides stab-id, stab-sw, stab-cs, stab-cw, stab-csw,
--      stab-cws.
--    - V_4 normality: Substrate.Groups.V4-Normality (slice 9) closes
--      the algebraic backbone making "embed v · s = S_4 element"
--      well-defined as a group iso.
------------------------------------------------------------------------
