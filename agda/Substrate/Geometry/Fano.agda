------------------------------------------------------------------------
-- Substrate.Geometry.Fano
--
-- M-9 of the Cocycles structural-migration plan. The Fano plane
-- PG(2, 2) — the projective plane over F₂. 7 points, 7 lines, each
-- line has 3 points, each point on 3 lines. The smallest projective
-- plane.
--
-- Structural definition:
--   * Points = the 7 nonzero vectors of F₂³ (= columns of the Hamming
--     [7, 4, 3] parity-check matrix from M-7).
--   * Lines = the 7 hyperplanes through the origin in F₂³
--     (equivalently: the 7 codewords of weight 3 in the simplex code,
--     = the 7 codewords of weight 4 in RM(1, 3) excluding the
--     all-ones).
--   * Incidence: a point p lies on a line ℓ iff p ⋅ ℓ ≡ 𝟘 (dot
--     product over F₂); equivalently, 3 collinear points sum to 𝟘.
--
-- The collinearity relation `Collinear-Three` is the structural
-- primitive — it makes the Fano plane derivable from F₂ arithmetic,
-- not from a hand-enumerated incidence table.
--
-- The reason all 7 `line-i-j-k : Collinear-Three pᵢ pⱼ pₖ` proofs
-- close by `refl`: each Fano line is itself a 2-dim F₂-subspace of
-- F₂³, and its 3 collinear points are the V4-Nonzero of that
-- subspace. The "4th point" (= 𝟎ⱽ, off the Fano plane) is the
-- parity of the 3 — i.e., (p₁ +ⱽ p₂) +ⱽ p₃ ≡ 𝟎ⱽ by F₂² Klein-four
-- parity. The 3+1 parity pattern recurs at OrbitKey (6+2 in F₂³),
-- Live/Reserved (24+8 in F₂⁵), and extended Hamming's parity bit
-- — see memory `project_3plus1_parity_universal`.
--
-- Connection to the rest of the migration:
--   * Points of Fano = columns of Hamming H (M-7).
--   * Lines of Fano = codewords of weight 4 in RM(1, 3) excluding
--     the all-ones (M-6).
--   * Self-dual incidence structure (point ↔ line duality).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.Fano where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅; ₆; ₇)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Codes.Hamming.H-7-4-3 using (H-cols)

------------------------------------------------------------------------
-- Points.
--
-- A Fano point is identified by its column-position in the Hamming
-- parity-check matrix (= a Fin 7). The corresponding F₂³ vector is
-- recovered via H-cols.
------------------------------------------------------------------------

Point : Set
Point = Fin 7

point-coords : Point → Vector 3
point-coords = H-cols

------------------------------------------------------------------------
-- Collinearity.
--
-- Three points p₁, p₂, p₃ are collinear iff their F₂³ coordinates
-- sum to 𝟎ⱽ.
--
-- This is the structural definition: collinearity is reduced to F₂
-- arithmetic on the points' coordinates. No incidence table.
------------------------------------------------------------------------

Collinear-Three : Point → Point → Point → Set
Collinear-Three p₁ p₂ p₃ =
  ((point-coords p₁ +ⱽ point-coords p₂) +ⱽ point-coords p₃) ≡ 𝟎ⱽ

------------------------------------------------------------------------
-- The 7 lines of the Fano plane, each as a triple of collinear points.
--
-- The 7 lines (under our H-cols ordering = LSB-first binary indexing):
--   {1, 2, 3}  : (1,0,0) + (0,1,0) + (1,1,0) = 𝟎ⱽ
--   {1, 4, 5}  : (1,0,0) + (0,0,1) + (1,0,1) = 𝟎ⱽ
--   {1, 6, 7}  : (1,0,0) + (0,1,1) + (1,1,1) = 𝟎ⱽ
--   {2, 4, 6}  : (0,1,0) + (0,0,1) + (0,1,1) = 𝟎ⱽ
--   {2, 5, 7}  : (0,1,0) + (1,0,1) + (1,1,1) = 𝟎ⱽ
--   {3, 4, 7}  : (1,1,0) + (0,0,1) + (1,1,1) = 𝟎ⱽ
--   {3, 5, 6}  : (1,1,0) + (1,0,1) + (0,1,1) = 𝟎ⱽ
--
-- (Index notation: 1..7 in the catalog ↔ Fin 7 zero..fin-6 here,
-- 0-indexed.)
------------------------------------------------------------------------

open import Substrate.Foundation.Fin.Fin

-- 1 = Fin index 0, 2 = Fin index 1, ..., 7 = Fin index 6.
p₁ p₂ p₃ p₄ p₅ p₆ p₇ : Point
p₁ = zero
p₂ = suc zero
p₃ = suc ₁
p₄ = suc ₂
p₅ = suc ₃
p₆ = suc ₄
p₇ = suc ₅

line-1-2-3 : Collinear-Three p₁ p₂ p₃
line-1-2-3 = refl

line-1-4-5 : Collinear-Three p₁ p₄ p₅
line-1-4-5 = refl

line-1-6-7 : Collinear-Three p₁ p₆ p₇
line-1-6-7 = refl

line-2-4-6 : Collinear-Three p₂ p₄ p₆
line-2-4-6 = refl

line-2-5-7 : Collinear-Three p₂ p₅ p₇
line-2-5-7 = refl

line-3-4-7 : Collinear-Three p₃ p₄ p₇
line-3-4-7 = refl

line-3-5-6 : Collinear-Three p₃ p₅ p₆
line-3-5-6 = refl
