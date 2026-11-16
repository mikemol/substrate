------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.CostLeaf
--
-- Defines: cost-leaf
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.CostLeaf where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost
open import Substrate.Algebra.R.Trace.SKIShedDuality.SkiProduct
open import Substrate.Algebra.R.Trace.SKIShedDuality.Chain
-- ⚑ `shed⟨_⟩` IS A RECORD CONSTRUCTOR — the same seed blindness as SkiProduct's `I`/`_∙_`,
-- one shape further out. A peer's measurement named this exact case: `--provides …Shed`
-- returns `Shed · peeled · shed⟨ · shed⟨_⟩ · ⟩`, so the leaf exports the record, its FIELD
-- and its CONSTRUCTOR — and a `-- Defines: Shed` header shows only the first. A fix scoped
-- to datatype constructors alone would have caught SkiProduct and missed this file.
open import Substrate.Algebra.R.Trace.SKIShedDuality.Shed



-- THE AUTOCHAIN LEAF: a shed of term t, its grade wired to the ACTUAL cost t (not
-- a hand-specified 1). Chain (cost t) — the cost is READ from the term, automatic.
cost-leaf : (t : Tm) → Chain (cost t)
cost-leaf t = leaf {P = ski-product} {i = cost t} (shed⟨ t ⟩)
