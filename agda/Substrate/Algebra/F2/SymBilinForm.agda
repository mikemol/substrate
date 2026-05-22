------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm
--
-- The n-parametric symmetric bilinear form on F₂ⁿ — the categorical
-- fixed point of the substrate's metric-gauge work. File-per-lemma:
--
--   SymBilinForm.BilinForm           — general (not nec. symmetric) form
--   SymBilinForm.IsSymmetric         — symmetry predicate
--   SymBilinForm.Type                — SymBilinForm n + projections
--   SymBilinForm.BilinearFormOf      — Σᵢ vᵢ · Σⱼ M(i,j) · wⱼ
--   SymBilinForm.MetricId            — n-parametric diagonal identity
--   SymBilinForm.MetricIdSymmetric   — proof metric-id is symmetric
--   SymBilinForm.MetricIdSym         — metric-id packaged as SymBilinForm
--   SymBilinForm.CongruenceAct       — generic T^T M T action
--   SymBilinForm.PairEqFamily        — per-w equalizer family
--   SymBilinForm.Radical             — Wide-Meet of pair-eq-family
--   SymBilinForm.NonDegenerate       — kernel-free predicate
--
-- After this decomposition: the language for metric-gauge work is the
-- categorical primitive layer. Adding dim n requires zero new
-- infrastructure; bilinear-form-of metric-id v w at any n is the
-- generic dot product; NonDegenerate M at any n is the categorical
-- predicate.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm where

open import Substrate.Algebra.F2.SymBilinForm.BilinForm          public
open import Substrate.Algebra.F2.SymBilinForm.IsSymmetric        public
open import Substrate.Algebra.F2.SymBilinForm.Type               public
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf     public
open import Substrate.Algebra.F2.SymBilinForm.MetricId           public
open import Substrate.Algebra.F2.SymBilinForm.MetricIdSymmetric  public
open import Substrate.Algebra.F2.SymBilinForm.MetricIdSym        public
open import Substrate.Algebra.F2.SymBilinForm.CongruenceAct      public
open import Substrate.Algebra.F2.SymBilinForm.PairEqFamily       public
open import Substrate.Algebra.F2.SymBilinForm.Radical            public
open import Substrate.Algebra.F2.SymBilinForm.NonDegenerate      public
