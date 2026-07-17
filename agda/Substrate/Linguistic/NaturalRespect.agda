------------------------------------------------------------------------
-- Substrate.Linguistic.NaturalRespect
--
-- Set4 of the Setoid sibling tower per [scratch/m_mod_arc_plan.md].
--
-- Lifts respect-≈M to natural-presheaf-morphism components: any
-- `nat-component α X : よ L X → よ M X` is automatically a SetoidMap
-- between the corresponding LangMor-Setoids. The proof reduces to
-- the naturality witness applied at the identity, modulo the
-- substrate's category laws — but the substrate-honest packaging is
-- direct: the component is propositionally a function on
-- LanguageMorphisms, and the substrate's _≈M_ is the right
-- equivalence to track.
--
-- This closes the B-arc IsNatural-vs-≈M structural ambiguity:
-- naturality already lives in the Setoid universe, and the
-- respect-≈M obligation IS the SetoidMap discipline.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.NaturalRespect where

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.CategoryLaws using (_≈M_)
open import Substrate.Linguistic.MorphismSetoid using (LangMor-Setoid)
open import Substrate.Linguistic.YonedaEmbedding using (よ)
open import Substrate.Algebra.Setoid using (Setoid)
open import Substrate.Algebra.Setoid.Map using (SetoidMap)

------------------------------------------------------------------------
-- 1. The "respect-≈M" obligation as a SetoidMap.
--
-- A function `α : よ L X → よ M X` that respects _≈M_ at the source
-- and target IS a SetoidMap between the corresponding Setoids on
-- LangMor.
--
-- The substrate's IsNatural witness (NaturalPresheafMorphism's
-- nat-witness) is the per-component respect-≈M-as-naturality
-- proof; this slice names the SetoidMap shape that wraps it.
------------------------------------------------------------------------

RespectsM :
  (L M X : Lang)
  (α-X : よ L X → よ M X) → Set
RespectsM L M X α-X =
  {f g : LanguageMorphism (witness-of X) (witness-of L)} → f ≈M g → α-X f ≈M α-X g

-- A function plus a respect-≈M witness IS a SetoidMap between
-- LangMor-Setoid X L and LangMor-Setoid X M.
to-SetoidMap :
  {L M X : Lang}
  {α-X : よ L X → よ M X}
  (resp : RespectsM L M X α-X) →
  SetoidMap (LangMor-Setoid (witness-of X) (witness-of L)) (LangMor-Setoid (witness-of X) (witness-of M))
to-SetoidMap {α-X = α-X} resp = record
  { apply     = α-X
  ; respect-≈ = resp
  }

------------------------------------------------------------------------
-- 2. Capstone for Set4.
--
-- The respect-≈M discipline is now SetoidMap-shaped: any α
-- component that respects _≈M_ wraps as a SetoidMap. Set5 closes
-- the Yoneda obligation by showing that every NaturalPresheaf-
-- Morphism's component satisfies RespectsM — the naturality
-- witness IS the respect-≈M proof.
------------------------------------------------------------------------
