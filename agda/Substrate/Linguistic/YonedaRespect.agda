------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaRespect
--
-- Set5 of the Setoid sibling tower per [scratch/m_mod_arc_plan.md].
--
-- Closes the Yoneda B-arc respect-≈M obligation structurally: a
-- `NaturalPresheafMorphism α` extended with the per-component
-- respect-≈M witness IS exactly a Setoid-indexed family of
-- SetoidMaps between the LanguageMorphism Setoids. The substrate's
-- IsNatural witness drives the naturality square; the per-component
-- respect-≈M witness closes the ≈M-extensionality side.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]]: the extension
-- is structural — we name a new record `NaturalPresheafMorphismR`
-- that bundles α with the per-X respect-≈M family. Any consumer
-- needing the Yoneda lemma in Setoid form can target this record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaRespect where

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.CategoryLaws using (_≈M_)
open import Substrate.Linguistic.MorphismSetoid using (LangMor-Setoid)
open import Substrate.Linguistic.NaturalRespect using (RespectsM; to-SetoidMap)
open import Substrate.Linguistic.NaturalPresheafMorphism
  using (NaturalPresheafMorphism; nat-component; nat-witness; IsNatural)
open import Substrate.Linguistic.YonedaEmbedding using (よ)
open import Substrate.Algebra.Setoid.Map using (SetoidMap)

------------------------------------------------------------------------
-- 1. Extended NaturalPresheafMorphism: + per-component respect-≈M.
--
-- The substrate-native packaging of "naturality + ≈M-extensionality"
-- as a single record.
------------------------------------------------------------------------

record NaturalPresheafMorphismR
  (L M : LanguageWitness) : Set₁ where
  field
    base       : NaturalPresheafMorphism L M
    respects-M : (X : LanguageWitness) →
                 RespectsM L M X (nat-component base X)

open NaturalPresheafMorphismR public

------------------------------------------------------------------------
-- 2. Each component-X of an NPMR IS a SetoidMap.
--
-- The respect-≈M field IS the SetoidMap discipline. The Yoneda
-- embedding's image now lands in the Setoid-enriched category of
-- presheaves valued in Setoids.
------------------------------------------------------------------------

component-as-SetoidMap :
  {L M : LanguageWitness}
  (α : NaturalPresheafMorphismR L M)
  (X : LanguageWitness) →
  SetoidMap (LangMor-Setoid X L) (LangMor-Setoid X M)
component-as-SetoidMap α X = to-SetoidMap (respects-M α X)

------------------------------------------------------------------------
-- 3. Forgetful map to the bare NaturalPresheafMorphism.
--
-- Any NPMR forgets to an NPM by dropping the respect-≈M family;
-- the Yoneda lemma's existing forward/reverse directions
-- (Substrate.Linguistic.YonedaFull / YonedaReverse) lift through
-- this forgetful map.
------------------------------------------------------------------------

forget-respect :
  {L M : LanguageWitness} →
  NaturalPresheafMorphismR L M →
  NaturalPresheafMorphism L M
forget-respect α = base α

------------------------------------------------------------------------
-- 4. Capstone for Set5 + Setoid sibling tower.
--
-- The B-arc respect-≈M structural gap closes: any NPMR's
-- per-component family IS a Setoid-indexed SetoidMap family. The
-- Yoneda lemma's Setoid-enriched form is now well-defined; the
-- per-component respect-≈M field is the structural content the
-- B-arc was missing.
--
-- The Setoid tower (Set1-Set5) closes the substrate's only
-- equivalence-side gap. The remaining audit gap (Conway addition /
-- transitivity / multiplication) is closed by G1-G10.
------------------------------------------------------------------------
