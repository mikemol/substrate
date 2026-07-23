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
-- ⚑ THE SINGLE-OBJECT IDENTIFICATION — MACHINE-CHECKED, FIELDED (◆jac-gamma). The two
-- halves are about the SAME paper map F, under two independent encodings — HALF A's
-- curried ℚ functions `C.f₁/f₂/f₃` and HALF B's `MPoly` F (`Algebra.Z.JacobianResidue`'s
-- `f₁/f₂/f₃`, of which `detJac` is the determinant). These were previously conjoined
-- only BY INSPECTION (identical monomial structure); the rung equating the ℚ-eval of the
-- `MPoly` F with the curried ℚ F is PROVEN in `JacobianEncodingLiteral.literal₁/₂/₃`
--    literalᵢ : Identifyᵢ   (≡ (x y z : ℚ) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z)
-- (the ⟡jac-encoding-bridge Rosetta Stone, closed by a free-algebra universal-property
-- lift; f₁'s (1+xy)³ cube γ₁ = `JacCubeNorm.identify₁`, a reflective-normalizer proof). So
-- the `identify₁/₂/₃` fields below make this a TRUE single-object statement: this ℚ F IS
-- the ℤ F, evaluated — one map, machine-checked end-to-end.
--
-- ⟡cap128-jac-stage: the γ literals ARE fielded here — via the OrderOf opaque-TYPE seal
-- (cap384). `JacobianEncodingLiteral.Identifyᵢ` is `opaque`, so the heavy cube reduction
-- (`evalℚ` over the degree-9 f₁) happens ONCE behind that boundary (~89 MB); this capstone
-- fields the `literalᵢ` as NON-REDUCING handles `: Identifyᵢ`, so the record type-check is
-- SYNTACTIC and never re-fires the cube. (Fielding the RAW literal — busting the cap — is
-- the wall the seal routes around, the same class as the cited `detJac-literal` below.)
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianCounterexample where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Product using (proj₁)
open import Substrate.Algebra.Z using (ℤ; -suc_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
import Substrate.Algebra.Q.JacobianCollision as C
import Substrate.Algebra.Z.JacobianResidue   as R
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Z.JacobianDetNative using (detNative; detNative-normal)
import Substrate.Algebra.Q.JacobianEncodingLiteral as L

-- ⚑ The ℚ-EVAL companion of `det-is-const-neg2` — the RAW determinant polynomial
-- evaluated equals −2 at every point — is `Substrate.Algebra.Q.JacobianDetLiteral.
-- detJac-literal : evalℚ x y z R.detJac ≈ℚ ℤ→ℚ (-suc 1)` (⟡jac-det-literal). It is
-- NOT a field of this record: this module declares a `record` (a def-provider) and
-- importing that heavy `normalize-eval`-over-det proof would deserialize it at ~40×
-- and OOM the per-module gate (`scripts/check_def_proof_separation.sh` mechanism).
-- The rigid normal-form fact below (a cheap `refl`) is the one held here.

-- ⟡cap128-jac-stage: the native, INCREMENTALLY-normalized Leibniz-over-S₃ determinant
-- (`detNative = det {3} JacMat` over the NormPoly semiring, which normalizes after each ⊕/⊗)
-- IS the constant −2, at ~98 MB — whereas the monolithic `normalize R.detJac` (below) is 317 MB
-- (comparing it to a single `kP` term has no cheaper normal form to stream the global cancellation
-- against, so agda holds all ~204 pre-cancellation terms at once).
det-native-is-neg2 : proj₁ detNative ≡ R.kP (-suc 1)
det-native-is-neg2 = refl

-- HALF B, box-free: the determinant's full normal form is the constant −2. Proven THROUGH the native
-- det: `detNative-normal : proj₁ detNative ≡ normalize detJac` (streaming comparison, cheap here as a
-- stuck neutral) composed with `det-native-is-neg2`. `normalize detJac` never reduces in this module.
norm-detJac-is-const : normalize R.detJac ≡ R.kP (-suc 1)
norm-detJac-is-const = trans (sym detNative-normal) det-native-is-neg2

record IsJacobianCounterexample : Set where
  field
    -- HALF A — F(p) ≈ F(q) componentwise at two distinct points.
    collide₁ : C.f₁ 0ℚ 0ℚ C.-1/4ℚ ≈ℚ C.f₁ 1ℚ C.-3/2ℚ C.13/2ℚ
    collide₂ : C.f₂ 0ℚ 0ℚ C.-1/4ℚ ≈ℚ C.f₂ 1ℚ C.-3/2ℚ C.13/2ℚ
    collide₃ : C.f₃ 0ℚ 0ℚ C.-1/4ℚ ≈ℚ C.f₃ 1ℚ C.-3/2ℚ C.13/2ℚ
    distinct : (0ℚ ≈ℚ 1ℚ) → 0ℤ ≡ 1ℤ
    -- HALF B — det Jac F is the nonzero constant −2 (box-free).
    det-is-const-neg2 : normalize R.detJac ≡ R.kP (-suc 1)
    -- ◆jac-gamma — HALF A's curried ℚ F IS HALF B's MPoly F, evaluated at every point.
    -- Fielded through the opaque `L.Identifyᵢ` handle (≡ (x y z) → evalℚ x y z R.fᵢ ≈ℚ
    -- C.fᵢ x y z); the seal keeps the reification cheap (see the header, ⟡cap128-jac-stage).
    identify₁ : L.Identify₁
    identify₂ : L.Identify₂
    identify₃ : L.Identify₃

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
