------------------------------------------------------------------------
-- Substrate.Category.Poly.Category (T8)
--
-- The graded-monoid structure of the poly term-algebra. With the term carrier
-- routed through the witness tower (PolyTerm = LehmerPath; _++ₚ_ = _⊕_), the
-- "category" is the graded monoid (PolyTerm, _++ₚ_, []ₚ) — a `GradedProductOver`
-- whose laws are the tower's OWN proofs (⊕-unit-left / ⊕-unit-right /
-- ⊕-assoc-over), not a bespoke `CategoryOf` re-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Category where

open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedAssocOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-assoc-over)

open import Substrate.Category.Poly.Term using (poly-product)

-- Associativity of composition = the tower's GradedAssocOver on the graded
-- product. Unit laws are OrientationSum.⊕-unit-left / OrientationSumLaws.⊕-unit-right.
poly-assoc : GradedAssocOver +-assoc poly-product
poly-assoc = ⊕-assoc-over
