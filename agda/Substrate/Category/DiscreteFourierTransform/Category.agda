------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Category (T20)
--
-- The graded-monoid structure of the DFT term-algebra. With the term carrier
-- routed through the witness tower (DFTTerm = LehmerPath; _++ᶠ_ = _⊕_), the
-- "category" is the graded monoid (DFTTerm, _++ᶠ_, []ᶠ) — a `GradedProductOver`
-- whose laws are the tower's OWN proofs (⊕-unit-left / ⊕-unit-right / ⊕-assoc-over),
-- not a bespoke `CategoryOf` re-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Category where

open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedAssocOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-assoc-over)

open import Substrate.Category.DiscreteFourierTransform.Term using (dft-product)

-- Associativity of composition = the tower's GradedAssocOver on the graded
-- product. Unit laws are OrientationSum.⊕-unit-left / OrientationSumLaws.⊕-unit-right.
dft-assoc : GradedAssocOver +-assoc dft-product
dft-assoc = ⊕-assoc-over
