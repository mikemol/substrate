------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4elementsareinvolutions
--
-- Defines: coemit-v4-elements-are-involutions
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4elementsareinvolutions where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- V₄'s three non-identity elements are GROUP ELEMENTS (not axes): each an involution in V4Full (the kernel).
coemit-v4-elements-are-involutions : (V4._·_ V4.rowSwap-gen V4.rowSwap-gen ≡ V4.e)
                                   × ((V4._·_ V4.recip-gen V4.recip-gen ≡ V4.e)
                                   × (V4._·_ V4.klein V4.klein ≡ V4.e))
coemit-v4-elements-are-involutions = V4.rowSwap-invol , (V4.recip-invol , V4.klein-invol)
