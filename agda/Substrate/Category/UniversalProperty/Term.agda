------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Term
--
-- UP3 of the UP-topos arc (TERM-ALGEBRA REVISION) per
-- [scratch/up_topos_arc_plan.md].
--
-- The term-algebra encoding of UP-morphisms, per the
-- [[roll-our-own-via-word-algebra]] discipline and the substrate's
-- existing Coxeter Word / OpcodeAlgebra / GeneratorOperad pattern.
--
-- An object-level UP-morphism is NOT a record but a typed-cons-list
-- of GENERATORS. The record-based UPMorphism (UP2,
-- Substrate.Category.UniversalProperty.Morphism) is the SEMANTIC
-- target — what a UPTerm evaluates to. The term IS the morphism;
-- the record is its denotation.
--
-- This makes the substrate's UPCategory a small term-presented
-- category whose sheaves are tractable (UP31+), and lets the
-- existing word-algebra infrastructure apply to UP-morphisms
-- uniformly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Term where

open import Substrate.Category.UniversalProperty using (UniversalProperty)
open import Substrate.Category.UniversalProperty.Morphism using (UPMorphism)

------------------------------------------------------------------------
-- 1. The generator datatype: UPGen.
--
-- Parametric in source / target UPs. Each constructor is a "named
-- elementary refinement" between two universal properties. The
-- generators ARE the substrate's irreducible UP-translation moves;
-- composite refinements are sequences of these.
--
-- A generator records the WITNESS (a UPMorphism record) — that is,
-- each generator carries its own semantic content. UPTerm-level
-- composition stacks them; eval (UP5) realises the stack.
--
-- This pattern mirrors Substrate.Category.GeneratorOperad's
-- generator-plus-semantics design: the generator IS data carrying
-- a target-realisation.
------------------------------------------------------------------------

data UPGen : UniversalProperty → UniversalProperty → Set₁ where
  -- The fundamental generator: lift a UPMorphism record to a
  -- single-step term. Every concrete refinement (forget, transport,
  -- yoneda, dualise, adjoint-swap, ...) shows up as a `lift mor`
  -- with `mor` the appropriate UPMorphism record.
  lift : {U₁ U₂ : UniversalProperty} → UPMorphism U₁ U₂ → UPGen U₁ U₂

------------------------------------------------------------------------
-- 2. The term datatype: UPTerm = typed cons-list of UPGen.
--
-- A UPTerm U₁ U₂ is a sequence of generators stacking from U₁ to U₂
-- through an arbitrary chain of intermediate UPs. The empty term is
-- the identity; append is composition.
------------------------------------------------------------------------

data UPTerm : UniversalProperty → UniversalProperty → Set₁ where
  []  : {U : UniversalProperty} → UPTerm U U
  _∷_ : {U₁ U₂ U₃ : UniversalProperty} →
        UPGen U₁ U₂ → UPTerm U₂ U₃ → UPTerm U₁ U₃

infixr 5 _∷_

------------------------------------------------------------------------
-- 3. Term concatenation (composition at the term level).
--
-- The substrate-native composition: append the generator-lists.
-- Identity at U is `[]`; associativity is the substrate's standard
-- list-append associativity (mechanical induction).
------------------------------------------------------------------------

_++ᵤ_ :
  {U₁ U₂ U₃ : UniversalProperty} →
  UPTerm U₁ U₂ → UPTerm U₂ U₃ → UPTerm U₁ U₃
[]       ++ᵤ ys = ys
(x ∷ xs) ++ᵤ ys = x ∷ (xs ++ᵤ ys)

infixr 4 _++ᵤ_

------------------------------------------------------------------------
-- 4. Capstone for UP3.
--
-- The term-algebra is named. UP4 supplies the equational theory
-- (relations on UPTerm); UP5 supplies the semantics
-- eval : UPTerm → UPMorphism-record. UP6 packages UPCategory
-- as terms modulo equations.
------------------------------------------------------------------------
