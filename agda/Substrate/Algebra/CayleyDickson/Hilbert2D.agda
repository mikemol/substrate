------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Hilbert2D
--
-- ⊙.hilbert2d — the full 2D Hilbert curve (reflection + ROTATION), resolving the
-- ⊙.hilbert "Gray = Hilbert" wedge. `Curve.gray` is the 1D reflected-binary curve
-- (reflection only, the rotation-free corner); the genuine 2D Hilbert needs the
-- per-quadrant ROTATION to stay continuous. That rotation is exactly what this
-- adds — and it is what 1D Gray never needs.
--
-- The order-n curve is its point sequence, built recursively: 4 transformed copies
-- of the order-(n−1) curve — A = transpose (entry rotation), B/C = translated, D =
-- anti-diagonal reflection (exit rotation). CONTINUITY (consecutive points adjacent,
-- Manhattan = 1, across the quadrant seams too) holds ONLY because the A/D rotations
-- orient the sub-curves to meet; `maxjump (hilbert k) ≡ 1` by refl VALIDATES the
-- construction (a wrong rotation would make the seam jump > 1). The general
-- ∀n continuity (an inductive entry/exit-adjacency invariant) is a further refinement.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Hilbert2D where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

Pt : Set
Pt = ℕ × ℕ

pow2 : ℕ → ℕ
pow2 zero    = 1
pow2 (suc n) = pow2 n + pow2 n

mapL : (Pt → Pt) → List Pt → List Pt
mapL f []       = []
mapL f (p ∷ ps) = f p ∷ mapL f ps

-- the order-n Hilbert curve, point by point.
hilbert : ℕ → List Pt
hilbert zero    = (0 , 0) ∷ []
hilbert (suc n) =
       mapL (λ p → (proj₂ p , proj₁ p)) h                            -- A: transpose (entry rotation)
    ++ mapL (λ p → (proj₁ p , proj₂ p + s)) h                        -- B: shift up
    ++ mapL (λ p → (proj₁ p + s , proj₂ p + s)) h                    -- C: shift up-right
    ++ mapL (λ p → (((s + s) ∸ 1) ∸ proj₂ p , (s ∸ 1) ∸ proj₁ p)) h  -- D: anti-diag reflect (exit rotation)
  where h = hilbert n
        s = pow2 n

------------------------------------------------------------------------
-- Continuity = the max consecutive Manhattan jump is 1.
------------------------------------------------------------------------

maxℕ : ℕ → ℕ → ℕ
maxℕ zero    n       = n
maxℕ (suc m) zero    = suc m
maxℕ (suc m) (suc n) = suc (maxℕ m n)

manh : Pt → Pt → ℕ                                   -- L¹ distance ((a∸b)+(b∸a) = |a−b|)
manh p q = ((proj₁ p ∸ proj₁ q) + (proj₁ q ∸ proj₁ p))
         + ((proj₂ p ∸ proj₂ q) + (proj₂ q ∸ proj₂ p))

maxjump : List Pt → ℕ
maxjump []           = 0
maxjump (_ ∷ [])     = 0
maxjump (p ∷ q ∷ ps) = maxℕ (manh p q) (maxjump (q ∷ ps))

-- order-1 IS the U tetromino: (0,0)→(0,1)→(1,1)→(1,0).
hilbert-1 : hilbert 1 ≡ (0 , 0) ∷ (0 , 1) ∷ (1 , 1) ∷ (1 , 0) ∷ []
hilbert-1 = refl

-- THE TEST: consecutive points adjacent everywhere — the curve is continuous,
-- INCLUDING across all three quadrant seams (order 2 exercises A→B, B→C, C→D).
-- refl here is the correctness check on the A/D rotations.
hilbert-1-continuous : maxjump (hilbert 1) ≡ 1
hilbert-1-continuous = refl

hilbert-2-continuous : maxjump (hilbert 2) ≡ 1
hilbert-2-continuous = refl
