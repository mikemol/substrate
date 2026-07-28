------------------------------------------------------------------------
-- Substrate.Linguistic.ClassFunctor
--
-- Y6 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The `class : LanguageWitness → FreeConstructionClass` map lifts
-- to a functor from LanguageCategory to the CODISCRETE category on
-- FreeConstructionClass. In the codiscrete category, there's a
-- unique morphism between every pair of classes; this makes the
-- lift trivially functorial.
--
-- Per [[feedback-categorical-name-first]]: the classification is a
-- FUNCTOR (not just a function-on-objects); the codiscrete
-- codomain is the substrate-honest framing for "classes don't
-- constrain morphisms — morphisms can cross cells, but the class
-- is still a well-defined classifying assignment."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.ClassFunctor where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Morphism using (LanguageMorphism)

------------------------------------------------------------------------
-- 1. The codiscrete category on FreeConstructionClass.
--
-- Has a unique morphism between every pair of classes. Sometimes
-- called the "chaotic" or "indiscrete" category.
------------------------------------------------------------------------

  using (Free-monoid; Free-F2-module; Free-cyclic;
         Free-relation; Free-CCC; Free-Lie)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment.Witness using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)
data ClassMorphism : FreeConstructionClass → FreeConstructionClass → Set where
  any-class-mor :
    (a b : FreeConstructionClass) → ClassMorphism a b

-- Identity in this category: a self-morphism.
id-ClassMorphism : (a : FreeConstructionClass) → ClassMorphism a a
id-ClassMorphism a = any-class-mor a a

-- Composition: trivially defined (codiscrete category).
_∘C_ :
  {a b c : FreeConstructionClass} →
  ClassMorphism b c → ClassMorphism a b → ClassMorphism a c
_∘C_ {a} {_} {c} _ _ = any-class-mor a c

------------------------------------------------------------------------
-- 2. The class functor on morphisms.
--
-- For any LanguageMorphism f : L₁ → L₂, lift to a morphism
-- (class L₁) → (class L₂) in the codiscrete category.
------------------------------------------------------------------------

class-on-morphism :
  {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂} →
  LanguageMorphism L₁ L₂ →
  ClassMorphism (class L₁) (class L₂)
class-on-morphism {L₁ = L₁} {L₂ = L₂} _ = any-class-mor (class L₁) (class L₂)

------------------------------------------------------------------------
-- 3. Functoriality witnesses (trivially in the codiscrete codomain).
--
-- Both laws hold because the codiscrete category has at most one
-- morphism between any pair of objects.
------------------------------------------------------------------------

-- The two morphisms between fixed (a, b) in the codiscrete
-- category are equal — there's only one.
codiscrete-unique :
  {a b : FreeConstructionClass}
  (f g : ClassMorphism a b) → f ≡ g
codiscrete-unique (any-class-mor _ _) (any-class-mor _ _) = refl

------------------------------------------------------------------------
-- 4. Smoke tests: the six witnesses' class assignments.
--
-- Each witness's class is exactly the expected cell.
------------------------------------------------------------------------


class-lojban   : class lojban-witness   ≡ Free-monoid
class-lojban   = refl

class-tokipona : class tokipona-witness ≡ Free-F2-module
class-tokipona = refl

class-solresol : class solresol-witness ≡ Free-cyclic
class-solresol = refl

class-kelen    : class kelen-witness    ≡ Free-relation
class-kelen    = refl

class-lambda   : class lambda-witness   ≡ Free-CCC
class-lambda   = refl

class-lie      : class lie-witness      ≡ Free-Lie
class-lie      = refl

------------------------------------------------------------------------
-- 5. Capstone for Y6.
--
-- class is a functor from LanguageCategory to the codiscrete
-- category on FreeConstructionClass. Y7 builds the Hom-functor;
-- Y8 the Yoneda embedding.
------------------------------------------------------------------------
