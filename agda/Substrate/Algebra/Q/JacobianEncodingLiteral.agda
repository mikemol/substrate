{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingLiteral — ◆jac-gamma, THE LITERAL CLOSE.
--
-- Closes the ⟡jac-encoding-bridge single-object identification at the LITERAL
-- ℚ-function level:
--
--     literalᵢ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≋ C.fᵢ x y z
--
-- HALF A's curried-ℚ `C.fᵢ` (JacobianCollision) and HALF B's MPoly `R.fᵢ`
-- (JacobianResidue) are the SAME paper map F, WHEN EVALUATED at any point.
--
-- ⚑ THE METHOD — a FREE-ALGEBRA UNIVERSAL-PROPERTY LIFT (`homAgree`, in
-- `JacobianEncodingHom.Point2`). This module holds ONLY the C-specific degree-9
-- INSTANTIATIONS: `eᵢ` mirrors C's grouping, so `encode eᵢ` reduces to `Cᴹfᵢ` and
-- the direct eval to `C.fᵢ x y z` (both refl); `γᵢ = homAgree eᵢ`. Those heavy
-- uses are kept HERE, off the reusable generator/hom layers, so a cheap consumer
-- (e.g. the det literal) does not pay their ~40× deserialization tax
-- (def/proof-separation memory mechanism).
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingLiteral where

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (≈ℚ-trans)

import Substrate.Algebra.Z.JacobianResidue as R

-- The generator layer (E / _≋_ / Point) and the hom engine (Point2.homAgree).
open import Substrate.Algebra.Q.JacobianEncodingGen
open import Substrate.Algebra.Q.JacobianEncodingHom

open import Substrate.Algebra.Q.JacobianEvalNormalize
  using (evalBridge₁; evalBridge₂; evalBridge₃)
open import Substrate.Algebra.Q.JacobianEncodingNormalize using (Cᴹf₁; Cᴹf₂; Cᴹf₃)
import Substrate.Algebra.Q.JacobianCollision as C

open import Substrate.Algebra.Q.JacobianExpr using (e₁; e₂; e₃)

module _ (x y z : ℚ) where

  open Point  x y z    -- E / _≋_-usable E-values
  open Point2 x y z    -- homAgree

  ----------------------------------------------------------------------
  -- γ (evalℚ Cᴹfᵢ ≋ C.fᵢ) BY UNIQUENESS, then the LITERAL close.
  --   `encode eᵢ` reduces to `Cᴹfᵢ` and `evalDirect eᵢ` to `C.fᵢ x y z`,
  --   both by refl, so `γᵢ = homAgree eᵢ`.
  ----------------------------------------------------------------------

  γ₁ : E Cᴹf₁ ≋ C.f₁ x y z
  γ₁ = homAgree e₁
  γ₂ : E Cᴹf₂ ≋ C.f₂ x y z
  γ₂ = homAgree e₂
  γ₃ : E Cᴹf₃ ≋ C.f₃ x y z
  γ₃ = homAgree e₃

  literal₁ : E R.f₁ ≋ C.f₁ x y z
  literal₁ = ≈ℚ-trans {E R.f₁} {E Cᴹf₁} {C.f₁ x y z} (evalBridge₁ x y z) γ₁
  literal₂ : E R.f₂ ≋ C.f₂ x y z
  literal₂ = ≈ℚ-trans {E R.f₂} {E Cᴹf₂} {C.f₂ x y z} (evalBridge₂ x y z) γ₂
  literal₃ : E R.f₃ ≋ C.f₃ x y z
  literal₃ = ≈ℚ-trans {E R.f₃} {E Cᴹf₃} {C.f₃ x y z} (evalBridge₃ x y z) γ₃
