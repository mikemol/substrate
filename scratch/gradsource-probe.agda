-- ⟡graded-source-probe: does detJac have a graded source (the Leibniz/S₃ grade)?
-- WITNESS: the grade-0 fiber (constant coefficient) of detJac IS the Leibniz
-- determinant `LeibnizDet.det {3}` of the constant-part Jacobian matrix, over ℤ
-- (NO Semiring MPoly needed — the constant term of a determinant is the
-- determinant of the constant-term matrix, and that lives in ℤ).
{-# OPTIONS --safe --without-K --guardedness #-}

module gradsource-probe where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Semiring.Instances.Z using (ℤ-semiring; mul-sign-computes)
import Substrate.WitnessTower.LeibnizDet as LD
import Substrate.Algebra.Z.JacobianResidue as JR

open LD.Det ℤ ℤ-semiring using (Mat)
open LD.Det.WithSign ℤ ℤ-semiring (-suc 0) mul-sign-computes using (det)

-- The constant part (at the origin) of Jac F, verified from f₁/f₂/f₃:
--   ∂F/∂(x,y,z) at (0,0,0) = [[0,0,1],[0,1,0],[2,0,0]]   (row-major flat Fin 9).
JacConst : Mat 3
JacConst zero                                     = + 0
JacConst (suc zero)                               = + 0
JacConst (suc (suc zero))                         = + 1
JacConst (suc (suc (suc zero)))                   = + 0
JacConst (suc (suc (suc (suc zero))))             = + 1
JacConst (suc (suc (suc (suc (suc zero)))))       = + 0
JacConst (suc (suc (suc (suc (suc (suc zero)))))) = + 2
JacConst (suc (suc (suc (suc (suc (suc (suc zero))))))) = + 0
JacConst (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))) = + 0

-- det {3} JacConst = −2 (the (0 2)-transposition: 1·1·2, odd sign).
det-JacConst : det {3} JacConst ≡ -suc 1
det-JacConst = refl

-- THE PROBE: detJac's grade-0 fiber (its constant coefficient) IS the Leibniz
-- determinant of the constant-part Jacobian. So the graded source EXISTS and is
-- the S₃/Leibniz sign grade — machine-checked at grade 0.
graded-source-at-0 : det {3} JacConst ≡ JR.coeff (JR.mono 0 0 0) JR.detJac
graded-source-at-0 = refl
