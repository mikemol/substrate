------------------------------------------------------------------------
-- Substrate.Linguistic.Morphism
--
-- Y1 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The LanguageMorphism record: a typed morphism between two
-- LanguageWitness instances, consisting of a basis-map and a
-- carrier-map with η-coherence.
--
-- This is the categorical morphism class for the substrate's
-- category-of-languages: language alignments at the FreeOverBasis
-- level. The η-coherence law `carrier-map (η L₁ b) ≡ η L₂ (basis-map
-- b)` is the standard "preserves the basis embedding" condition for
-- morphisms in any category of free constructions.
--
-- Per [[feedback-categorical-name-first]]: "morphism in the category
-- of free constructions over a basis" is the standard categorical
-- name. Substrate.Category.Morphism is the generic primitive; this
-- module specialises it to LanguageWitness.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]]: cell-specific
-- structure-preservation (monoid-hom for free-monoid pairs, linear-
-- map for free-module pairs, etc.) is richer than basic η-coherence
-- and is deferred to a follow-up arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Morphism where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; FreeOverBasis; η; structure)

------------------------------------------------------------------------
-- 1. The LanguageMorphism record.
--
-- A morphism from L₁ to L₂ pairs:
--   * basis-map : B₁ → B₂  (translation at the basis layer)
--   * carrier-map : F₁ → F₂  (induced at the free-carrier layer)
-- subject to η-coherence:
--   carrier-map (η (structure L₁) b) ≡ η (structure L₂) (basis-map b)
--
-- B₁/F₁/B₂/F₂ are the (Basis, FreeCarrier) pairs L₁/L₂ were
-- instantiated at (⟡rc-lang, W5-L2) — explicit implicits, never a
-- `private variable` (a dependent carrier there would generalize
-- with a fresh level per use).
------------------------------------------------------------------------

record LanguageMorphism {B₁ F₁ B₂ F₂ : Set}
                         (L₁ : LanguageWitness B₁ F₁) (L₂ : LanguageWitness B₂ F₂) : Set where
  constructor mkLangMor
  field
    basis-map   : B₁ → B₂
    carrier-map : F₁ → F₂
    η-coherence :
      (b : B₁) →
      carrier-map (η (structure L₁) b) ≡ η (structure L₂) (basis-map b)

open LanguageMorphism public

------------------------------------------------------------------------
-- 2. Capstone for Y1.
--
-- The record names the morphism shape. Y2 supplies identity
-- morphisms; Y3 supplies composition; Y4 proves category laws.
------------------------------------------------------------------------
