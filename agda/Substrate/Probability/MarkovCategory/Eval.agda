------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Eval
--
-- T3: evaluation MarkovTerm → MarkovCategory record.
--
-- The TERM IS the morphism; the RECORD is its denotation. Eval
-- traverses the cons-list, applying each generator's semantic
-- content under composition in the target MarkovCategory.
--
-- Per the substrate's pattern (Substrate.Category.UniversalProperty.
-- Compose's eval): each generator carries witness data; eval
-- threads them through the category's composition.
--
-- This site connects the SYNTACTIC presentation (Term) to the
-- SEMANTIC target (record-shaped Hom).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Eval where

open import Substrate.Probability.MarkovCategory.Term

------------------------------------------------------------------------
-- Eval is parameterised over the SEMANTIC target — the abstract
-- Hom type and composition operation. Concrete instances supply
-- specific kernel semantics.

module _ {Hom : Obj → Obj → Set}
         (id-Hom : ∀ {X} → Hom X X)
         (comp-Hom : ∀ {X Y Z} → Hom Y Z → Hom X Y → Hom X Z)
         (lift-Hom : ∀ {X Y} → (X → Y → Set) → Hom X Y) where

  eval-gen : ∀ {X Y} → MarkovGen X Y → Hom X Y
  eval-gen (lift X Y rel) = lift-Hom rel

  eval : ∀ {X Y} → MarkovTerm X Y → Hom X Y
  eval []       = id-Hom
  eval (g ∷ ts) = comp-Hom (eval ts) (eval-gen g)

------------------------------------------------------------------------
-- Per the substrate's two-layer discipline: the term IS the
-- morphism (syntactic); eval IS the denotation function back to
-- the record.
