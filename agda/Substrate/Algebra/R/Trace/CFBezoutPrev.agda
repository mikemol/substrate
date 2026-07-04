{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFBezoutPrev — ⟡N1b-Matrix-prevconv (the HONEST
-- CLEAN core; the fold-reconciliation is separately scoped).
--
-- ADD 52 caught that "bezout-ℤ = convergent-matrix inverse (as a fold)" is
-- FALSE (opposite fold directions). The TRUE relation is "Bézout coeffs =
-- PREVIOUS convergent ± sign". ⟡H0: that IS the neighbour determinant det4
-- (Properties): det4 pₙ qₙ pₙ₋₁ qₙ₋₁ = (pₙ·qₙ₋₁) ⊖ (pₙ₋₁·qₙ) — which is
-- EXACTLY the Bézout combination of the previous convergent (qₙ₋₁, −pₙ₋₁)
-- against the current one (pₙ, qₙ). And det²≡1 (Properties) proves the
-- seed-rooted determinant is a UNIT. So the previous convergent SOLVES the
-- Bézout equation for the current convergent, its combination = ±1.
--
-- CLEAN CORE (built here): bezout-combo (qₙ₋₁,−pₙ₋₁) for (pₙ,qₙ) ≡ det4, and
-- (seed-rooted) det4 is a unit — the previous convergent IS a Bézout witness.
-- OUT OF SCOPE (honest): that bezout-ℤ's SPECIFIC (s,t) output equals this
-- previous convergent requires the forward/backward fold reconciliation
-- (⟡N1b-Matrix-prevconv-fold) — NOT claimed. This module lands the VALUE-level
-- correspondence (convergents supply Bézout witnesses) on the repo's det4/det².
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFBezoutPrev where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Add using (_⊖_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.R.Trace using (RealTrace)
open import Substrate.Algebra.R.Trace.Properties using (det4; det-after; det²≡1)

open import Substrate.Foundation.Nat using (_*_)

------------------------------------------------------------------------
-- the Bézout combination of the PREVIOUS convergent (p₀,q₀)=(pₙ₋₁,qₙ₋₁) as
-- coefficients (q₀, −p₀) against the CURRENT convergent (p₁,q₁)=(pₙ,qₙ):
--   q₀·p₁ − p₀·q₁   (i.e. coefficient q₀ on p₁, coefficient −p₀ on q₁).
-- Written via ⊖ (the ℕ→ℤ truncated difference) as (p₁·q₀) ⊖ (p₀·q₁).
------------------------------------------------------------------------
bezout-combo : ℕ → ℕ → ℕ → ℕ → ℤ
bezout-combo p₁ q₁ p₀ q₀ = (p₁ * q₀) ⊖ (p₀ * q₁)

-- THE BRIDGE (value level): the previous-convergent Bézout combination IS the
-- neighbour determinant det4 — definitionally the same expression.
combo-is-det4 : (p₁ q₁ p₀ q₀ : ℕ)
              → bezout-combo p₁ q₁ p₀ q₀ ≡ det4 p₁ q₁ p₀ q₀
combo-is-det4 p₁ q₁ p₀ q₀ = refl

-- and the seed-rooted determinant along any trace is a UNIT (its square ≡ +1),
-- so the previous convergent's Bézout combination is ±1 — a genuine Bézout
-- witness. This DELEGATES to the repo's det²≡1 (no reproof).
prev-convergent-is-bezout-unit :
  (n : ℕ) (r : RealTrace) →
  (det-after n 1 0 0 1 r) *ℤ (det-after n 1 0 0 1 r) ≡ (+ 1)
prev-convergent-is-bezout-unit = det²≡1
