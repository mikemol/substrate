{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianLiteral2 — ◆jac-gamma, literal₂ in its OWN file.
--
-- literal₂ : (x y z : ℚ) → evalℚ x y z R.f₂ ≋ C.f₂ x y z
--
-- Lemma-per-file: the per-module memory cap is a FORCING FUNCTION for proof
-- complexity. f₂ has no (1+xy)³ cube, so `γ₂ = homAgree e₂` stays light (~94 MB);
-- one file per literal NAMES that, instead of a 3-lemma aggregate.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianLiteral2 where

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (≈ℚ-trans)

import Substrate.Algebra.Z.JacobianResidue as R
open import Substrate.Algebra.Q.JacobianEncodingGen
open import Substrate.Algebra.Q.JacobianEncodingHom
open import Substrate.Algebra.Q.JacobianEvalNormalize using (evalBridge₂)
open import Substrate.Algebra.Q.JacobianEncodingNormalize using (Cᴹf₂)
import Substrate.Algebra.Q.JacobianCollision as C
open import Substrate.Algebra.Q.JacobianExpr using (e₂)

module _ (x y z : ℚ) where
  open Point  x y z
  open Point2 x y z

  γ₂ : E Cᴹf₂ ≋ C.f₂ x y z
  γ₂ = homAgree e₂

  literal₂ : E R.f₂ ≋ C.f₂ x y z
  literal₂ = ≈ℚ-trans {E R.f₂} {E Cᴹf₂} {C.f₂ x y z} (evalBridge₂ x y z) γ₂
