------------------------------------------------------------------------
-- Substrate.Algebra.F2.FanoPlane
--
-- ℙ²(F₂) — the Fano plane: the projectivization of F₂³. Carries 7
-- points (= the 7 nonzero vectors of F₂³, since F₂* is trivial) and
-- 7 lines (= the 7 two-dimensional subspaces of F₂³, minus zero).
--
-- Built as the natural geometry for the Sylow-7 ↔ Singer cyclic
-- tricycles structural identification per
-- [[klein-quartic-kinematic-anatomy]]. The Singer cycle (multiplication
-- by a primitive root in F₈ = F₂[x]/(x³+x+1)) is the canonical order-7
-- element of GL(3, F₂); it permutes the 7 points (and the 7 lines) in
-- a single 7-cycle.
--
-- S2 of the multi-route equivariance arc per
-- [[multi-route-equivariance-recovery]]: provides the Sylow-7 carrier
-- + Singer cycle that S3 (GL3F2) wires into the full 168-element
-- group via the FieldFanOut architecture.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.FanoPlane where

open import Substrate.Foundation.Fin using (Fin) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector; basis; _+ⱽ_)
open import Substrate.Algebra.F2.Linear using (Linear)
open import Substrate.Algebra.F2.Linear.FromImages using (linear-from-images)

------------------------------------------------------------------------
-- 1. Points: 7 named constructors corresponding to the 7 nonzero
-- vectors of F₂³.
--
-- Naming convention: eᵢ = basis vector i; eᵢⱼ = basis i + basis j;
-- e₁₂₃ = sum of all three basis vectors.
------------------------------------------------------------------------

data Point : Set where
  e₁ e₂ e₃ e₁₂ e₁₃ e₂₃ e₁₂₃ : Point

------------------------------------------------------------------------
-- 2. Embedding: each point maps to its underlying F₂³ vector.
------------------------------------------------------------------------

point-to-vec : Point → Vector 3
point-to-vec e₁   = basis fz
point-to-vec e₂   = basis (fs fz)
point-to-vec e₃   = basis (fs (fs fz))
point-to-vec e₁₂  = basis fz +ⱽ basis (fs fz)
point-to-vec e₁₃  = basis fz +ⱽ basis (fs (fs fz))
point-to-vec e₂₃  = basis (fs fz) +ⱽ basis (fs (fs fz))
point-to-vec e₁₂₃ = basis fz +ⱽ (basis (fs fz) +ⱽ basis (fs (fs fz)))

------------------------------------------------------------------------
-- 3. Singer cycle: the canonical order-7 element of GL(3, F₂),
-- realised as multiplication by x in F₈ = F₂[x]/(x³+x+1).
--
-- Cycle:    1 → x → x² → x+1 → x²+x → x²+x+1 → x²+1 → 1
-- As points: e₁ → e₂ → e₃ → e₁₂ → e₂₃ → e₁₂₃ → e₁₃ → e₁
--
-- Verification: multiplication by x in F₂[x]/(x³+x+1):
--   1 ↦ x; x ↦ x²; x² ↦ x³ = x+1; (x+1) ↦ x²+x;
--   (x²+x) ↦ x³+x² = (x+1)+x² = x²+x+1;
--   (x²+x+1) ↦ x³+x²+x = (x+1)+x²+x = x²+1;
--   (x²+1) ↦ x³+x = (x+1)+x = 1.
------------------------------------------------------------------------

singer : Point → Point
singer e₁   = e₂
singer e₂   = e₃
singer e₃   = e₁₂
singer e₁₂  = e₂₃
singer e₂₃  = e₁₂₃
singer e₁₂₃ = e₁₃
singer e₁₃  = e₁

------------------------------------------------------------------------
-- 4. Singer is a 7-cycle: singer⁷ = id on every point.
------------------------------------------------------------------------

singer⁷ : Point → Point
singer⁷ p = singer (singer (singer (singer (singer (singer (singer p))))))

singer⁷-id : (p : Point) → singer⁷ p ≡ p
singer⁷-id e₁   = refl
singer⁷-id e₂   = refl
singer⁷-id e₃   = refl
singer⁷-id e₁₂  = refl
singer⁷-id e₁₃  = refl
singer⁷-id e₂₃  = refl
singer⁷-id e₁₂₃ = refl

------------------------------------------------------------------------
-- 5. Singer as an F₂-linear map: Vector 3 → Vector 3, via the basis
-- images
--
--   basis 0 = e₁ ↦ e₂   = basis 1
--   basis 1 = e₂ ↦ e₃   = basis 2
--   basis 2 = e₃ ↦ e₁₂  = basis 0 +ⱽ basis 1
--
-- The linear extension `singer-Linear = linear-from-images singer-basis`
-- coincides with the Singer-cycle action on every Point under
-- point-to-vec (`singer-Linear-on-Point` to land in a follow-on slice
-- if needed).
------------------------------------------------------------------------

