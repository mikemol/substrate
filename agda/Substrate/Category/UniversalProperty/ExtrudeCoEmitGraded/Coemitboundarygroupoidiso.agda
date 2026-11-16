------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitboundarygroupoidiso
--
-- Defines: coemit-boundary-groupoid-iso
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitboundarygroupoidiso where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (1) coemit-boundary-groupoid-iso: the frame-groupoid iso connecting the boundaries is the PERSPECTIVE-PERMUTATION
--     — s3-reaches gives, for the μ-axis (finite prefixes) and any other leg, the permutation witnessing they are
--     "the same finite from a different perspective". The iso IS the S₃-reachability (higher-order finite), not a
--     carrier ≡. Witness: the μν-axis reaches every axis (the finite-prefix perspective generates all).
coemit-boundary-groupoid-iso : (b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ μν-axis ≡ b)
coemit-boundary-groupoid-iso = s3-reaches μν-axis
