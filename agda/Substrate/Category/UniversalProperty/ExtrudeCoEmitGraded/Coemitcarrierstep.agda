------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcarrierstep
--
-- Defines: coemit-carrier-step
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcarrierstep where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCoalgebra
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitacthomfull
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- REVISIT (post-compaction, operator re-supplies 335's reframe): the orbit is the COALGEBRA of the LEAST fixed
-- point μ of the CARRIER, and the CARRIER is the COMPOSITION — RealTrace acting on RealTrace via the coalgebraic
-- morphism = trace-mul (head=0 [the differential], tail = trace-mul of tails [threading via the coalgebra]).
-- AUDIT of 336: CoemitMuCoalgebra had project=perspective-finite + transition=s3-reaches, but the CARRIER trace-mul
-- was ONLY in coemit-act-hom-full — DISCONNECTED from the μ-object. Strengthen: weave trace-mul in AS the carrier.
------------------------------------------------------------------------
-- the composition-carrier step: RealTrace acting on RealTrace via the coalgebraic morphism (trace-mul is the action,
-- head=0 the differential, tail the threaded composition). This IS the carrier (the composition), not a single Φ_T step.
coemit-carrier-step : RealTrace → RealTrace → RealTrace
coemit-carrier-step = trace-mul
