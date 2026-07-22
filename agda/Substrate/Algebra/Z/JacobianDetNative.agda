{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.JacobianDetNative — ⟡jac-det-native (RUNG 3c).
--
-- The counterexample's determinant, computed by the NATIVE Leibniz-over-S₃
-- determinant `WitnessTower.LeibnizDet.Det.WithSign.det` over the polynomial
-- Semiring `NormPoly` (RUNG 3b) — replacing the hand-written six-term S₃
-- Leibniz sum `JacobianResidue.detJac`. The final theorem is that the two
-- agree coefficient-by-coefficient: the machine's determinant IS the
-- hand-written one.
------------------------------------------------------------------------

module Substrate.Algebra.Z.JacobianDetNative where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (proj₁; _,_)
open import Substrate.Algebra.Z using (ℤ)
open import Substrate.Algebra.Z.JacobianResidue
  using (∂x; ∂y; ∂z; f₁; f₂; f₃; detJac; coeff; MPoly; Mono)
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Z.MPolyNormalize.Properties using (coeff-normalize; normalize-sorted)
open import Substrate.Algebra.Z.MPolySemiring using (NormPoly; NormPoly-Semiring; ε₂; ε₂-sq)
open import Substrate.WitnessTower.LeibnizDet using (module Det)

open Det NormPoly NormPoly-Semiring using (Mat)
open Det.WithSign NormPoly NormPoly-Semiring ε₂ ε₂-sq using (det)

-- Set₀ packaging glue (3b named its Σ-constructor differently).
mkN : MPoly → NormPoly
mkN p = (normalize p , normalize-sorted p)

coeffN : Mono → NormPoly → ℤ
coeffN j q = coeff j (proj₁ q)

------------------------------------------------------------------------
-- JacMat : Mat 3 = Fin 9 → NormPoly, flat = component*3 + variable.
-- Entry (row fᵢ, col v) = the normalized existing derivative ∂v fᵢ.
------------------------------------------------------------------------

JacMat : Mat 3
JacMat zero                                                 = mkN (∂x f₁)
JacMat (suc zero)                                           = mkN (∂y f₁)
JacMat (suc (suc zero))                                     = mkN (∂z f₁)
JacMat (suc (suc (suc zero)))                               = mkN (∂x f₂)
JacMat (suc (suc (suc (suc zero))))                         = mkN (∂y f₂)
JacMat (suc (suc (suc (suc (suc zero)))))                   = mkN (∂z f₂)
JacMat (suc (suc (suc (suc (suc (suc zero))))))             = mkN (∂x f₃)
JacMat (suc (suc (suc (suc (suc (suc (suc zero)))))))       = mkN (∂y f₃)
JacMat (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))) = mkN (∂z f₃)

detNative : NormPoly
detNative = det {3} JacMat

------------------------------------------------------------------------
-- The theorem: the native determinant agrees with the hand-written one at
-- every monomial. The determinant's normal form is unique, so the native
-- computation's sorted result IS `normalize detJac`.
------------------------------------------------------------------------

detNative-normal : proj₁ detNative ≡ normalize detJac
detNative-normal = refl

det-native-correct : (j : Mono) → coeffN j detNative ≡ coeff j detJac
det-native-correct j =
  trans (cong (coeff j) detNative-normal) (coeff-normalize j detJac)
