------------------------------------------------------------------------
-- Substrate.FUSep.FUSepConv.EqSetoid
--
-- Defines: EqSetoid, refl≈, sym≈, trans≈
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepConv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepConv.EqSetoid where

open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- A SETOID: a carrier with an equivalence — the HetQ packaging. Bundling the
-- relation + its laws into ONE record is what avoids the mixfix/parameter
-- threading; the coincidence below takes TWO setoids over one carrier (the
-- finite ≈ side and the coinductive ≋ side) plus an observation.
------------------------------------------------------------------------
-- ⟡set1-paydown: parameterize the relation _≈_ : C → C → Set out of the record
-- (substrate stance: the carrier AND its relation are params, never fields). C was
-- already a record param; _≈_ joins it, so the record drops from Set₁ to Set.
-- Consumers write `EqSetoid C _≈_`; projection calls (`trans≈ Fin`) are unchanged.
record EqSetoid (C : Set) (_≈_ : C → C → Set) : Set where  -- cluster-local bundled setoid (refl≈/sym≈/trans≈); distinct-shape from Algebra.Setoid, pinned
  field
    refl≈ : ∀ {a} → a ≈ a
    sym≈  : ∀ {a b} → a ≈ b → b ≈ a
    trans≈ : ∀ {a b c} → a ≈ b → b ≈ c → a ≈ c
open EqSetoid public
