------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
--
-- Defines: v-of-axis-anchor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.SemidirectProduct.V; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor where

open import Substrate.Axes.Axis
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4



------------------------------------------------------------------------
-- Anchor-parametric generator.
--
-- The D-anchored case is special-cased to `v-of-axis x` directly, so
-- `v-of-axis-anchor D x ≡ v-of-axis x` holds DEFINITIONALLY (not just
-- propositionally via ε-right). This is the structural fact that lets
-- the D-specialized callsites (the cocycle's anchor) use the
-- parametric form without cast.
------------------------------------------------------------------------

v-of-axis-anchor : Axis → Axis → V₄
v-of-axis-anchor D x = v-of-axis x
-- ⚑ Ⓠ7: `V4.·` → `V4.·₄`. The Klein-group operation was renamed at source
-- (Ⓠ6ᵉ, `_·_` → `_·₄_`), and `rename_at_source` did NOT rewrite this site:
-- it covers the four BARE spellings (declaration, infix, and both sections)
-- but not the QUALIFIED form `<alias>.name`. An aliased import is exactly the
-- shape that tool cannot see — the Ⓠ5 gap, from the other side.
v-of-axis-anchor X x = v-of-axis x V4.·₄ v-of-axis X
