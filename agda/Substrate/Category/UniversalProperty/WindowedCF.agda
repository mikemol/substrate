------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.WindowedCF
--
-- CERTIFYING the apex (user, 2026-06-13: "Let's do it. The only honest thing about
-- this system is the math"). The similarity detector FOUND `windowed-cf`; this
-- turns "Exp/Log/Window factor through a rational kernel" from a refactoring into a
-- theorem, by registering the family through `UPArrow`:
--
--   Source  (Spec) = an operation  ℕ → RealTrace → List ℕ   (window n, real x ↦ CF)
--   Target  (Inst) = a rational kernel  ℕ → ℕ → ℕ × ℕ
--   Witness        = op ≡ windowed-cf K   ("K computes that CF")
--
-- The three are instances, by refl — after the apex refactor they ARE
-- `windowed-cf` of their kernels DEFINITIONALLY (`exp-cf-inst`/`log-cf-inst`/
-- `homographic-inst`). It is a RecognizedUP (carries non-vacuity). And it is
-- UNIVERSAL in the honest sense: the kernel is the WHOLE variation boundary —
-- `Windowed.windowed-cf-determined`, re-exported, shows agreement of kernels ⇒
-- agreement of ops at every (n, x).
--
-- HONEST CALIBRATION (the math, not the hype): this is weaker than the wedge UP.
-- The wedge's kernel is RECOVERABLE (recon-bounded-unique: the witness pins (q,r)).
-- Here the kernel is read only at the reachable convergents, so two kernels that
-- differ only off-convergent are identified — `windowed-cf` is determined BY the
-- kernel but does not conversely pin every kernel value. So: a genuine UPArrow with
-- proved instances + pointwise universality, NOT an initial algebra with a unique
-- kernel. That distinction is the certificate's exact strength.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.WindowedCF where

open import Substrate.Foundation.Nat      using (ℕ; _+_; _*_; _∸_)
open import Substrate.Foundation.List     using (List; []; _∷_)
open import Substrate.Foundation.Product  using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq       using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.R.Trace          using (RealTrace; sqrt2)
open import Substrate.Algebra.R.Trace.Windowed using (windowed-cf; windowed-cf-determined)
open import Substrate.Algebra.R.Trace.Exp      using (exp-cf; horner)
open import Substrate.Algebra.R.Trace.Log      using (log-cf; ath)
open import Substrate.Algebra.R.Trace.Window   using (homographic-cf)

open import Substrate.Category.UniversalProperty            using (UPArrowP; mkUP; WitnessP)
open import Substrate.Category.UniversalProperty.Vacuity    using (Contentful)
open import Substrate.Category.UniversalProperty.Recognized using (RecognizedUP)

------------------------------------------------------------------------
-- The windowed-CF family as a UPArrow: an op is solved by a kernel that computes
-- its continued fraction.
------------------------------------------------------------------------

windowedCF-W : (ℕ → RealTrace → List ℕ) → (ℕ → ℕ → ℕ × ℕ) → Set
windowedCF-W op K = op ≡ windowed-cf K

windowedCF-UP : UPArrowP (ℕ → RealTrace → List ℕ) (ℕ → ℕ → ℕ × ℕ) windowedCF-W
windowedCF-UP = mkUP

------------------------------------------------------------------------
-- The three operations are instances — each witnessed by its kernel, by refl.
------------------------------------------------------------------------

exp-cf-inst : (terms : ℕ) → WitnessP windowedCF-UP (exp-cf terms) (λ p q → horner terms p q 1 1)
exp-cf-inst terms = refl

log-cf-inst : (terms : ℕ) → WitnessP windowedCF-UP (log-cf terms)
              (λ p q → let sn = p ∸ q
                           sd = p + q
                           U  = ath terms (2 * terms ∸ 1) (sn * sn) (sd * sd) 0 1
                       in 2 * sn * proj₁ U , sd * proj₂ U)
log-cf-inst terms = refl

homographic-inst : (a b c d : ℕ)
                 → WitnessP windowedCF-UP (homographic-cf a b c d) (λ p q → a * p + b * q , c * p + d * q)
homographic-inst a b c d = refl

------------------------------------------------------------------------
-- CONTENTFUL: the constant-[] op is NOT windowed-cf of the constant-(2,1) kernel
-- (at (n,x) = (0, √2) the latter is [2], not []). So the relation has content.
------------------------------------------------------------------------

windowedCF-contentful : Contentful windowedCF-UP
windowedCF-contentful = (λ _ _ → []) , (λ _ _ → 2 , 1) , ne
  where
    ne : ¬ ((λ _ _ → []) ≡ windowed-cf (λ _ _ → 2 , 1))
    ne eq with cong (λ f → f 0 sqrt2) eq
    ... | ()

windowedCF-recognized : RecognizedUP (ℕ → RealTrace → List ℕ) (ℕ → ℕ → ℕ × ℕ) windowedCF-W
windowedCF-recognized = record { content = windowedCF-contentful }

------------------------------------------------------------------------
-- UNIVERSALITY (honest form): the kernel is the whole variation boundary.
------------------------------------------------------------------------

windowedCF-universal :
  (K₁ K₂ : ℕ → ℕ → ℕ × ℕ) → ((p q : ℕ) → K₁ p q ≡ K₂ p q)
  → (n : ℕ) (x : RealTrace) → windowed-cf K₁ n x ≡ windowed-cf K₂ n x
windowedCF-universal = windowed-cf-determined
