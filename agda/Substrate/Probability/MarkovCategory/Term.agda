------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Term
--
-- T1: term-algebra encoding of Markov-category morphisms — dissolved to Set₀
-- by the PARAMETERIZED-GENERATOR move, on BOTH of its Set₁ sources.
--
-- The flat form `data MarkovGen/MarkovTerm : Obj → Obj → Set₁` (with Obj = Set)
-- was Set₁ for TWO independent reasons; both dissolve by the SAME move (a
-- Set-valued thing becomes a Set₀ generator PARAMETER, its content recovered by
-- the fold's valuation — set1-carrier-always-parameterize):
--
--   LEG 1 — the PAYLOAD. `MarkovGen.lift` carried a kernel RELATION `X → Y → Set`
--     (data). It becomes a CHOICE from a kernel-generator alphabet — `Word K` (a
--     free combination of kernel-generators K); the actual relation is recovered
--     by a valuation `κ : Word K → Hom X Y` at eval (the pre-existing lift-Hom slot).
--   LEG 2 — the OBJECTS. `Obj = Set` (Set₁) becomes a Set₀ object-alphabet
--     PARAMETER `O : Set` — the same carrier-parameterize move that dissolved
--     UPArrow / ConjugationCoalgebra. No ℕ-index needed.
--
-- With `O K : Set` both Set₀ parameters, `MarkovGen`/`MarkovTerm : O → O → Set`
-- land at Set₀. A MarkovTerm is still a typed cons-list of named kernel moves
-- (composition = concatenation; identity = the empty term).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Term where

open import Substrate.Groups.Coxeter.Word using (Word)

-- LEG 2: the object alphabet O is a Set₀ DATA PARAMETER (was `Obj = Set`, Set₁).
-- LEG 1: K is the kernel-generator alphabet; a kernel is a `Word K`.
-- (O K are data parameters, so the constructors take them implicitly and infix
-- composition infers them.)

-- A generator: a named elementary Markov move between two objects, carrying a
-- kernel-CHOICE (a word over the kernel-generators K), not the opaque relation.
data MarkovGen (O K : Set) : O → O → Set where
  lift : (X Y : O) → Word K → MarkovGen O K X Y

-- The term datatype = typed cons-list of generators.
data MarkovTerm (O K : Set) : O → O → Set where
  []  : {X : O} → MarkovTerm O K X X
  _∷_ : {X Y Z : O} →
        MarkovGen O K X Y → MarkovTerm O K Y Z → MarkovTerm O K X Z

infixr 5 _∷_

-- Term concatenation = morphism composition.
_++ₘ_ : {O K : Set} {X Y Z : O} →
        MarkovTerm O K X Y → MarkovTerm O K Y Z → MarkovTerm O K X Z
[]       ++ₘ ys = ys
(x ∷ xs) ++ₘ ys = x ∷ (xs ++ₘ ys)

infixr 4 _++ₘ_
