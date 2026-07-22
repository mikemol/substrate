{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianDetLiteral — ⟡jac-det-literal.
--
-- The determinant residue at the LITERAL ℚ level. `norm-detJac-is-const :
-- normalize R.detJac ≡ R.kP (-suc 1)` (HALF B, box-free) is the RIGID
-- normal-form statement; β (`normalize-eval`) lifts it across the ℚ evaluator
-- to the literal VALUE of the RAW determinant polynomial:
--
--     detJac-literal : (x y z : ℚ) → evalℚ x y z R.detJac ≈ℚ ℤ→ℚ (−2)
--
-- so `det Jac F` evaluates to the constant −2 at EVERY ℚ point — the ℚ-eval
-- companion of the capstone's rigid `det-is-const-neg2`.
--
-- ⚑ MEMORY DISCIPLINE (why this is 3 modules, not one line in the literal
-- module; `scripts/check_def_proof_separation.sh`):
--   * Imports ONLY the MINIMAL generator layer `JacobianEncodingGen.Point`
--     (for `gen-kP`) + β — NOT the `homAgree`/`*P` engine, NOT the degree-9 γᵢ:
--     importing either deserializes its proof closure at ~40× and OOMs the gate.
--   * The endpoints touching the RAW det (`evalℚ x y z R.detJac` and
--     `… (normalize R.detJac)`) are pinned with `β.evalℚ x y z` DIRECTLY, never
--     the opened `Point.E` alias: unfolding `Point.E` across the huge det term
--     inside the `≈ℚ-trans` implicit costs >1 GB, whereas `β.evalℚ x y z` matches
--     `normalize-eval`'s result syntactically (no reduction). `gen-kP` (whose type
--     mentions `Point.E`) touches only the tiny `R.kP`, so its unfold is free.
--   * The `normalize R.detJac ⇒ R.kP (-suc 1)` reduction lives ONLY in the local
--     `nd = refl`; `cong` transports the endpoint so the trans node never reduces
--     the raw det.  Net: the whole obligation is ~85 MB (was >3 GB monolithic).
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianDetLiteral where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.Z using (-suc_)
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)

import Substrate.Algebra.Z.JacobianResidue as R
import Substrate.Algebra.Q.JacobianEvalNormalize as β

-- The MINIMAL generator layer — take ONLY gen-kP, NOT E (see the memory note).
open import Substrate.Algebra.Q.JacobianEncodingGen

module _ (x y z : ℚ) where

  open Point x y z using (gen-kP)

  private
    nd : normalize R.detJac ≡ R.kP (-suc 1)
    nd = refl

  detJac-literal : β.evalℚ x y z R.detJac ≈ℚ ℤ→ℚ (-suc 1)
  detJac-literal =
    ≈ℚ-trans {β.evalℚ x y z R.detJac} {β.evalℚ x y z (normalize R.detJac)} {ℤ→ℚ (-suc 1)}
      (β.normalize-eval x y z R.detJac)
      (≈ℚ-trans {β.evalℚ x y z (normalize R.detJac)} {β.evalℚ x y z (R.kP (-suc 1))} {ℤ→ℚ (-suc 1)}
        (β.≡→≈ℚ (cong (β.evalℚ x y z) nd))
        (gen-kP (-suc 1)))
