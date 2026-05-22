------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection
--
-- The phase projection from the 2-D word algebra Z₃ × ℕ back to Z₃.
--
-- Concretely: `phase-project (w-phase, w-cycle) = w-phase`. This is
-- `proj₁` on the underlying pair, with structural lemmas showing
-- it's a Coxeter Core homomorphism (preserves _·_, ε, normalize).
--
-- The phase-projection IS the cover map: the 2-D structure has a
-- universal-cover flavor where the phase axis (Z/3) is the quotient
-- and the cycle axis (ℕ) is the cover. Forgetting cycle = projecting
-- onto Z/3.
--
-- Per the 2-D word algebra arc: this is the operational realization
-- of "forget cycle, recover Z/n." For Z₃ specifically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection where

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.Z3-x-FreeCyclic as Z₃×F
open import Substrate.Groups.Coxeter.Word using (Word)

------------------------------------------------------------------------
-- N-1: phase-project — extract the Z₃ phase from a Z₃ × ℕ word.
------------------------------------------------------------------------

phase-project : Z₃×F.Word → Word Z₃.Gen
phase-project = proj₁

------------------------------------------------------------------------
-- N-2: phase-project preserves the identity ε.
--
-- ε in Z₃-x-FreeCyclic is (ε_Z₃, ε_F). Projecting gives ε_Z₃.
------------------------------------------------------------------------

phase-project-ε : phase-project Z₃×F.ε ≡ Z₃.ε
phase-project-ε = refl

------------------------------------------------------------------------
-- N-3: phase-project preserves _·_ (homomorphism property).
--
-- In Z₃-x-FreeCyclic, (a₁ , a₂) · (b₁ , b₂) = normalize ((a₁ , a₂)
-- ++ (b₁ , b₂)) = (normalize (a₁ ++ b₁), normalize (a₂ ++ b₂))
--                = (a₁ ·_Z₃ b₁, a₂ ·_F b₂).
-- Projecting: phase-project (a · b) = a₁ ·_Z₃ b₁ = phase-project a
--                                                 ·_Z₃ phase-project b.
------------------------------------------------------------------------

phase-project-· :
  (a b : Z₃×F.Word) →
  phase-project (a Z₃×F.· b) ≡ phase-project a Z₃.· phase-project b
phase-project-· (a₁ , a₂) (b₁ , b₂) = refl

------------------------------------------------------------------------
-- N-4: phase-project commutes with normalize.
--
-- The lift from "underlying Word equality" to "Canonical form
-- equality" via the projection. Used downstream for showing
-- phase-project of a normalized 2-D word equals the normalized
-- Z₃ projection.
------------------------------------------------------------------------

phase-project-normalize :
  (w : Z₃×F.Word) →
  phase-project (Z₃×F.normalize w) ≡ Z₃.normalize (phase-project w)
phase-project-normalize (w₁ , w₂) = refl

------------------------------------------------------------------------
-- N-5: Capstone — phase-projection lands at Z₃.
--
-- After this slice:
--
--   * phase-project : Z₃×F.Word → Z₃.Word
--     (the cover map "forget cycle counter")
--   * phase-project-ε : preserves identity
--   * phase-project-· : preserves product (Coxeter homomorphism)
--   * phase-project-normalize : commutes with normalize
--
-- Together these witness that phase-project IS a Coxeter Core
-- homomorphism Z₃-x-FreeCyclic → Z₃. The kernel is the FreeCyclic
-- component (= the deck transformation group of the cover).
--
-- Per [[project-graded-bicategorical-arc]]: at the strict 2-monoid
-- level, phase-project is a strict monoid morphism on the 1-cells
-- and respects the _≈_ 2-cell structure (the normalize commutativity).
------------------------------------------------------------------------
