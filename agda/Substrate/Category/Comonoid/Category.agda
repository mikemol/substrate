------------------------------------------------------------------------
-- Substrate.Category.Comonoid.Category (T13)
--
-- The graded-monoid structure of the comonoid term-algebra. With the term
-- carrier routed through the witness tower (ComonoidTerm = LehmerPath; _++c_ =
-- _⊕_), the "category" is the graded monoid (ComonoidTerm, _++c_, []c) — a
-- `GradedProductOver` whose laws are the tower's OWN proofs (⊕-unit-left /
-- ⊕-unit-right / ⊕-assoc-over), not a bespoke `CategoryOf` re-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonoid.Category where

open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedAssocOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-assoc-over)

open import Substrate.Category.Comonoid.Term using (comonoid-product)

-- Associativity of composition = the tower's GradedAssocOver on the graded
-- product. Unit laws are OrientationSum.⊕-unit-left / OrientationSumLaws.⊕-unit-right.
comonoid-assoc : GradedAssocOver +-assoc comonoid-product
comonoid-assoc = ⊕-assoc-over
