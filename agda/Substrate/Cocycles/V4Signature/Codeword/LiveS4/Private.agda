------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4.Private
--
-- Defines: --
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.V4Signature.Codeword.LiveS4; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4.Private where

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

-- The (axis=D, selector=sel-ftf) Live codeword gives
--   embed (v-of-axis D) · stab-from-selector sel-ftf
--     = embed e · stab-cs
-- Applied to D this is D, since v-of-axis D = e (identity on axes)
-- and stab-cs fixes D.
