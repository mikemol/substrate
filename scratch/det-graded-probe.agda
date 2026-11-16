{-# OPTIONS --safe --without-K #-}
module gs where
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; sym)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_; _+_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-identityˡ)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Algebra.Wedge.Graded.Morphism using (GradedDivStrMorphism)
open import Substrate.Algebra.R.Trace.CFMatrixBridge using (Mat; mat; detM; state)
open import Substrate.Algebra.R.Trace.CFMatrixBridge.Properties using (matrix-det-flip)

-- ONE CF step as a grade-raising recon: state at rung n → state at rung (suc n)
cfStep : ℕ → Mat → Mat
cfStep a (mat p₁ p₀ q₁ q₀) = mat (a * p₁ + p₀) p₁ (a * q₁ + q₀) q₁

cf-graded : GradedDivStr (λ _ → Mat) (λ _ → ℕ)
cf-graded = record { recon = λ n s a → cfStep a s }

-- the SIGN target (multiplicative ℤ): recon multiplies
ℤˣ-target : GradedDivStr (λ _ → ℤ) (λ _ → ℤ)
ℤˣ-target = record { recon = λ n b r → r *ℤ b }

-- the bridge lemma: negation IS multiplication by −1. REUSED, not hand-rolled:
-- `-suc 0` IS `-ℤ (+ 1)` definitionally, so this is neg-*-left + the ℤ unit law.
neg-is-mul : (x : ℤ) → -ℤ x ≡ (-suc 0) *ℤ x
neg-is-mul x = sym (trans (neg-*-left (+ 1) x) (cong -ℤ_ (*ℤ-identityˡ x)))

-- ⚑ THE DETERMINANT AS A GRADED MORPHISM: map-R is constantly −1,
--   so detM at rung n is (−1)ⁿ · detM at rung 0.
det-graded : GradedDivStrMorphism cf-graded ℤˣ-target
det-graded = record
  { map-C = detM
  ; map-R = λ _ → -suc 0
  ; respects-recon = λ { n (mat p₁ p₀ q₁ q₀) a →
      trans (matrix-det-flip a p₁ q₁ p₀ q₀) (neg-is-mul (detM (mat p₁ p₀ q₁ q₀))) }
  }
