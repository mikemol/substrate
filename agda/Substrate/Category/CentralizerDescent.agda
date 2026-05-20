------------------------------------------------------------------------
-- Substrate.Category.CentralizerDescent
--
-- The recursive centralizer-of primitive: given a ConjugationCoalgebra
-- G and a class c, the centralizer C_G(rep c) is itself a
-- ConjugationCoalgebra. Iteratively applying gives the Happy Family
-- hierarchy from the Monster (Baby Monster = C_M(2A involution)/⟨z⟩;
-- Conway / Fischer / Mathieu groups via further descent).
--
-- V1 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Sub-arc V (Centralizer descent / Happy Family) foundation.
--
-- Per [[expose-generator-not-orbit]]: the centralizer descent is the
-- structural mechanism for the entire Happy Family — each sporadic
-- subquotient is named via its position in the descent tree, not by
-- enumerating its elements.
--
-- Per [[categorical-name-first]]: "centralizer" / "centralizer
-- descent" / "subquotient" — standard categorical / group-theoretic
-- naming.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CentralizerDescent where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The CentralizerDescent record.
--
-- Bundles:
--   * base : the original ConjugationCoalgebra (= "outer" group G)
--   * target-class : the class c in base whose centralizer we descend to
--   * descent : the ConjugationCoalgebra for C_G(rep c) (= "inner" group)
--   * embed : G_descent → G_base (the centralizer's elements embed
--     into G as elements that commute with rep target-class)
--   * centralizes : axiom — every element of G_descent (via embed)
--     commutes with rep base target-class
--
-- The descent ITSELF is supplied as a parameter — the substrate
-- primitive provides the structural record, not the constructive
-- existence of centralizers (which depends on G's specific structure).
-- This matches substrate's convention: primitives package structure;
-- constructive existence supplied per-instance.
------------------------------------------------------------------------

record CentralizerDescent : Set (lsuc ℓ) where
  constructor mkCentralizerDescent
  field
    base         : ConjugationCoalgebra {ℓ}
    descent      : ConjugationCoalgebra {ℓ}

  open ConjugationCoalgebra base
    renaming (G to G-base; _·_ to _·b_; _⁻¹ to _⁻¹b; Class to Class-base; rep to rep-base)
  open ConjugationCoalgebra descent
    renaming (G to G-descent)

  field
    target-class : Class-base
    embed        : G-descent → G-base
    -- Centralization axiom: embedded descent elements commute with
    -- the target-class representative.
    centralizes  : (h : G-descent) →
                   ((embed h) ·b (rep-base target-class)) ≡
                   ((rep-base target-class) ·b (embed h))

------------------------------------------------------------------------
-- Capstone — descent primitive in place.
--
-- V1 of the 20-slice arc. With V1 landed, the Happy Family
-- hierarchy is expressible as a chain of CentralizerDescent values:
--
--   M (Monster, T8) ─── descent at 2A class ───→ 2·B (BabyMonster cover)
--   2·B ─── quotient by ⟨z⟩ ───→ B (BabyMonster, V2 next slice)
--   M ─── descent at 2B class ───→ 2^(1+24).Co₁
--   ... etc.
--
-- Per [[shadow-architecture]]: this is the foundational primitive
-- for V2-V5 (BabyMonster, Conway, Mathieu/Fischer, HappyFamily
-- capstone). Each sporadic subquotient becomes a named
-- CentralizerDescent instance (with the descent CCA supplied per-
-- instance from ATLAS / CFSG-cited data).
--
-- Quotient operation (= dividing by ⟨z⟩ for BabyMonster) is a
-- separate primitive (CentralizerQuotient as future follow-on); V1
-- handles the descent step only.
------------------------------------------------------------------------
