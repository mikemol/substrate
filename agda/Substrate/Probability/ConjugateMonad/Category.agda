------------------------------------------------------------------------
-- Substrate.Probability.ConjugateMonad.Category (T18)
--
-- The graded-monoid structure of the conjugate-update term-algebra. With the
-- term carrier routed through the witness tower (ConjTerm = LehmerPath, the
-- free tower of combined generators; _++ᶜ_ = _⊕_), the "category" is the graded
-- monoid (ConjTerm, _++ᶜ_, []ᶜ) — a `GradedProductOver` whose laws are the
-- tower's OWN proofs (no re-proving):
--
--   * left unit    []ᶜ ++ᶜ t ≡ t                 — OrientationSum.⊕-unit-left (refl)
--   * right unit   t ++ᶜ []ᶜ ≡ t  (up to grade)  — OrientationSumLaws.⊕-unit-right
--   * associativity                              — ⊕-assoc-over (GradedAssocOver)
--
-- so the term-algebra IS a specialisation of `⊕-over` and inherits its monoid
-- laws verbatim, rather than a bespoke `CategoryOf` re-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.ConjugateMonad.Category where

open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedAssocOver)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties using (⊕-assoc-over)

open import Substrate.Probability.ConjugateMonad.Term using (conj-product)

-- Associativity of composition = the tower's GradedAssocOver on the graded
-- product (the additive associator of the orientation rig). The unit laws are
-- OrientationSum.⊕-unit-left / OrientationSumLaws.⊕-unit-right (see header).
conj-assoc : GradedAssocOver +-assoc conj-product
conj-assoc = ⊕-assoc-over
