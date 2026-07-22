{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianCounterexample — ⟡jac-counterexample-capstone.
--
-- The two machine-checked halves of the Jacobian-conjecture counterexample
-- F(x,y,z) = ( z(1+xy)³ + y²(1+xy)(4+3xy)
--            , y + 3x(1+xy)²z + 3xy²(4+3xy)
--            , 2x − 3x²y − x³z )
-- conjoined into ONE discoverable statement `IsJacobianCounterexample`:
--
--   HALF A (NOT injective, over ℚ) — `Algebra.Q.JacobianCollision`: F sends
--     the two distinct points (0,0,−1/4) and (1,−3/2,13/2) to the same image
--     (−1/4,0,0). The `_≈ℚ_` (cross-multiplication) collisions + the
--     distinctness pole `x-differs`.
--   HALF B (det Jac F is the NONZERO CONSTANT −2, over ℤ) — the native
--     Leibniz determinant's normal form is the single term −2:
--     `normalize detJac ≡ kP (-suc 1)`. This is BOX-FREE — `normalize`
--     (RUNG 3a) enumerates the true support (combines like monomials, drops
--     zeros), so "det is the constant −2" needs no degree-bound argument.
--
-- ⚑ THE SINGLE-OBJECT IDENTIFICATION — NOW MACHINE-CHECKED (◆jac-gamma). The two
-- halves are about the SAME paper map F, under two independent encodings — HALF A's
-- curried ℚ functions `C.f₁/f₂/f₃` and HALF B's `MPoly` F (`Algebra.Z.JacobianResidue`'s
-- `f₁/f₂/f₃`, of which `detJac` is the determinant). These were previously conjoined
-- only BY INSPECTION (identical monomial structure); the rung equating the ℚ-eval of the
-- `MPoly` F with the curried ℚ F is now PRESENT: `JacobianEncodingLiteral.literal₁/₂/₃`
--    literalᵢ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z
-- (the ⟡jac-encoding-bridge Rosetta Stone, closed by a free-algebra universal-property
-- lift). So the `identify₁/₂/₃` fields below make the capstone a TRUE single-object
-- statement: this ℚ F IS the ℤ F, evaluated — one map, machine-checked end-to-end.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianCounterexample where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; -suc_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
import Substrate.Algebra.Q.JacobianCollision as C
import Substrate.Algebra.Z.JacobianResidue   as R
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
import Substrate.Algebra.Q.JacobianEvalNormalize as β
import Substrate.Algebra.Q.JacobianEncodingLiteral as L

-- HALF B, box-free: the determinant's full normal form is the constant −2.
norm-detJac-is-const : normalize R.detJac ≡ R.kP (-suc 1)
norm-detJac-is-const = refl

record IsJacobianCounterexample : Set where
  field
    -- HALF A — F(p) ≈ F(q) componentwise at two distinct points.
    collide₁ : C.f₁ 0ℚ 0ℚ C.-1/4ℚ ≈ℚ C.f₁ 1ℚ C.-3/2ℚ C.13/2ℚ
    collide₂ : C.f₂ 0ℚ 0ℚ C.-1/4ℚ ≈ℚ C.f₂ 1ℚ C.-3/2ℚ C.13/2ℚ
    collide₃ : C.f₃ 0ℚ 0ℚ C.-1/4ℚ ≈ℚ C.f₃ 1ℚ C.-3/2ℚ C.13/2ℚ
    distinct : (0ℚ ≈ℚ 1ℚ) → 0ℤ ≡ 1ℤ
    -- HALF B — det Jac F is the nonzero constant −2 (box-free).
    det-is-const-neg2 : normalize R.detJac ≡ R.kP (-suc 1)
    -- THE SINGLE-OBJECT IDENTIFICATION — HALF A's curried ℚ F IS HALF B's MPoly F,
    -- evaluated at every point (◆jac-gamma, JacobianEncodingLiteral.literalᵢ).
    identify₁ : (x y z : ℚ) → β.evalℚ x y z R.f₁ ≈ℚ C.f₁ x y z
    identify₂ : (x y z : ℚ) → β.evalℚ x y z R.f₂ ≈ℚ C.f₂ x y z
    identify₃ : (x y z : ℚ) → β.evalℚ x y z R.f₃ ≈ℚ C.f₃ x y z

jac-counterexample : IsJacobianCounterexample
jac-counterexample = record
  { collide₁          = C.collision₁
  ; collide₂          = C.collision₂
  ; collide₃          = C.collision₃
  ; distinct          = C.x-differs
  ; det-is-const-neg2 = norm-detJac-is-const
  ; identify₁         = L.literal₁
  ; identify₂         = L.literal₂
  ; identify₃         = L.literal₃
  }
