{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingLiteral — ◆jac-gamma aggregator.
--
-- Seals the three literal closes
--
--     literalᵢ : Identifyᵢ   where   Identifyᵢ = (x y z : ℚ) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z
--
-- from the per-witness modules JacCubeNorm/JacobianLiteral2/3 (lemma-per-file). f₁'s
-- (1+xy)³ cube (the heavy one, `JacCubeNorm.identify₁`, a 128 MB reflective-normalizer
-- proof) is isolated off f₂/f₃ (~94/77 MB).
--
-- ⚑ ⟡cap128-jac-stage — the OrientationFin/OrderOf opaque-TYPE seal (cap384), applied to
-- ◆jac-gamma. Each `Identifyᵢ` is `opaque`, so the heavy work (reducing `evalℚ` over the
-- degree-9 cube f₁) happens ONCE, HERE, at the abstract boundary (~89 MB) — and a
-- downstream consumer that FIELDS `literalᵢ` sees a NON-REDUCING handle `: Identifyᵢ`,
-- so the record type-check is SYNTACTIC (cheap) instead of re-reducing the cube (which
-- busts the per-module cap). "Perform the heavy work abstractly, the reification is cheap":
-- the cube reduces behind the seal here, the capstone reifies the sealed handle for free.
-- (This module elaborates its three closes and seals them; it declares no data/record, so
-- the def/proof-separation gate does not fire.)
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingLiteral where

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
import Substrate.Algebra.Z.JacobianResidue        as R
import Substrate.Algebra.Q.JacobianEvalNormalize   as β
import Substrate.Algebra.Q.JacobianCollision       as C
import Substrate.Algebra.Q.JacCubeNorm             as JC1
import Substrate.Algebra.Q.JacobianLiteral2        as JL2
import Substrate.Algebra.Q.JacobianLiteral3        as JL3

opaque
  -- The three ◆jac-gamma statement TYPES, sealed: a consumer fields these as
  -- non-reducing handles, so `evalℚ … R.fᵢ` (the cube reduction for f₁) never
  -- re-fires at the reification site.
  Identify₁ Identify₂ Identify₃ : Set
  Identify₁ = (x y z : ℚ) → β.evalℚ x y z R.f₁ ≈ℚ C.f₁ x y z
  Identify₂ = (x y z : ℚ) → β.evalℚ x y z R.f₂ ≈ℚ C.f₂ x y z
  Identify₃ = (x y z : ℚ) → β.evalℚ x y z R.f₃ ≈ℚ C.f₃ x y z

  -- The closes, elaborated ONCE behind the seal (the heavy cube reduction is paid here).
  literal₁ : Identify₁
  literal₁ = JC1.identify₁
  literal₂ : Identify₂
  literal₂ = JL2.literal₂
  literal₃ : Identify₃
  literal₃ = JL3.literal₃
