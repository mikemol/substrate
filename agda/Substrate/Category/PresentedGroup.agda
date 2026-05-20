------------------------------------------------------------------------
-- Substrate.Category.PresentedGroup
--
-- A group whose carrier may not admit a computable normal form, so
-- equality is replaced by a propositional equivalence ∼. The "bottom-
-- up" side of the Galois adjunction in the prime-factored-gauge arc.
--
-- Generalises the substrate's Coxeter framework: every Coxeter
-- instance (via Coxeter.Core) IS a PresentedGroup (with ∼ = ≡ on
-- normalize); but PresentedGroup also admits instances where
-- normalize doesn't exist or is intractable — e.g., the Monster's
-- Y₅₅₅ + spider presentation (per
-- [[prime-factored-gauge-arc]] T8).
--
-- Per [[universal-property-discipline]] +
-- [[categorical-name-first]]: this IS the standard "presented group"
-- = ⟨generators | relations⟩ construction at the categorical level.
-- The substrate's universal version takes the equivalence relation
-- as a parameter rather than fixing propositional equality, which
-- side-steps the funext / decidable-equality issues that arise for
-- groups without computable normal forms.
--
-- Per [[roll-our-own-via-word-algebra]]: the substrate's existing
-- Word algebra (Substrate.Groups.Coxeter.Word) is the natural Carrier
-- for most PresentedGroup instances; this primitive abstracts away
-- the Carrier shape so non-Word carriers also work (e.g., elements
-- of a vertex operator algebra acting via Aut(V♮)).
--
-- T2 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. Foundation for T4
-- (GaloisAdjunction); without T2 the bottom-up direction of the
-- adjunction has no abstract target.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PresentedGroup where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The PresentedGroup record.
--
-- Bundles a group's data + axioms up to a custom equivalence ∼:
--   * Carrier  : the underlying set (often Word or FreeGroup-like)
--   * _·_      : binary operation
--   * ε        : identity element
--   * _⁻¹      : inverse operation
--   * _∼_      : the equivalence relation (= equality in the quotient)
--   * Equivalence axioms (refl, sym, trans)
--   * Group laws up to ∼ (assoc, identityˡ, identityʳ, inv-leftˡ,
--     inv-rightʳ)
--   * Congruences (·-cong, ⁻¹-cong)
--
-- This is everything needed for a group whose Carrier doesn't have a
-- computable normal form. For Carriers WITH computable normal forms,
-- the Coxeter framework's Core is the more ergonomic primitive (it
-- derives _≈_ as ≡ on normalize); PresentedGroup is the strictly-
-- more-general fallback.
------------------------------------------------------------------------

record PresentedGroup : Set (lsuc ℓ) where
  constructor mkPresentedGroup
  field
    Carrier      : Set ℓ
    _·_          : Carrier → Carrier → Carrier
    ε            : Carrier
    _⁻¹          : Carrier → Carrier
    _∼_          : Carrier → Carrier → Set ℓ

    -- Equivalence axioms.
    ∼-refl       : (a : Carrier) → a ∼ a
    ∼-sym        : {a b : Carrier} → a ∼ b → b ∼ a
    ∼-trans      : {a b c : Carrier} → a ∼ b → b ∼ c → a ∼ c

    -- Group laws up to ∼.
    ∼-assoc      : (a b c : Carrier) → ((a · b) · c) ∼ (a · (b · c))
    ∼-identityˡ  : (a : Carrier) → (ε · a) ∼ a
    ∼-identityʳ  : (a : Carrier) → (a · ε) ∼ a
    ∼-inv-leftˡ  : (a : Carrier) → ((a ⁻¹) · a) ∼ ε
    ∼-inv-rightʳ : (a : Carrier) → (a · (a ⁻¹)) ∼ ε

    -- Congruences.
    ∼-cong-·     : {a a' b b' : Carrier} → a ∼ a' → b ∼ b' → (a · b) ∼ (a' · b')
    ∼-cong-⁻¹    : {a a' : Carrier} → a ∼ a' → (a ⁻¹) ∼ (a' ⁻¹)

------------------------------------------------------------------------
-- Capstone — primitive in place.
--
-- T2 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. With T2 landed, T3
-- (ConjugationCoalgebra) gives the top-down view; T4 (GaloisAdjunction)
-- connects the two; T8 (Monster) becomes possible via top-down without
-- needing a tractable Word algebra at Monster scale.
--
-- Concrete instances expected:
--   * Any Coxeter instance via the existing GroupAdapter (with ∼ = ≡
--     on normalize); follows mechanically from Coxeter.Core's outputs.
--   * The Monster as ⟨Y₅₅₅ + spider relation⟩; equality propositional,
--     no normalize required.
--   * Any finitely-presented group from group theory literature; data
--     entry from the citation.
--
-- Per [[shadow-architecture]]: T2 is DBE-foundational. Each
-- subsequent instance is a separate (small) slice.
--
-- Per [[expose-generator-not-orbit]]: PresentedGroup exposes
-- generators + relations (the "generator" side) without enumerating
-- the group's elements (the "orbit" side).
------------------------------------------------------------------------
