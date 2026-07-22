{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianLiteral3 — ◆jac-gamma, literal₃ in its OWN file.
--
-- literal₃ : (x y z : ℚ) → evalℚ x y z R.f₃ ≋ C.f₃ x y z
--
-- Lemma-per-file: the per-module memory cap is a FORCING FUNCTION for proof
-- complexity. f₃ likewise has no (1+xy)³ cube, so `γ₃ = homAgree e₃` stays light (~94 MB);
-- one file per literal NAMES that, instead of a 3-lemma aggregate.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianLiteral3 where

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (≈ℚ-trans)

import Substrate.Algebra.Z.JacobianResidue as R
open import Substrate.Algebra.Q.JacobianEncodingGen
open import Substrate.Algebra.Q.JacobianEncodingHom
open import Substrate.Algebra.Q.JacobianEvalNormalize using (evalBridge₃)
open import Substrate.Algebra.Q.JacobianEncodingNormalize using (Cᴹf₃)
import Substrate.Algebra.Q.JacobianCollision as C
open import Substrate.Algebra.Q.JacobianExpr using (e₃)

module _ (x y z : ℚ) where
  open Point  x y z
  open Point2 x y z

  γ₃ : E Cᴹf₃ ≋ C.f₃ x y z
  γ₃ = homAgree e₃

  literal₃ : E R.f₃ ≋ C.f₃ x y z
  literal₃ = ≈ℚ-trans {E R.f₃} {E Cᴹf₃} {C.f₃ x y z} (evalBridge₃ x y z) γ₃
