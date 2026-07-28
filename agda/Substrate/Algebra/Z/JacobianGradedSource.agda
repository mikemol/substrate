{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.JacobianGradedSource — ⟡graded-source-probe.
--
-- Q (the probe): does `JacobianResidue.detJac` have a GRADED SOURCE — is it an
-- instance of the S₃/Leibniz determinant, so its negation is structural (the
-- sign) rather than arbitrary? A (positive, machine-checked at the grade-0 fiber).
--
-- `detJac` is written by hand as the six-term S₃ Leibniz sum (three even +, three
-- odd carrying `kP (-suc 0)`; `JacobianResidue.agda:192-199` annotates each
-- summand with its permutation). That IS `WitnessTower.LeibnizDet.det {3}` of the
-- Jacobian matrix — the enumerate/encode/mono/sign/sum pipeline — so the S₃
-- Leibniz grade is the source, and the negation is ENTIRELY the μ₂ sign of S₃
-- (the tower's sign character; cf. `LeibnizDetPerm.det-sign-morphism`).
--
-- ⚑ THE WITNESS (grade-0, over ℤ — NO `Semiring MPoly` needed). The constant term
-- of a determinant is the determinant of the constant-term matrix, so the grade-0
-- fiber `coeff (mono 0 0 0) detJac` (= −2) equals `det {3}` of the constant-part
-- Jacobian `JacConst = ∂F/∂(x,y,z)|₍₀,₀,₀₎ = [[0,0,1],[0,1,0],[2,0,0]]` — a real
-- `Mat 3` over the PROVEN `ℤ-semiring`, with the μ₂ sign `ε₂ = -suc 0`
-- (`mul-sign-computes`). `graded-source-at-0` checks that identity by `refl`.
--
-- ⚑ HONEST BOUNDARY (the residue). This confirms the source at GRADE 0 only. The
-- full ∀-monomial identity `det {3} JacMat ≈ detJac` (over the whole degree box)
-- needs `Semiring MPoly` — the bespoke-`MPoly`-rebuild debt = ⟡jac-det-via-sppf's
-- N1 rung — and holds only up to `≈` (coeff-equality; `MPoly` is unnormalised, so
-- `det JacMat` is an unnormalised permutation of `detJac`'s terms). The probe
-- DECIDES: the arc lifts (⟡jac-neg-graded / ⟡jac-neg-cover), gated on `Semiring
-- MPoly`. Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.JacobianGradedSource where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Semiring.Instances.Z using (ℤ-semiring; mul-sign-computes)
import Substrate.WitnessTower.LeibnizDet as LD
import Substrate.Algebra.Z.JacobianResidue as JR

open LD.Det ℤ ℤ-semiring using (Mat)
open LD.Det.WithSign ℤ ℤ-semiring (-suc 0) mul-sign-computes using (det)

-- The constant part (at the origin) of Jac F, read from f₁/f₂/f₃:
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
