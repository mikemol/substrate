------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitanchorfixedcanonically
--
-- Defines: coemit-anchor-fixed-canonically
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitanchorfixedcanonically where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
open import Substrate.Axes.Axis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkey
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeytostab
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the ANCHOR D is FIXED by every Stab(D)-representative — the CANONICAL witness of D-fixed-point-is-anchor (344).
coemit-anchor-fixed-canonically : (k : coemit-orbitkey) → Stab D (coemit-orbitkey-to-stab k)
coemit-anchor-fixed-canonically = orbit-key-to-stab-d-fixes-D
