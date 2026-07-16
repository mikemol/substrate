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

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

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

record CentralizerDescent
  (G-base : Set ℓ) (_·b_ : G-base → G-base → G-base) (εb : G-base) (_⁻¹b : G-base → G-base)
  (Class-base : Set ℓ) (rep-base : Class-base → G-base) (in-class-base : Class-base → G-base → Set ℓ)
  (G-descent : Set ℓ) (_·d_ : G-descent → G-descent → G-descent) (εd : G-descent) (_⁻¹d : G-descent → G-descent)
  (Class-descent : Set ℓ) (rep-descent : Class-descent → G-descent) (in-class-descent : Class-descent → G-descent → Set ℓ)
  -- ⟡set1-rp-descenttree: Set (lsuc ℓ) → Set ℓ — the lsuc was STALE (a leftover from before
  -- ConjugationCoalgebra was parameterized): every field now lands at level ℓ, so the record does too.
  : Set ℓ where
  constructor mkCentralizerDescent
  field
    base         : ConjugationCoalgebra G-base _·b_ εb _⁻¹b Class-base rep-base in-class-base
    descent      : ConjugationCoalgebra G-descent _·d_ εd _⁻¹d Class-descent rep-descent in-class-descent

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
