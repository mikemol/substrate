{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingNormalize — ⟡jac-encoding-bridge, ROUTE C2.
--
-- THE SINGLE-OBJECT IDENTIFICATION the capstone flagged, landed the way the
-- Rosetta Stone says it lands: through `normalize` (the canonical form), NOT
-- by hand-composing `≈ℚ`.
--
-- ⚑ THE WALL (route A/B): `evalℚ R.fᵢ ≈ℚ C.fᵢ` hand-composed is a WALL —
-- `JacobianEncodingBridge.agda` → EXIT 1 (UnsolvedConstraints). Transparent
-- `≈ℚ` over the eta-record ℚ defeats endpoint inference even fully-pinned.
--
-- ⚑ THE LANDING (route C2): the two encodings of the paper map F —
-- HALF A's curried-ℚ `C.fᵢ` (JacobianCollision) and HALF B's MPoly `R.fᵢ`
-- (JacobianResidue) — are the SAME polynomial. Transcribe C's ℚ-function
-- formula into MPoly-over-ℤ as `Cᴹfᵢ` (C's coefficients are integers; `-ℚ b`
-- is `kP (-suc 0) *P b`). R and C differ only by association/expansion, so
-- `normalize` sends both to the IDENTICAL canonical sorted list:
--
--     normalize R.fᵢ ≡ normalize Cᴹfᵢ    (refl)
--
-- Rigid ℤ `≡`, zero `≈ℚ` composition — the mirror of `norm-detJac-is-const`
-- (JacobianCounterexample), which is `refl` on a heavier degree-9 object.
-- This proves the identification at the POLYNOMIAL level. The remaining inch
-- to the literal ℚ FUNCTION `C.fᵢ` is the labelled-open β
-- (`evalℚ p ≈ℚ evalℚ (normalize p)`), not attempted here.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingNormalize where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (+_; -suc_)
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Z.JacobianResidue as R
  using (MPoly; X; Y; Z₁; 𝟙P; kP; _*P_; _+P_)

------------------------------------------------------------------------
-- 1. Cᴹfᵢ — HALF A's C.fᵢ (JacobianCollision) transcribed into MPoly-over-ℤ,
--    keeping C's OWN grouping (right-assoc, inline u/v), so it is a genuinely
--    independent encoding of F, not R's helpers reused.
--      x ↦ X , y ↦ Y , z ↦ Z₁ , nℚ ↦ kP (+ n) , a -ℚ b ↦ a +P (kP (-suc 0) *P b)
------------------------------------------------------------------------

Cu Cv : MPoly
Cu = 𝟙P +P (X *P Y)                          -- C.u = 1ℚ +ℚ (x *ℚ y)
Cv = kP (+ 4) +P (kP (+ 3) *P (X *P Y))      -- C.v = 4ℚ +ℚ (3ℚ *ℚ (x *ℚ y))

Cᴹf₁ Cᴹf₂ Cᴹf₃ : MPoly
-- C.f₁ x y z = (z *ℚ (u *ℚ (u *ℚ u))) +ℚ (((y *ℚ y) *ℚ u) *ℚ v)
Cᴹf₁ = (Z₁ *P (Cu *P (Cu *P Cu))) +P (((Y *P Y) *P Cu) *P Cv)
-- C.f₂ x y z = (y +ℚ ((3ℚ *ℚ (x *ℚ (u *ℚ u))) *ℚ z)) +ℚ ((3ℚ *ℚ (x *ℚ (y *ℚ y))) *ℚ v)
Cᴹf₂ = (Y +P ((kP (+ 3) *P (X *P (Cu *P Cu))) *P Z₁))
       +P ((kP (+ 3) *P (X *P (Y *P Y))) *P Cv)
-- C.f₃ x y z = ((2ℚ *ℚ x) -ℚ ((3ℚ *ℚ (x *ℚ x)) *ℚ y)) -ℚ (((x *ℚ x) *ℚ x) *ℚ z)
Cᴹf₃ = ((kP (+ 2) *P X) +P (kP (-suc 0) *P ((kP (+ 3) *P (X *P X)) *P Y)))
       +P (kP (-suc 0) *P (((X *P X) *P X) *P Z₁))

------------------------------------------------------------------------
-- 2. THE BRIDGE: the two encodings normalize to the same canonical polynomial.
------------------------------------------------------------------------

bridge₁ : normalize R.f₁ ≡ normalize Cᴹf₁
bridge₁ = refl

bridge₂ : normalize R.f₂ ≡ normalize Cᴹf₂
bridge₂ = refl

bridge₃ : normalize R.f₃ ≡ normalize Cᴹf₃
bridge₃ = refl
