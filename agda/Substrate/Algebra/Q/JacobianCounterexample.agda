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
-- ⚑ HONEST BOUNDARY. The two halves are about the SAME paper map F but use
-- two independent encodings — HALF A's curried ℚ functions `C.f₁/f₂/f₃` and
-- HALF B's `MPoly` `detJac` (of `Algebra.Z.JacobianResidue`'s `f₁/f₂/f₃`).
-- They are conjoined BY CONSTRUCTION (identical monomial structure, by
-- inspection), NOT by a machine-checked bridge: a term equating the ℚ-eval of
-- the `MPoly` F with the curried ℚ F is the one rung not present. So this
-- capstone states "this ℚ F is non-injective AND this ℤ F has det ≡ −2",
-- true of the one map, without a single-object identification.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianCounterexample where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; -suc_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
import Substrate.Algebra.Q.JacobianCollision as C
import Substrate.Algebra.Z.JacobianResidue   as R
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)

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

jac-counterexample : IsJacobianCounterexample
jac-counterexample = record
  { collide₁          = C.collision₁
  ; collide₂          = C.collision₂
  ; collide₃          = C.collision₃
  ; distinct          = C.x-differs
  ; det-is-const-neg2 = norm-detJac-is-const
  }
