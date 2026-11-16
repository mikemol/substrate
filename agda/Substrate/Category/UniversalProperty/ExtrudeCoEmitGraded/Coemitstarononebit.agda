------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstarononebit
--
-- Defines: coemit-star-on-one-bit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstarononebit where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flipinvolutive
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- coemit's one-bit totality-dual (the chirality flip) has FaceSet's ★ shape: dual = totality ⊕ self, ★★ = id.
coemit-star-on-one-bit : (b : F₂) → f2-flip (f2-flip b) ≡ b            -- 𝟙 ⊕ (𝟙 ⊕ b) ≡ b — the same engine
coemit-star-on-one-bit = f2-flip-involutive
