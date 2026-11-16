{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingBridge — ⟡jac-encoding-bridge.
--
-- THE SINGLE-OBJECT IDENTIFICATION the capstone flagged as open:
--   bridge₁/₂/₃ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z.
-- HALF A's curried-ℚ `C.fᵢ` and HALF B's `MPoly` `R.fᵢ` are the SAME map. The
-- evaluator + homomorphism machinery lives in `Algebra.Q.JacobianEncoding`
-- (module `Ev`); this module walks each component's `+P`/`*P` skeleton against
-- the generator values. Split off from the shared eval to keep each module's
-- typecheck under the full-build heap cap (the distributed polynomials are heavy).
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingBridge where

open import Substrate.Algebra.Q.JacobianEncoding
open import Substrate.Algebra.Z using (+_; -suc_)
open import Substrate.Algebra.Q using (ℚ; 1ℚ)
open import Substrate.Algebra.Q.Neg using (-ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)
open import Substrate.Algebra.Q.Properties.Field using (*ℚ-assoc)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)

import Substrate.Algebra.Z.JacobianResidue as R
open R using (_*P_; _+P_)
import Substrate.Algebra.Q.JacobianCollision as C

module _ (x y z : ℚ) where

  open Ev x y z

  ----------------------------------------------------------------------
  -- 4.5 THE BRIDGES.  evalℚ R.fᵢ ≈ℚ C.fᵢ x y z.
  ----------------------------------------------------------------------

  bridge₁ : evalℚ R.f₁ ≈ℚ C.f₁ x y z
  bridge₁ = ≈ℚ-trans (evalℚ-++ (R.Z₁ *P R.u *P R.u *P R.u) (R.Y *P R.Y *P R.u *P R.v)) (≈ℚ-trans (+ℚ-cong (eval-*P4 R.Z₁ R.u R.u R.u) (eval-*P4 R.Y R.Y R.u R.v)) (≈ℚ-trans (+ℚ-cong (*ℚ-cong (*ℚ-cong (*ℚ-cong gen-Z gen-u) gen-u) gen-u) (*ℚ-cong (*ℚ-cong (*ℚ-cong gen-Y gen-Y) gen-u) gen-v)) (+ℚ-cong (assoc-lll z U U U) (≈ℚ-refl (((y · y) · U) · V)))))
    where
      U : ℚ
      U = 1ℚ ⊹ (x · y)
      V : ℚ
      V = (ℤ→ℚ (+ 4)) ⊹ ((ℤ→ℚ (+ 3)) · (x · y))

  bridge₂ : evalℚ R.f₂ ≈ℚ C.f₂ x y z
  bridge₂ = ≈ℚ-trans (evalℚ-++ (R.Y +P (R.kP (+ 3) *P R.X *P R.u *P R.u *P R.Z₁)) (R.kP (+ 3) *P R.X *P R.Y *P R.Y *P R.v)) (≈ℚ-trans (+ℚ-cong (evalℚ-++ R.Y (R.kP (+ 3) *P R.X *P R.u *P R.u *P R.Z₁)) (≈ℚ-refl (evalℚ (R.kP (+ 3) *P R.X *P R.Y *P R.Y *P R.v)))) (+ℚ-cong (+ℚ-cong gen-Y mid₂) last₂))
    where
      U : ℚ
      U = 1ℚ ⊹ (x · y)
      V : ℚ
      V = (ℤ→ℚ (+ 4)) ⊹ ((ℤ→ℚ (+ 3)) · (x · y))
      mid₂ : evalℚ (R.kP (+ 3) *P R.X *P R.u *P R.u *P R.Z₁)
           ≈ℚ ((ℤ→ℚ (+ 3)) · (x · (U · U))) · z
      mid₂ = ≈ℚ-trans (eval-*P5 (R.kP (+ 3)) R.X R.u R.u R.Z₁) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (*ℚ-cong (*ℚ-cong (gen-kP (+ 3)) gen-X) gen-u) gen-u) gen-Z) (*ℚ-cong (assoc-lll (ℤ→ℚ (+ 3)) x U U) (≈ℚ-refl z)))
      last₂ : evalℚ (R.kP (+ 3) *P R.X *P R.Y *P R.Y *P R.v)
            ≈ℚ ((ℤ→ℚ (+ 3)) · (x · (y · y))) · V
      last₂ = ≈ℚ-trans (eval-*P5 (R.kP (+ 3)) R.X R.Y R.Y R.v) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (*ℚ-cong (*ℚ-cong (gen-kP (+ 3)) gen-X) gen-Y) gen-Y) gen-v) (*ℚ-cong (assoc-lll (ℤ→ℚ (+ 3)) x y y) (≈ℚ-refl V)))

  bridge₃ : evalℚ R.f₃ ≈ℚ C.f₃ x y z
  bridge₃ = ≈ℚ-trans (evalℚ-++ (R.kP (+ 2) *P R.X +P (R.kP (-suc 2) *P R.X *P R.X *P R.Y)) (R.kP (-suc 0) *P R.X *P R.X *P R.X *P R.Z₁)) (≈ℚ-trans (+ℚ-cong (evalℚ-++ (R.kP (+ 2) *P R.X) (R.kP (-suc 2) *P R.X *P R.X *P R.Y)) (≈ℚ-refl (evalℚ (R.kP (-suc 0) *P R.X *P R.X *P R.X *P R.Z₁)))) (+ℚ-cong (+ℚ-cong term1₃ term2₃) term3₃))
    where
      term1₃ : evalℚ (R.kP (+ 2) *P R.X) ≈ℚ ((ℤ→ℚ (+ 2)) · x)
      term1₃ = ≈ℚ-trans (evalℚ-*P (R.kP (+ 2)) R.X) (*ℚ-cong (gen-kP (+ 2)) gen-X)
      term2₃ : evalℚ (R.kP (-suc 2) *P R.X *P R.X *P R.Y)
             ≈ℚ (-ℚ (((ℤ→ℚ (+ 3)) · (x · x)) · y))
      term2₃ = ≈ℚ-trans (eval-*P4 (R.kP (-suc 2)) R.X R.X R.Y) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (*ℚ-cong (gen-kP (-suc 2)) gen-X) gen-X) gen-Y) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (neg-·-l (ℤ→ℚ (+ 3)) x) (≈ℚ-refl x)) (≈ℚ-refl y)) (≈ℚ-trans (*ℚ-cong (neg-·-l ((ℤ→ℚ (+ 3)) · x) x) (≈ℚ-refl y)) (≈ℚ-trans (neg-·-l (((ℤ→ℚ (+ 3)) · x) · x) y) (neg-cong (*ℚ-cong (*ℚ-assoc (ℤ→ℚ (+ 3)) x x) (≈ℚ-refl y)))))))
      term3₃ : evalℚ (R.kP (-suc 0) *P R.X *P R.X *P R.X *P R.Z₁)
             ≈ℚ (-ℚ (((x · x) · x) · z))
      term3₃ = ≈ℚ-trans (eval-*P5 (R.kP (-suc 0)) R.X R.X R.X R.Z₁) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (*ℚ-cong (*ℚ-cong (gen-kP (-suc 0)) gen-X) gen-X) gen-X) gen-Z) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (*ℚ-cong (neg-·-l 1ℚ x) (≈ℚ-refl x)) (≈ℚ-refl x)) (≈ℚ-refl z)) (≈ℚ-trans (*ℚ-cong (*ℚ-cong (neg-·-l (1ℚ · x) x) (≈ℚ-refl x)) (≈ℚ-refl z)) (≈ℚ-trans (*ℚ-cong (neg-·-l ((1ℚ · x) · x) x) (≈ℚ-refl z)) (≈ℚ-trans (neg-·-l (((1ℚ · x) · x) · x) z) (neg-cong (*ℚ-cong (*ℚ-cong (*ℚ-cong (*ℚ-identityˡ x) (≈ℚ-refl x)) (≈ℚ-refl x)) (≈ℚ-refl z))))))))
