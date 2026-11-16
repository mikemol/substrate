------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdaggercanonical
--
-- Defines: coemit-dagger-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdaggercanonical where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.Wedge.Iso
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (2) coemit-isogroupoid: the canonical iso record is WedgeIso; IsoGroupoid supplies iso-sym = THE DAGGER †
--     and the pointwise _≈ʷ_ (ANOTHER totality construction: c ≈ʷ d = (x : C A) → translate (fwd c) x ≡ …).
--     Coemit's ~-groupoid is the same shape: its "pointwise" index is the STEP, and ~ is the totality (351).
------------------------------------------------------------------------

-- the dagger, canonically: IsoGroupoid's iso-sym on WedgeIso. (StarV4: "the groupoid's inverse iso-sym IS the †".)
coemit-dagger-canonical : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → WedgeIso A B → WedgeIso B A
coemit-dagger-canonical = iso-sym
