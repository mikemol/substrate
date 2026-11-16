------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4mul
--
-- Defines: coemit-s4-mul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4mul where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitS4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the twisted product (the ⋊): (a,σ) ·⋊ (b,τ) = (a twisted-through-σ combined with b's image , σ∘τ). Here the V₄
-- combination is s3-on-axis (act φ) — the semidirect twist. (Full Group laws = SemidirectGroupObligation, honest-partial.)
coemit-s4-mul : CoemitS4 → CoemitS4 → CoemitS4
coemit-s4-mul (a , σ) (b , τ) = s3-on-axis σ b , (λ x → σ (τ x))   -- act φ σ b (the twist) , σ·τ
