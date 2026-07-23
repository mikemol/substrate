{-# OPTIONS --safe --without-K #-}

-- SCRATCH: the explicit ℤ cube/product proof for identify₁ via Route 2.
-- Goal: identify₁ : evalℚ f₁ ≈ℚ C.f₁, cheap, by hand-driving the binomial
-- expansion in ℤ (NOT letting Agda auto-normalize — that balloons RAM).
module Substrate.Algebra.Q.JacCube where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; 0ℤ)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-assoc; +ℤ-identityˡ)
open import Substrate.Algebra.Q using (ℚ; mkℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.JacobianEvalNormalize using (evalℚ; normalize-eval; ≡→≈ℚ)
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Z.JacobianResidue using (MPoly; Mono; mono; Term; term)
import Substrate.Algebra.Z.JacobianResidue as R
import Substrate.Algebra.Q.JacobianEvalCD as CD
import Substrate.Algebra.Q.JacobianEvalCDCurried as Cur
import Substrate.Algebra.Q.JacobianCollision as C
open import Substrate.Foundation.List using (List; []; _∷_; _++_)

-- sumNum is additive over ++ (fold homomorphism).
sumNum-++ : (x y z : ℚ) (p q : MPoly) →
            CD.sumNum x y z 3 4 1 (p ++ q)
              ≡ CD.sumNum x y z 3 4 1 p +ℤ CD.sumNum x y z 3 4 1 q
sumNum-++ x y z []       q = sym (+ℤ-identityˡ (CD.sumNum x y z 3 4 1 q))
sumNum-++ x y z (t ∷ p) q =
  trans (cong (CD.padNum x y z 3 4 1 t +ℤ_) (sumNum-++ x y z p q))
        (sym (+ℤ-assoc (CD.padNum x y z 3 4 1 t) (CD.sumNum x y z 3 4 1 p)
                        (CD.sumNum x y z 3 4 1 q)))

-- my explicit expanded MPoly (order-controlled: z-part then y²-part).
Cᶠz Cᶠy Cᶠ : MPoly
Cᶠz = term (mono 0 0 1) (+ 1) ∷ term (mono 1 1 1) (+ 3)
    ∷ term (mono 2 2 1) (+ 3) ∷ term (mono 3 3 1) (+ 1) ∷ []
Cᶠy = term (mono 0 2 0) (+ 4) ∷ term (mono 1 3 0) (+ 7)
    ∷ term (mono 2 4 0) (+ 3) ∷ []
Cᶠ = Cᶠz ++ Cᶠy

-- same polynomial as f₁ (both canonicalize to the 7-term normal form).
bridgeᶠ : normalize R.f₁ ≡ normalize Cᶠ
bridgeᶠ = refl

