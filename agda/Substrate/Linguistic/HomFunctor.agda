------------------------------------------------------------------------
-- Substrate.Linguistic.HomFunctor
--
-- Y7 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The Hom-functors Hom(L, -) and Hom(-, L) on LanguageCategory.
--
-- The COVARIANT hom-functor Hom(L, -) sends X ↦ LanguageMorphism L
-- X, and on morphisms acts by POST-COMPOSITION (sending f : X → Y
-- to the function (h : Hom L X) ↦ f ∘L h).
--
-- The CONTRAVARIANT hom-functor Hom(-, L) sends X ↦ LanguageMorphism
-- X L, and on morphisms acts by PRE-COMPOSITION (sending f : X → Y
-- to the function (h : Hom Y L) ↦ h ∘L f). This is the building
-- block of the Yoneda embedding (Y8).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.HomFunctor where

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.Compose using (_∘L_)

------------------------------------------------------------------------
-- 1. The covariant hom-functor Hom(L, -).
--
-- Object part: X ↦ LanguageMorphism L X.
-- Morphism part: f : X → Y ↦ post-composition (h ↦ f ∘L h).
------------------------------------------------------------------------

Hom-cov : LanguageWitness → LanguageWitness → Set
Hom-cov L X = LanguageMorphism L X

-- The covariant functor's action on a morphism f : X → Y:
-- send (h : Hom-cov L X) to (f ∘L h : Hom-cov L Y).
Hom-cov-map :
  {L X Y : LanguageWitness} →
  LanguageMorphism X Y →
  Hom-cov L X → Hom-cov L Y
Hom-cov-map f h = f ∘L h

------------------------------------------------------------------------
-- 2. The contravariant hom-functor Hom(-, L).
--
-- Object part: X ↦ LanguageMorphism X L.
-- Morphism part: f : X → Y ↦ PRE-composition (h ↦ h ∘L f).
--
-- Note the direction reversal: applying Hom(-, L) to f : X → Y
-- gives a function Hom(Y, L) → Hom(X, L) (reversed).
------------------------------------------------------------------------

Hom-contra : LanguageWitness → LanguageWitness → Set
Hom-contra X L = LanguageMorphism X L

-- The contravariant functor's action on a morphism f : X → Y:
-- send (h : Hom-contra Y L) to (h ∘L f : Hom-contra X L).
Hom-contra-map :
  {L X Y : LanguageWitness} →
  LanguageMorphism X Y →
  Hom-contra Y L → Hom-contra X L
Hom-contra-map f h = h ∘L f

------------------------------------------------------------------------
-- 3. Worked examples for the canonical witnesses.
--
-- For the six witnesses, the hom-sets at each pair (X, Y) collect
-- all language morphisms X → Y. The substrate-native Set-valued
-- Hom-set is realised at the type level.
------------------------------------------------------------------------

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)

-- Hom-set from Lojban to Toki Pona.
Hom-Lojban-TokiPona : Set
Hom-Lojban-TokiPona = LanguageMorphism lojban-witness tokipona-witness

-- Hom-set from Lojban to itself (always inhabited via id-morphism).
Hom-Lojban-Lojban : Set
Hom-Lojban-Lojban = LanguageMorphism lojban-witness lojban-witness

------------------------------------------------------------------------
-- 4. Capstone for Y7.
--
-- Hom-functors are defined. Hom-contra is the building block of
-- the Yoneda embedding (Y8): the contravariant Hom(-, L) IS the
-- presheaf よ(L).
------------------------------------------------------------------------
