------------------------------------------------------------------------
-- Substrate.Linguistic.MorphismSetoid
--
-- Set3 of the Setoid sibling tower per [scratch/m_mod_arc_plan.md].
--
-- Equips `LanguageMorphism L₁ L₂` with a Setoid: lifts the existing
-- `_≈M_` from Substrate.Linguistic.CategoryLaws (Y4) to a full
-- Setoid record by supplying the missing symmetry + transitivity
-- witnesses.
--
-- The substrate's B-arc IsNatural respect-≈M gap is closed
-- structurally: any function that respects this equivalence IS a
-- SetoidMap (Set2). Set4 lifts natural-transformation respect to
-- this Setoid; Set5 lifts the Yoneda embedding's respect-≈M
-- obligation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.MorphismSetoid where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; Basis; FreeCarrier)
open import Substrate.Linguistic.Morphism
  using (LanguageMorphism; basis-map; carrier-map)
open import Substrate.Linguistic.CategoryLaws
  using (_≈M_; basis-≈; carrier-≈; ≈M-refl)
open import Substrate.Algebra.Setoid using (Setoid)

------------------------------------------------------------------------
-- 1. Symmetry of _≈M_.
------------------------------------------------------------------------

≈M-sym :
  {L₁ L₂ : LanguageWitness}
  {f g : LanguageMorphism L₁ L₂} →
  f ≈M g → g ≈M f
≈M-sym fg = record
  { basis-≈   = λ b → sym (basis-≈   fg b)
  ; carrier-≈ = λ x → sym (carrier-≈ fg x)
  }

------------------------------------------------------------------------
-- 2. Transitivity of _≈M_.
------------------------------------------------------------------------

≈M-trans :
  {L₁ L₂ : LanguageWitness}
  {f g h : LanguageMorphism L₁ L₂} →
  f ≈M g → g ≈M h → f ≈M h
≈M-trans fg gh = record
  { basis-≈   = λ b → trans (basis-≈   fg b) (basis-≈   gh b)
  ; carrier-≈ = λ x → trans (carrier-≈ fg x) (carrier-≈ gh x)
  }

------------------------------------------------------------------------
-- 3. The Setoid on LanguageMorphism L₁ L₂.
------------------------------------------------------------------------

LangMor-Setoid :
  (L₁ L₂ : LanguageWitness) → Setoid (LanguageMorphism L₁ L₂)
LangMor-Setoid L₁ L₂ = record
  { _≈_     = _≈M_
  ; ≈-refl  = λ _ → ≈M-refl
  ; ≈-sym   = ≈M-sym
  ; ≈-trans = ≈M-trans
  }

------------------------------------------------------------------------
-- 4. Capstone for Set3.
--
-- LanguageMorphism Setoid landed via the existing _≈M_. Set4 lifts
-- respect-≈M to natural transformations; Set5 closes the Yoneda
-- obligation.
------------------------------------------------------------------------
