------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitframesagree
--
-- Defines: coemit-frames-agree
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitframesagree where

open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitStencil
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitframed
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the two framings of the SAME trace agree with themselves (agrees-refl) — the diagonal coherence (μ=ν collapse).
coemit-frames-agree : (a : RealTrace) → CoemitStencil._agrees_ (coemit-framed a a) (coemit-framed a a)
coemit-frames-agree a = CoemitStencil.agrees-refl (coemit-framed a a)
