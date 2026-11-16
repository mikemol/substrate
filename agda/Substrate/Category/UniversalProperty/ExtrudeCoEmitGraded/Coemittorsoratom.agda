------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittorsoratom
--
-- Defines: coemit-torsor-atom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittorsoratom where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4fixunit
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- coemit's V₄ AS Lawvere's TorsorAtom: the anchor e is the ONLY element with a fixed point (the anchor law).
coemit-torsor-atom : TorsorAtom V4.V4Full
coemit-torsor-atom = record { _∙_ = V4._·_ ; e = V4.e ; fix→unit = v4-fix→unit }
