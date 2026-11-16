------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4.ExampleDFixed
--
-- Defines: example-σD-fixed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.V4Signature.Codeword.LiveS4; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4.ExampleDFixed where

open import Substrate.Foundation.Product
open import Substrate.Axes.Axis
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Cocycles.V4Signature.S4Iso.StabElements
open import Substrate.Groups.V4-Embedding
open import Substrate.Groups.SemidirectProduct
open import Substrate.Cocycles.V4Signature.S4Iso
open import Substrate.Cocycles.V4Signature.Codeword
open import Substrate.Cocycles.V4Signature.Codeword.Live
open import Substrate.Groups.Symmetric.Permutation.Compose Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Groups.Symmetric.Identity Axis
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4.StabFromSelector
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4.LiveToPermutation
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4.Private


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