singer-basis : Fin 3 → Vector 3
singer-basis fz                = basis (fs fz)
singer-basis (fs fz)           = basis (fs (fs fz))
singer-basis (fs (fs fz))      = basis fz +ⱽ basis (fs fz)

singer-Linear : Linear 3 3
singer-Linear = linear-from-images singer-basis

------------------------------------------------------------------------
-- 6. Lines: 7 named constructors corresponding to the 7 two-dim
-- subspaces of F₂³ (minus zero).
--
-- Each line is uniquely determined by any two of its three points;
-- the third is their sum (over F₂). The 7 lines:
--
--   L₁₂    = {e₁, e₂, e₁₂}      — basis (0,1) plane
--   L₁₃    = {e₁, e₃, e₁₃}      — basis (0,2) plane
--   L₂₃    = {e₂, e₃, e₂₃}      — basis (1,2) plane
--   L₁-₂₃  = {e₁,  e₂₃, e₁₂₃}   — basis 0 + (e₂+e₃) plane
--   L₂-₁₃  = {e₂,  e₁₃, e₁₂₃}   — basis 1 + (e₁+e₃) plane
--   L₃-₁₂  = {e₃,  e₁₂, e₁₂₃}   — basis 2 + (e₁+e₂) plane
--   L₁₂-₁₃ = {e₁₂, e₁₃, e₂₃}    — all-pairwise-sums line
------------------------------------------------------------------------

data FanoLine : Set where      -- ⟦shape:dcb2f19f L₁₂ L₁₃ L₂₃ L₁-₂₃ L₂-₁₃ L₃-₁₂ L₁₂-₁₃⟧
  L₁₂ L₁₃ L₂₃ L₁-₂₃ L₂-₁₃ L₃-₁₂ L₁₂-₁₃ : FanoLine

-- Line-points: the three points lying on each line.
line-points : FanoLine → Point × Point × Point
line-points L₁₂    = e₁ , e₂ , e₁₂
line-points L₁₃    = e₁ , e₃ , e₁₃
line-points L₂₃    = e₂ , e₃ , e₂₃
line-points L₁-₂₃  = e₁ , e₂₃ , e₁₂₃
line-points L₂-₁₃  = e₂ , e₁₃ , e₁₂₃
line-points L₃-₁₂  = e₃ , e₁₂ , e₁₂₃
line-points L₁₂-₁₃ = e₁₂ , e₁₃ , e₂₃

------------------------------------------------------------------------
-- 7. Singer action on lines: the Singer cycle permutes the 7 lines
-- in a single 7-cycle (compatibly with its action on points).
--
-- Cycle: L₁₂ → L₂₃ → L₃-₁₂ → L₁₂-₁₃ → L₁-₂₃ → L₂-₁₃ → L₁₃ → L₁₂
--
-- Verification: apply singer to each of the 3 points on each line and
-- recognise the result as another line's triple.
--   L₁₂   = {e₁,e₂,e₁₂}     ↦ {e₂,e₃,e₂₃}      = L₂₃
--   L₂₃   = {e₂,e₃,e₂₃}     ↦ {e₃,e₁₂,e₁₂₃}    = L₃-₁₂
--   L₃-₁₂ = {e₃,e₁₂,e₁₂₃}   ↦ {e₁₂,e₂₃,e₁₃}    = L₁₂-₁₃
--   L₁₂-₁₃= {e₁₂,e₁₃,e₂₃}   ↦ {e₂₃,e₁,e₁₂₃}    = L₁-₂₃
--   L₁-₂₃ = {e₁,e₂₃,e₁₂₃}   ↦ {e₂,e₁₂₃,e₁₃}    = L₂-₁₃
--   L₂-₁₃ = {e₂,e₁₃,e₁₂₃}   ↦ {e₃,e₁,e₁₃}      = L₁₃
--   L₁₃   = {e₁,e₃,e₁₃}     ↦ {e₂,e₁₂,e₁}      = L₁₂
------------------------------------------------------------------------

singer-line : FanoLine → FanoLine
singer-line L₁₂    = L₂₃
singer-line L₂₃    = L₃-₁₂
singer-line L₃-₁₂  = L₁₂-₁₃
singer-line L₁₂-₁₃ = L₁-₂₃
singer-line L₁-₂₃  = L₂-₁₃
singer-line L₂-₁₃  = L₁₃
singer-line L₁₃    = L₁₂

singer-line⁷ : FanoLine → FanoLine
singer-line⁷ l =
  singer-line (singer-line (singer-line (singer-line
   (singer-line (singer-line (singer-line l))))))

singer-line⁷-id : (l : FanoLine) → singer-line⁷ l ≡ l
singer-line⁷-id L₁₂    = refl
singer-line⁷-id L₁₃    = refl
singer-line⁷-id L₂₃    = refl
singer-line⁷-id L₁-₂₃  = refl
singer-line⁷-id L₂-₁₃  = refl
singer-line⁷-id L₃-₁₂  = refl
singer-line⁷-id L₁₂-₁₃ = refl
