{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianCollision — ⟡jac-collision.
--
-- HALF (i) of the claimed counterexample to the JACOBIAN CONJECTURE: the map
--
--   F(x,y,z) = ( z(1+xy)³ + y²(1+xy)(4+3xy)
--              , y + 3x(1+xy)²z + 3xy²(4+3xy)
--              , 2x − 3x²y − x³z )
--
-- is NOT INJECTIVE — it sends the two distinct points (0,0,−1/4) and
-- (1,−3/2,13/2) to the same image (−1/4,0,0). Machine-checked here by
-- evaluation, componentwise, in ℚ.
--
-- ⚑ PROVENANCE, AND WHAT THIS DOES *NOT* SHOW. The map is attributed to Levent
-- Alpöge (2026-07-19) via Wikipedia; I have no independent knowledge of it (my
-- training predates it) and the problem is, in that article's own words,
-- "notorious for the large number of published and unpublished false proofs
-- that turned out to contain subtle errors". A counterexample needs BOTH
--   (i) F(p) = F(q) with p ≠ q          ← THIS MODULE
--   (ii) det Jac F a nonzero CONSTANT   ← NOT HERE; see ⟡jac-det
-- and ALL of the subtlety lives in (ii). **This module does not verify the
-- counterexample. It verifies its easy half.** Do not cite it for more.
--
-- ⚑ WHY `_≈ℚ_` AND NOT `_≡_`: `ℚ` is the UNNORMALIZED pair `mkℚ (num : ℤ)
-- (den-1 : ℕ)` (Algebra/Q.agda:32-36), so 1/2 and 2/4 are DISTINCT VALUES and
-- `_≡_` is the wrong relation. `_≈ℚ_` is cross-multiplication
-- (Algebra/Q/Equiv.agda:37), which is the equality of rationals proper.
--
-- ⚑ NO `¬` HERE — distinctness is stated as a DERIVED ABSURD EQUATION, as in
-- `R.Trace.EventualPeriod`: the caller does the `()`. Reading an observable and
-- seeing it differ, rather than assuming and refuting.
--
-- --safe --without-K; no postulates, no holes. Every proof is `refl`.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianCollision where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Sub using (_-ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- 1. Literals. All coefficients of F are integers; only the POINTS are
--    genuinely rational.
------------------------------------------------------------------------

2ℚ 3ℚ 4ℚ : ℚ
2ℚ = mkℚ (+ 2) 0
3ℚ = mkℚ (+ 3) 0
4ℚ = mkℚ (+ 4) 0

-1/4ℚ : ℚ
-1/4ℚ = mkℚ (-suc 0) 3          -- −1 / 4

-3/2ℚ : ℚ
-3/2ℚ = mkℚ (-suc 2) 1          -- −3 / 2

13/2ℚ : ℚ
13/2ℚ = mkℚ (+ 13) 1            -- 13 / 2

------------------------------------------------------------------------
-- 2. The three components of F.
------------------------------------------------------------------------

f₁ : ℚ → ℚ → ℚ → ℚ
f₁ x y z = (z *ℚ (u *ℚ (u *ℚ u))) +ℚ (((y *ℚ y) *ℚ u) *ℚ v)
  where
    u = 1ℚ +ℚ (x *ℚ y)
    v = 4ℚ +ℚ (3ℚ *ℚ (x *ℚ y))

f₂ : ℚ → ℚ → ℚ → ℚ
f₂ x y z = (y +ℚ ((3ℚ *ℚ (x *ℚ (u *ℚ u))) *ℚ z)) +ℚ ((3ℚ *ℚ (x *ℚ (y *ℚ y))) *ℚ v)
  where
    u = 1ℚ +ℚ (x *ℚ y)
    v = 4ℚ +ℚ (3ℚ *ℚ (x *ℚ y))

f₃ : ℚ → ℚ → ℚ → ℚ
f₃ x y z = ((2ℚ *ℚ x) -ℚ ((3ℚ *ℚ (x *ℚ x)) *ℚ y)) -ℚ (((x *ℚ x) *ℚ x) *ℚ z)

------------------------------------------------------------------------
-- 3. THE COLLISION, componentwise. p = (0, 0, −1/4), q = (1, −3/2, 13/2).
------------------------------------------------------------------------

collision₁ : f₁ 0ℚ 0ℚ -1/4ℚ ≈ℚ f₁ 1ℚ -3/2ℚ 13/2ℚ
collision₁ = refl

collision₂ : f₂ 0ℚ 0ℚ -1/4ℚ ≈ℚ f₂ 1ℚ -3/2ℚ 13/2ℚ
collision₂ = refl

collision₃ : f₃ 0ℚ 0ℚ -1/4ℚ ≈ℚ f₃ 1ℚ -3/2ℚ 13/2ℚ
collision₃ = refl

------------------------------------------------------------------------
-- 4. …and the common image is (−1/4, 0, 0), as claimed.
------------------------------------------------------------------------

image₁ : f₁ 0ℚ 0ℚ -1/4ℚ ≈ℚ -1/4ℚ
image₁ = refl

image₂ : f₂ 0ℚ 0ℚ -1/4ℚ ≈ℚ 0ℚ
image₂ = refl

image₃ : f₃ 0ℚ 0ℚ -1/4ℚ ≈ℚ 0ℚ
image₃ = refl

------------------------------------------------------------------------
-- 5. THE POINTS ARE DISTINCT — they already differ in x. Stated as a derived
--    absurd equation rather than a negation: if the x-coordinates were equal
--    as rationals, then 0ℤ ≡ 1ℤ, and the caller refutes that with `()`.
------------------------------------------------------------------------

x-differs : (0ℚ ≈ℚ 1ℚ) → 0ℤ ≡ 1ℤ
x-differs e = e
