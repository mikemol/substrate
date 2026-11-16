------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.SkiProduct
--
-- Defines: ski-product
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.SkiProduct where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Shed
-- ⚑ THE CONSTRUCTORS COME FROM `Tm`, NOT THROUGH `Shed`. This leaf uses `I` and
-- `_∙_` directly; `Shed` imports `Tm` but does not re-export it (the split emits
-- bare, non-public imports by design — Ⓡ1), so the constructor is out of scope
-- one hop away. A split leaf needs every name it MENTIONS, not only the ones its
-- direct dependency's TYPE mentions.
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



------------------------------------------------------------------------
-- 2. THE SKI GradedProduct: C n = Shed n; u = the grade-0 shed (a normal form,
-- cost 0, peeled = a fixed nf marker); _∧_ = chain two sheds, grades ADDING (the
-- total cost accumulates). This IS the two-index braiding chained: grade = Σ cost.
------------------------------------------------------------------------
-- ⟡set1-paydown: GradedProduct's carrier family is now its param (Shed).
ski-product : GradedProduct Shed
ski-product = record
  { u   = shed⟨ I ⟩                                   -- grade-0 unit: the trivial nf shed
  ; _∧_ = λ {i}{j} s t → shed⟨ peeled s ∙ peeled t ⟩  -- chain: grade i+j, rebuild structure
  }
