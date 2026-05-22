------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Term
--
-- T1: term-algebra encoding of Markov-category morphisms.
--
-- Per the substrate's UP-topos discipline ([[roll-our-own-via-word-
-- algebra]] + Substrate.Category.UniversalProperty.Term pattern):
-- morphism = typed cons-list of generators.
--
-- A MarkovTerm X Y is a sequence of named elementary kernel moves
-- stacking from X to Y through arbitrary intermediate objects.
-- Composition is list concatenation; identity is the empty term.
-- Category laws hold STRUCTURALLY (mechanical list-append induction).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Term where

------------------------------------------------------------------------
-- Markov object abstraction: an abstract Set of objects parameterised
-- by a chosen carrier type. Concrete instances supply the carrier.

Obj : Set₁
Obj = Set

------------------------------------------------------------------------
-- T1a: The generator datatype MarkovGen.
--
-- Each constructor is a named elementary Markov-category move:
--   copy   : X → X × X         (comonoid copy / branching)
--   delete : X → ⊤              (comonoid delete / marginalisation)
--   swap   : X × Y → Y × X      (symmetric monoidal swap)
--   tensor : X → Y, X' → Y' lift to X×X' → Y×Y'
--   lift   : an opaque kernel X → Y (e.g., a Markov matrix)
--
-- The lift constructor carries witness data; concrete instances
-- (FinStoch, Stoch) supply their own kernel representation.

data MarkovGen : Obj → Obj → Set₁ where
  -- Lift an opaque kernel between two objects.
  lift   : (X Y : Obj) → (X → Y → Set) → MarkovGen X Y
  -- The structural generators are stated abstractly; concrete
  -- instances supply copy / delete / swap as specific lifts.

------------------------------------------------------------------------
-- T1b: The term datatype MarkovTerm = typed cons-list.

data MarkovTerm : Obj → Obj → Set₁ where
  []  : {X : Obj} → MarkovTerm X X
  _∷_ : {X Y Z : Obj} →
        MarkovGen X Y → MarkovTerm Y Z → MarkovTerm X Z

infixr 5 _∷_

------------------------------------------------------------------------
-- T1c: Term concatenation = morphism composition.

_++ₘ_ : {X Y Z : Obj} →
        MarkovTerm X Y → MarkovTerm Y Z → MarkovTerm X Z
[]       ++ₘ ys = ys
(x ∷ xs) ++ₘ ys = x ∷ (xs ++ₘ ys)

infixr 4 _++ₘ_
