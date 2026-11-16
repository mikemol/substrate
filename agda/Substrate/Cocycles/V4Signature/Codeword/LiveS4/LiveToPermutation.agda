------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4.LiveToPermutation
--
-- Defines: live-to-permutation
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.V4Signature.Codeword.LiveS4; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4.LiveToPermutation where

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
