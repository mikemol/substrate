------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
--
-- Defines: s3-reaches
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap01
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap12
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- TRANSITIVITY: from any axis, some S₃ permutation reaches any target axis (the single orbit = higher-order finite).
s3-reaches : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
s3-reaches μν-axis        μν-axis        = (λ x → x) , refl
s3-reaches μν-axis        head-tail-axis = swap01 , refl
s3-reaches μν-axis        cyc-aper-axis  = swap12 ∘f swap01 , refl
  where _∘f_ : (Fin 3 → Fin 3) → (Fin 3 → Fin 3) → (Fin 3 → Fin 3)
        (f ∘f g) x = f (g x)
s3-reaches head-tail-axis μν-axis        = swap01 , refl
s3-reaches head-tail-axis head-tail-axis = (λ x → x) , refl
s3-reaches head-tail-axis cyc-aper-axis  = swap12 , refl
s3-reaches cyc-aper-axis  μν-axis        = swap01 ∘f swap12 , refl
  where _∘f_ : (Fin 3 → Fin 3) → (Fin 3 → Fin 3) → (Fin 3 → Fin 3)
        (f ∘f g) x = f (g x)
s3-reaches cyc-aper-axis  head-tail-axis = swap12 , refl
s3-reaches cyc-aper-axis  cyc-aper-axis  = (λ x → x) , refl
