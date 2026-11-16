------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuleast
--
-- Defines: coemit-mu-least
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuleast where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCarrier
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmucarrier
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the LEAST fixed point of the composition-carrier: every trace-mul product collapses to zero-trace (the ~-least
-- element, μ). So μ(carrier) ~ zero-trace — the least fixed point of the composition is the collapsed/finite point.
coemit-mu-least : (r s : RealTrace) → CoemitMuCarrier.carrier coemit-mu-carrier r s ~ zero-trace
coemit-mu-least = trace-mul-collapses
