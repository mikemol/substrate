------------------------------------------------------------------------
-- Substrate.WitnessTower.SignStepCocycle
--
-- ⟡sign-step-correspondence — the SIGN cocycle stated as a CORRESPONDENCE
-- OVER THE INDUCTIVE STEP, not at a fixed grade. Per the graded-morphism
-- discipline (GradedDivStrMorphism.respects-recon: a map commutes with the
-- grade-raising `recon`, quantified over all n at once), the right statement
-- of "sign is a graded cocycle over tower-graded" is NOT `sign (σ·τ) at fixed
-- n` — it is how sign behaves under the tower's witnessing STEP
-- `recon tower-graded n = insert-at`, from which every grade follows by
-- induction.
--
-- THE STEP CORRESPONDENCE (proved, no fixed grade):
--   sign (insert-at p σ) ≡ parityLess p (map (punchIn p) σ) xor sign σ
-- i.e. the sign after one witnessing-insertion = (the insertion digit's
-- parity contribution) xor (the sign below). This is sign's `respects-recon`
-- for tower-graded — the single equation over the step. The digit
-- contribution is written HONESTLY as what the step actually adds
-- (parityLess p over the punched images), NOT prematurely collapsed to
-- parity(toℕ p) (which needs IsPerm).
--
-- The crux is finLt-punch: punchIn is strictly monotone, so it preserves all
-- order comparisons — hence sign-punch (punchIn preserves the sign of the
-- tail). Both are proved by induction on the STEP structure.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SignStepCocycle where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)
open import Substrate.Foundation.Bool using (Bool; _xor_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)
open import Substrate.Algebra.Wedge.Graded using (recon)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign; parityLess; finLt)

------------------------------------------------------------------------
-- 1. punchIn is strictly monotone: it preserves order comparisons.
--    (Proved over the step structure of p, y, x.)
------------------------------------------------------------------------

finLt-punch : {n : ℕ} (p : Fin (suc n)) (y x : Fin n) →
              finLt (punchIn p y) (punchIn p x) ≡ finLt y x
finLt-punch zero    y       x       = refl
finLt-punch (suc p) zero    zero    = refl
finLt-punch (suc p) zero    (suc x) = refl
finLt-punch (suc p) (suc y) zero    = refl
finLt-punch {suc n} (suc p) (suc y) (suc x) = finLt-punch p y x

------------------------------------------------------------------------
-- 2. Hence parityLess and sign are preserved by the punchIn shift.
------------------------------------------------------------------------

pl-punch : {n k : ℕ} (p : Fin (suc n)) (x : Fin n) (xs : Vec (Fin n) k) →
           parityLess (punchIn p x) (map (punchIn p) xs) ≡ parityLess x xs
pl-punch p x []       = refl
pl-punch p x (y ∷ ys) = cong₂ _xor_ (finLt-punch p y x) (pl-punch p x ys)

sign-punch : {n k : ℕ} (p : Fin (suc n)) (σ : Vec (Fin n) k) →
             sign (map (punchIn p) σ) ≡ sign σ
sign-punch p []       = refl
sign-punch p (x ∷ xs) = cong₂ _xor_ (pl-punch p x xs) (sign-punch p xs)

------------------------------------------------------------------------
-- 3. THE STEP CORRESPONDENCE. sign under the tower's witnessing step
--    (recon tower-graded n = insert-at). One equation, all grades by
--    induction — the graded-morphism `respects-recon` for sign.
------------------------------------------------------------------------

sign-step : {n : ℕ} (p : Fin (suc n)) (σ : Perm n) →
            sign (insert-at p σ) ≡ (parityLess p (map (punchIn p) σ) xor sign σ)
sign-step p σ = cong (parityLess p (map (punchIn p) σ) xor_) (sign-punch p σ)

-- The REAL identification: tower-graded's grade-raising recon IS insert-at, so
-- sign-step is literally sign's `respects-recon` for tower-graded. This binds
-- sign-step to the graded structure (not a trivial self-equality): recon
-- tower-graded n σ p computes to insert-at p σ, hence sign-step restated on
-- recon holds by the same proof.
sign-respects-recon :
  {n : ℕ} (σ : Perm n) (p : Fin (suc n)) →
  sign (recon tower-graded n σ p) ≡ (parityLess p (map (punchIn p) σ) xor sign σ)
sign-respects-recon σ p = sign-step p σ
