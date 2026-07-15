------------------------------------------------------------------------
-- Substrate.Category.CascadedCoalgebra.Category (T16)
--
-- The graded-monoid structure of the cascade term-algebra. With the term
-- carrier routed through the witness tower (CascadeTerm = LehmerPath; _++ᶜᶜ_ =
-- _⊕_), the "category" is the graded monoid (CascadeTerm, _++ᶜᶜ_, []ᶜᶜ) — a
-- `GradedProductOver` whose laws are the tower's OWN proofs (⊕-unit-left /
-- ⊕-unit-right / ⊕-assoc-over), not a bespoke `CategoryOf` re-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CascadedCoalgebra.Category where

open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedAssocOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-assoc-over)

open import Substrate.Category.CascadedCoalgebra.Term using (cascade-product)

-- Associativity of composition = the tower's GradedAssocOver on the graded
-- product. Unit laws are OrientationSum.⊕-unit-left / OrientationSumLaws.⊕-unit-right.
cascade-assoc : GradedAssocOver +-assoc cascade-product
cascade-assoc = ⊕-assoc-over
