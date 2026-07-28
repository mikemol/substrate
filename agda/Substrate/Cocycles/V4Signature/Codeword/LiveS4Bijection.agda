------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection
--
-- Slice 11d: bundles Live ↔ Permutation as a constructive bijection.
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 489-line module is now a thin re-export shim over four
-- submodules in LiveS4Bijection/.
--
-- Submodule decomposition:
--   LiveS4Bijection.Roundtrips  — axis-selector-roundtrip (24 refls),
--                                  axis-selector-roundtrip-cw (24+1),
--                                  live-perm-axis-sel (24 refls),
--                                  stab-from-selector-eq-orbit (16),
--                                  stab-from-selector-fixes-D (6),
--                                  stab-roundtrip.
--   LiveS4Bijection.Anchor      — selector-to-orbit-key +
--                                  stab-from-selector-anchor + fixers.
--   LiveS4Bijection.Forward     — σ-live-σ-roundtrip.
--   LiveS4Bijection.Reverse     — selector-from-stab-resp-≈,
--                                  s-for-of-live-perm-≈,
--                                  live-σ-live-roundtrip.
--
-- The bundled Live≃Permutation record is defined here over the
-- re-exported submodules.
--
-- Custom record bundling: stdlib's _↔_ wants _≡_ on both sides;
-- Permutation has _≈_ pointwise and Live's Σ-type wraps a ¬-component
-- whose propositional equality needs funext. So we use codeword-level
-- _≡_ on the Live side and _≈_ on the Permutation side.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection where

open import Substrate.Foundation.Product using (proj₁)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Axes.Axis using (Axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Cocycles.V4Signature.Codeword using (Live)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4
  using (live-to-permutation)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso
  using (permutation-to-live)

open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Roundtrips
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Anchor
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Forward
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Reverse
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
------------------------------------------------------------------------
-- The bundled bijection.
------------------------------------------------------------------------

record Live≃Permutation : Set where
  field
    to       : Live → Permutation
    from     : Permutation → Live
    to-from  : (σ : Permutation) → to (from σ) ≈ σ
    from-to  : (lv : Live) → proj₁ (from (to lv)) ≡ proj₁ lv

Live≃Permutation-bijection : Live≃Permutation
Live≃Permutation-bijection = record
  { to      = live-to-permutation
  ; from    = permutation-to-live
  ; to-from = σ-live-σ-roundtrip
  ; from-to = live-σ-live-roundtrip
  }
