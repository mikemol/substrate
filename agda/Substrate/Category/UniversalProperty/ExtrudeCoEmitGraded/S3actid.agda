------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actid
--
-- Defines: s3-act-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actid where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfiniso
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (2) coemit-s3-group-laws: s3-on-axis is a genuine G-ACTION (the graded stencil's action groupoid). Identity acts
--     trivially; composition of permutations composes the action. Objects = axes, morphisms = S₃ elements = a groupoid.
s3-act-id : (a : GradingAxis) → s3-on-axis (λ x → x) a ≡ a
s3-act-id = axis-fin-iso
