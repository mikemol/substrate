------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaReverse
--
-- B8 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- Closes Y9's deferred REVERSE direction of the Yoneda lemma at
-- the substrate-friendly NATURALITY-DIRECT form.
--
-- Given a NATURAL transformation α : よ L ⇒ よ M, we recover a
-- language morphism `forward-from-natural α = nat-component α L
-- (id-morphism L) : LanguageMorphism L M`. Naturality of α at
-- (f = h, h-arg = id-morphism L) directly gives:
--
--   nat-component α X (id-morphism L ∘L h)
--     ≈M (forward-from-natural α) ∘L h
--
-- This is the naturality-direct statement; the FULL Yoneda lemma's
-- "α ≈Nat yoneda-backward (forward-from-natural α)" further
-- requires α-X to respect _≈M_ on its inputs (a respect-condition
-- not given by the NaturalPresheafMorphism record). The honest
-- substrate-internal closure of the Y9 reverse direction is
-- exactly the lemma proven here; the additional respect-condition
-- is deferred per [[feedback-coalgebraic-not-consumer-driven]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaReverse where

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws using (_≈M_)
open import Substrate.Linguistic.YonedaEmbedding using (よ)
open import Substrate.Linguistic.NaturalPresheafMorphism
  using (NaturalPresheafMorphism; nat-component; nat-witness)

------------------------------------------------------------------------
-- 1. The forward-extraction: α at the identity.
--
-- Given a natural α : よ L ⇒ よ M, extract the language morphism
-- f : L → M whose post-composition recovers α.
------------------------------------------------------------------------

forward-from-natural :
  {L M : LanguageWitness} →
  NaturalPresheafMorphism L M → LanguageMorphism L M
forward-from-natural {L} α = nat-component α L (id-morphism L)

------------------------------------------------------------------------
-- 2. The reverse-direction statement (naturality-direct form).
--
-- Direct consequence of α's naturality at (f = h, h-arg = id):
--   nat-component α X (id-morphism L ∘L h)
--     ≈M (forward-from-natural α) ∘L h
--
-- The naturality witness PRODUCES this; no identity-law
-- manipulation needed at this level.
------------------------------------------------------------------------

yoneda-reverse-direct :
  {L M : LanguageWitness}
  (α : NaturalPresheafMorphism L M)
  {X : LanguageWitness}
  (h : よ L X) →
  nat-component α X (id-morphism L ∘L h)
    ≈M (forward-from-natural α) ∘L h
yoneda-reverse-direct α h = nat-witness α h (id-morphism _)

------------------------------------------------------------------------
-- 3. Capstone for B8.
--
-- The Yoneda reverse-direction's NATURALITY-DIRECT form holds.
-- The full ≈Nat-level reconstruction requires α-X to respect _≈M_
-- on inputs (i.e., extending NaturalPresheafMorphism with an
-- additional respect-≈M field). B9 packages BOTH directions of
-- the Yoneda lemma, citing the partial closure here.
------------------------------------------------------------------------
