------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCarrier
--
-- Defines: CoemitMuCarrier
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCarrier where

open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the strengthened μ-coalgebra: the carrier is trace-mul (the composition), and the coalgebra structure map takes a
-- trace to its head-observation (the differential, always 0) + the threaded tail (the composition acting) — a genuine
-- F-coalgebra step on the composition-carrier, NOT just the orbit-record of 336.
record CoemitMuCarrier : Set where
  field
    carrier   : RealTrace → RealTrace → RealTrace                 -- the COMPOSITION (RealTrace on RealTrace)
    diff-head : (r s : RealTrace) → RealTrace.head (carrier r s) ≡ 0        -- the coalgebraic morphism's head = the differential d
    thread    : (r s : RealTrace) → RealTrace.tail (carrier r s) ≡ carrier (RealTrace.tail r) (RealTrace.tail s)  -- RealTrace acting via the coalgebra
