------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.Stab
--
-- Stab predicate: σ fixes a given axis. Parametric in Axis — the
-- per-axis aliases (Stab-D, Stab-C, Stab-S, Stab-W) are gone, having
-- been pre-generator orbit-cataloguing artifacts. Callers use
-- `Stab X σ` directly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.Stab where


open import Substrate.Axes.Axis using (Axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Foundation.Eq

Stab : Axis → Permutation → Set
Stab X σ = apply σ X ≡ X
