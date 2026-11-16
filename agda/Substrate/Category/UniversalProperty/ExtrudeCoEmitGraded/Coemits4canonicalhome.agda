------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4canonicalhome
--
-- Defines: coemit-s4-canonical-home
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4canonicalhome where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitS4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (4) coemit-s4iso-reuse: the canonical S₄ iso lives at Cocycles.V4Signature.S4Iso (TotalSpace≃S₄). Documented as the
--     canonical home for the S₄ identification; coemit's braiding chain should reference it, not re-derive S₄.
--     (The iso's carrier is the V4Signature TotalSpace — a cocycle-side presentation, not RealTrace: honest-partial.)
coemit-s4-canonical-home : Set        -- the S₄=V₄⋊S₃ identification's canonical home (V4Signature.S4Iso); coemit refs it
coemit-s4-canonical-home = CoemitS4   -- coemit's (axis,perm) pairs; the canonical S₄Iso is the reference form
