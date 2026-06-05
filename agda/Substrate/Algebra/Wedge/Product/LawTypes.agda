------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.LawTypes
--
-- The graded-law PREDICATES (types only) over a GradedProduct:
-- GradedAssoc / GradedUnitˡ / GradedUnitʳ. Separated from Product.Laws (which
-- holds the PROOFS and the flatten construction) so that a law-bundling
-- record — Graded.MonoidalAdjunction's GradedMonoidalAdjunction, whose fields
-- ARE these predicates — can import the field types WITHOUT importing a proof
-- module (def/proof separation policy; see scratch/def_proof_separation_policy.md).
--
-- A predicate-only module (no data/record of its own): importing a *.Properties
-- here is fine, and a def-provider may import THIS.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product.LawTypes where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc; +-identityʳ)
open import Substrate.Foundation.Eq using (_≡_; subst)
open import Substrate.Algebra.Wedge.Product using (GradedProduct; C; u; _∧_)

-- A GradedProduct P satisfies the graded monoid laws iff it provides these
-- three. The left unit is definitional (u ∧ a : C (0 + i) = C i).

GradedAssoc : GradedProduct → Set
GradedAssoc P = {i j k : ℕ} (a : C P i) (b : C P j) (c : C P k) →
                subst (C P) (+-assoc i j k) (_∧_ P (_∧_ P a b) c) ≡ _∧_ P a (_∧_ P b c)

GradedUnitˡ : GradedProduct → Set
GradedUnitˡ P = {i : ℕ} (a : C P i) → _∧_ P (u P) a ≡ a

GradedUnitʳ : GradedProduct → Set
GradedUnitʳ P = {i : ℕ} (a : C P i) →
                subst (C P) (+-identityʳ i) (_∧_ P a (u P)) ≡ a
