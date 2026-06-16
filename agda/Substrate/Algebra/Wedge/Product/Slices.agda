------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.Slices
--
-- SLICE 2: "you actually get three DivStr, one for each degree of freedom"
-- (user). The wedge product _∧_ : C i → C j → C (i+j) has three grade DOF (the
-- two input grades and the one output grade). Each WAY OF HANDLING the grade
-- gives a different DivStr-shaped structure — the trichotomy:
--
--   * slice-step    — grade DOF STEPPING BY 1: the +1-step GradedDivStr
--                     (graded-of-product) — each step wedges a grade-1 increment.
--   * slice-flat    — grade DOF FOLDED INTO THE CARRIER: the flattened plain
--                     DivStr (Σ ℕ C); the count is the GRADE component of the
--                     carrier-element quotient ("flattening folded into the
--                     residue", count-as-grade).
--
-- (RETIRED under the recon : C→C→C→C pivot: `slice-scalar` — the grade-FORCED-TO-0
--  plain DivStr. Its quotient lives at grade 0 (`C P 0`), which carries no grade
--  to host the count, so the count-as-grade reading has nowhere to land there;
--  the grade-0 count was a frozen coordinate with no carrier-representative form.
--  It had no consumers. The genuine grade-0 structure survives as `slice-step` /
--  the GradedProduct itself — [[feedback_coordinate_to_geometry]].)
--
-- One wedge product, two surviving DivStr — the grade DOF stepped or folded.
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
-- SLICE B — grade steps by 1: the +1-step GradedDivStr.
------------------------------------------------------------------------

slice-step : GradedProduct → GradedDivStr
slice-step = graded-of-product

------------------------------------------------------------------------
-- SLICE C — grade folded into the carrier: the flattened plain DivStr.
------------------------------------------------------------------------

slice-flat : GradedProduct → DivStr
slice-flat = flatten
