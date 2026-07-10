------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationBimonoidal
--
-- ⟡rig-11 — THE UNIFYING FRAME (the generic record). The recursive-common-structure
-- endpoint of the whole arc: ⊕ and ⊗ are ONE structure — a graded product over a grading
-- MONOID — differing only in the grading (ℕ,+,0) vs (ℕ,·,1).
--
--   GradedProductOver (op)(ε)(C) = { u : C ε ; _∧_ : C i → C j → C (op i j) }
--
-- The existing Algebra.Wedge.Product.GradedProduct is exactly GradedProductOver _+_ 0.
-- This module is PROOF-FREE (def/proof separation): the concrete instances (⊕-over,
-- ⊗-over) and the fact that both associators instantiate the ONE generic law live in
-- .Properties. The full four-law table (assoc/unit/comm-iso/comm-nat on both fibres, all
-- proven this arc) is documented there.
--
-- (Reuse-search catalog.db: no bimonoidal/rig-category record exists; Category.Symmetric-
-- Monoidal needs a full CategoryOf of orderings — heavier.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationBimonoidal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; subst)

------------------------------------------------------------------------
-- The parameterized structure: a graded product over a grading operation (op, ε).
------------------------------------------------------------------------

record GradedProductOver (op : ℕ → ℕ → ℕ) (ε : ℕ) (C : ℕ → Set) : Set where
  field
    u   : C ε
    _∧_ : {i j : ℕ} → C i → C j → C (op i j)

open GradedProductOver public

-- the generic associativity law-type over the grading operation's own associativity.
GradedAssocOver : {op : ℕ → ℕ → ℕ} {ε : ℕ} {C : ℕ → Set}
                  (assoc : (x y z : ℕ) → op (op x y) z ≡ op x (op y z))
                  (P : GradedProductOver op ε C) → Set
GradedAssocOver {C = C} assoc P =
  ∀ {i j k} (a : C i) (b : C j) (c : C k) →
  subst C (assoc i j k) (_∧_ P (_∧_ P a b) c) ≡ _∧_ P a (_∧_ P b c)
