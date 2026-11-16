------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmufixed
--
-- Defines: coemit-mu-fixed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmufixed where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-mu-unique: μ = the LEAST fixed point (zero-trace). It IS a fixed point of the carrier (trace-mul z z ~ z),
--     and it is LEAST: every trace-mul product collapses to it (∀ r s, trace-mul r s ~ z). So z is the unique (up to ~)
--     least fixed point of the composition-carrier — the initial/universal μ.
coemit-mu-fixed : trace-mul zero-trace zero-trace ~ zero-trace          -- z is a fixed point of the carrier
coemit-mu-fixed = trace-mul-collapses zero-trace zero-trace
