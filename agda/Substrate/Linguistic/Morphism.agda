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

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; FreeOverBasis; η;
         Basis; FreeCarrier; structure)

------------------------------------------------------------------------
-- 1. The LanguageMorphism record.
--
-- A morphism from L₁ to L₂ pairs:
--   * basis-map : Basis L₁ → Basis L₂  (translation at the basis layer)
--   * carrier-map : FreeCarrier L₁ → FreeCarrier L₂  (induced at the
--     free-carrier layer)
-- subject to η-coherence:
--   carrier-map (η (structure L₁) b) ≡ η (structure L₂) (basis-map b)
------------------------------------------------------------------------

record LanguageMorphism (L₁ L₂ : LanguageWitness) : Set where
  constructor mkLangMor
  field
    basis-map   : Basis L₁ → Basis L₂
    carrier-map : FreeCarrier L₁ → FreeCarrier L₂
    η-coherence :
      (b : Basis L₁) →
      carrier-map (η (structure L₁) b) ≡ η (structure L₂) (basis-map b)

open LanguageMorphism public

------------------------------------------------------------------------
-- 2. Capstone for Y1.
--
-- The record names the morphism shape. Y2 supplies identity
-- morphisms; Y3 supplies composition; Y4 proves category laws.
------------------------------------------------------------------------
