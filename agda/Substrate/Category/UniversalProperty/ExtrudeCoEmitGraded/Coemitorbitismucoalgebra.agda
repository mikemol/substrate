------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitismucoalgebra
--
-- Defines: coemit-orbit-is-mu-coalgebra
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitismucoalgebra where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitacthomfull
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCarrier
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmucarrier
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the orbit is the COALGEBRA on this carrier: s3-reaches (the orbit) connects the finite projections, and the carrier
-- (trace-mul) is what the coalgebra acts by — associatively (coemit-act-hom-full). Together: the orbit coalgebra of μ.
coemit-orbit-is-mu-coalgebra : (r s t : RealTrace)
  → CoemitMuCarrier.carrier coemit-mu-carrier (CoemitMuCarrier.carrier coemit-mu-carrier r s) t
    ~ CoemitMuCarrier.carrier coemit-mu-carrier r (CoemitMuCarrier.carrier coemit-mu-carrier s t)
coemit-orbit-is-mu-coalgebra = coemit-act-hom-full
