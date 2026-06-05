------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.Slices
--
-- SLICE 2: "you actually get three DivStr, one for each degree of freedom"
-- (user). The wedge product _∧_ : C i → C j → C (i+j) has three grade DOF (the
-- two input grades and the one output grade). Each WAY OF HANDLING the grade
-- gives a different DivStr-shaped structure — the trichotomy:
--
--   * slice-scalar  — grade DOF FORCED TO 0: the grade-0 part (the scalars) is a
--                     plain DivStr in its own right (q copies stay at grade 0,
--                     since 0 + 0 = 0). "DivStr = GradedDivStr with a DOF forced
--                     to zero", most literally.
--   * slice-step    — grade DOF STEPPING BY 1: the +1-step GradedDivStr
--                     (graded-of-product) — each step wedges a grade-1 increment.
--   * slice-flat    — grade DOF FOLDED INTO THE CARRIER: the flattened plain
--                     DivStr (Σ ℕ C), the grade absorbed as data ("flattening
--                     folded into the residue").
--
-- One wedge product, three DivStr — the grade DOF fixed, stepped, or folded.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product.Slices where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; C; u; _∧_; graded-of-product; flatten)

------------------------------------------------------------------------
-- power at grade 0 — q copies of a grade-0 element, staying at grade 0
-- (0 + 0 = 0 definitionally, so no q*0 transport).
------------------------------------------------------------------------

power₀ : (P : GradedProduct) → C P 0 → ℕ → C P 0
power₀ P b zero    = u P
power₀ P b (suc n) = _∧_ P b (power₀ P b n)

------------------------------------------------------------------------
-- SLICE A — grade forced to 0: the scalar part is a plain DivStr.
------------------------------------------------------------------------

slice-scalar : GradedProduct → DivStr
slice-scalar P = record
  { C = C P 0 ; z = u P ; recon = λ q b r → _∧_ P (power₀ P b q) r }

------------------------------------------------------------------------
-- SLICE B — grade steps by 1: the +1-step GradedDivStr.
------------------------------------------------------------------------

slice-step : GradedProduct → GradedDivStr
slice-step = graded-of-product

------------------------------------------------------------------------
-- SLICE C — grade folded into the carrier: the flattened plain DivStr.
------------------------------------------------------------------------

slice-flat : GradedProduct → DivStr
slice-flat = flatten
