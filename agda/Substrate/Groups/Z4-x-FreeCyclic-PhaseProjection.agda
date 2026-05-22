------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection
--
-- The phase projection from the 2-D word algebra Z₄ × ℕ back to Z₄.
--
-- Mirror of Z3-x-FreeCyclic-PhaseProjection at n=4. `phase-project =
-- proj₁` with the Coxeter Core homomorphism lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection where

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.Z4-x-FreeCyclic as Z₄×F
open import Substrate.Groups.Coxeter.Word using (Word)

------------------------------------------------------------------------
-- N-1: phase-project — extract the Z₄ phase from a Z₄ × ℕ word.
------------------------------------------------------------------------

phase-project : Z₄×F.Word → Word Z₄.Gen
phase-project = proj₁

------------------------------------------------------------------------
-- N-2 / N-3 / N-4: Coxeter Core homomorphism witnesses.
------------------------------------------------------------------------

phase-project-ε : phase-project Z₄×F.ε ≡ Z₄.ε
phase-project-ε = refl

phase-project-· :
  (a b : Z₄×F.Word) →
  phase-project (a Z₄×F.· b) ≡ phase-project a Z₄.· phase-project b
phase-project-· (a₁ , a₂) (b₁ , b₂) = refl

phase-project-normalize :
  (w : Z₄×F.Word) →
  phase-project (Z₄×F.normalize w) ≡ Z₄.normalize (phase-project w)
phase-project-normalize (w₁ , w₂) = refl

------------------------------------------------------------------------
-- N-5: Capstone — phase-projection at Z₄ lands.
--
-- Mechanical mirror of Z3-x-FreeCyclic-PhaseProjection. The structure
-- generalizes uniformly across n; each new instance is one ~30-line
-- file via the DirectProduct + projection pattern.
------------------------------------------------------------------------
