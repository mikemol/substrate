------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Category (T5)
--
-- The graded-monoid structure of the stochastic-lens term-algebra. With the
-- term carrier routed through the witness tower (LensTerm = LehmerPath; _++ₗ_ =
-- _⊕_), the "category" is the graded monoid (LensTerm, _++ₗ_, []ₗ) — a
-- `GradedProductOver` whose laws are the tower's OWN proofs (⊕-unit-left /
-- ⊕-unit-right / ⊕-assoc-over), not a bespoke `CategoryOf` re-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Category where

open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedAssocOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-assoc-over)

open import Substrate.Category.StochasticLens.Term using (lens-product)

-- Associativity of composition = the tower's GradedAssocOver on the graded
-- product. Unit laws are OrientationSum.⊕-unit-left / OrientationSumLaws.⊕-unit-right.
lens-assoc : GradedAssocOver +-assoc lens-product
lens-assoc = ⊕-assoc-over
