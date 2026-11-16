------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4.StabFromSelector
--
-- Defines: stab-from-selector
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.V4Signature.Codeword.LiveS4; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4.StabFromSelector where

open import Substrate.Axes.Axis
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Cocycles.V4Signature.S4Iso.StabElements
open import Substrate.Cocycles.V4Signature.S4Iso
open import Substrate.Cocycles.V4Signature.Codeword.Live
open import Substrate.Groups.Symmetric.Permutation.Compose Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Groups.Symmetric.Identity Axis
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq



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
