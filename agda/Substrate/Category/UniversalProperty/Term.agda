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

open import Substrate.Category.UniversalProperty using (UPArrowP)
open import Substrate.Category.UniversalProperty.Morphism using (UPMorphism)

-- ⟡UPArrow-dissolve C: the objects are the UPArrowP telescope. UPGen/UPTerm
-- stay Set₁ (a data family whose constructors re-quantify {W : S→T→Set} cannot
-- land at Set₀ — see ⟡UPGen-ℕ-index for the deferred enumerable-objects drop),
-- but they no longer reference the flat UPArrow record. `variable` tames the
-- telescope so the constructors read as before.
-- NOTE: U₁/U₂/U₃ are bound EXPLICITLY per-signature (not as `variable`s):
-- UPArrowP is an eta record, and Agda refuses to auto-generalize over an
-- eta-expandable variable ("Cannot generalize over U₁ of eta-expandable type").
private variable
  S₁ T₁ S₂ T₂ S₃ T₃ : Set
  W₁ : S₁ → T₁ → Set
  W₂ : S₂ → T₂ → Set
  W₃ : S₃ → T₃ → Set

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

data UPGen : {S₁ T₁ : Set} {W₁ : S₁ → T₁ → Set} {S₂ T₂ : Set} {W₂ : S₂ → T₂ → Set}
           → UPArrowP S₁ T₁ W₁ → UPArrowP S₂ T₂ W₂ → Set₁ where
  -- The fundamental generator: lift a UPMorphism record to a
  -- single-step term. Every concrete refinement (forget, transport,
  -- yoneda, dualise, adjoint-swap, ...) shows up as a `lift mor`
  -- with `mor` the appropriate UPMorphism record.
  lift : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂}
       → UPMorphism U₁ U₂ → UPGen U₁ U₂

------------------------------------------------------------------------
-- 2. The term datatype: UPTerm = typed cons-list of UPGen.
--
-- A UPTerm U₁ U₂ is a sequence of generators stacking from U₁ to U₂
-- through an arbitrary chain of intermediate UPs. The empty term is
-- the identity; append is composition.
------------------------------------------------------------------------

data UPTerm : {S₁ T₁ : Set} {W₁ : S₁ → T₁ → Set} {S₂ T₂ : Set} {W₂ : S₂ → T₂ → Set}
            → UPArrowP S₁ T₁ W₁ → UPArrowP S₂ T₂ W₂ → Set₁ where
  []  : {U₁ : UPArrowP S₁ T₁ W₁} → UPTerm U₁ U₁
  _∷_ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃}
      → UPGen U₁ U₂ → UPTerm U₂ U₃ → UPTerm U₁ U₃

infixr 5 _∷_

------------------------------------------------------------------------
-- 3. Term concatenation (composition at the term level).
--
-- The substrate-native composition: append the generator-lists.
-- Identity at U is `[]`; associativity is the substrate's standard
-- list-append associativity (mechanical induction).
------------------------------------------------------------------------

_++ᵤ_ : {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃}
      → UPTerm U₁ U₂ → UPTerm U₂ U₃ → UPTerm U₁ U₃
[]       ++ᵤ ys = ys
(x ∷ xs) ++ᵤ ys = x ∷ (xs ++ᵤ ys)

infixr 4 _++ᵤ_

-- ⟡UPArrow-dissolve C: the shape of a binary object-family (the foldUPTerm
-- motive) under the UPArrowP telescope — a heterogeneous relation on objects.
-- Set₁ (quantifies over the carrier Sets); replaces the old `UPArrow → UPArrow
-- → Set` motive so foldUPTerm/foldUPTerm-unique need not spell the telescope.
ObjRel : Set₁
ObjRel = {S₁ T₁ : Set} {W₁ : S₁ → T₁ → Set} → UPArrowP S₁ T₁ W₁
       → {S₂ T₂ : Set} {W₂ : S₂ → T₂ → Set} → UPArrowP S₂ T₂ W₂ → Set

------------------------------------------------------------------------
-- ⟡ta-upterm COEXISTENCE — the O-parameterized generic forms (Set₀).
--
-- The telescope UPGen/UPTerm above are Set₁ because their constructors
-- re-quantify the objects' {S T : Set}. The dissolution (the same two-leg
-- parameterized-generator move that dissolved MarkovCategory.Term): the objects
-- become a Set₀ object-alphabet PARAMETER O (LEG 2), and the UPMorphism payload
-- becomes a CHOICE from the morphism set Hom (K:=Hom, recovered by the eval
-- valuation, LEG 1). O/Hom are DATA parameters, so constructors + infix compose
-- infer them; both datatypes land at Set₀. These coexist with the telescope
-- forms until the ~12 sheaf consumers migrate, then the telescope forms are
-- deleted and UPGenO/UPTermO renamed. (Eventual home: `module Site (O)(Hom)`.)
------------------------------------------------------------------------

data UPGenO (O : Set) (Hom : O → O → Set) : O → O → Set where
  liftO : {X Y : O} → Hom X Y → UPGenO O Hom X Y

data UPTermO (O : Set) (Hom : O → O → Set) : O → O → Set where
  []O  : {X : O} → UPTermO O Hom X X
  _∷O_ : {X Y Z : O} → UPGenO O Hom X Y → UPTermO O Hom Y Z → UPTermO O Hom X Z

infixr 5 _∷O_

_++ᵤO_ : {O : Set} {Hom : O → O → Set} {X Y Z : O}
       → UPTermO O Hom X Y → UPTermO O Hom Y Z → UPTermO O Hom X Z
[]O       ++ᵤO ys = ys
(x ∷O xs) ++ᵤO ys = x ∷O (xs ++ᵤO ys)

infixr 4 _++ᵤO_

------------------------------------------------------------------------
-- 4. Capstone for UP3.
--
-- The term-algebra is named. UP4 supplies the equational theory
-- (relations on UPTerm); UP5 supplies the semantics
-- eval : UPTerm → UPMorphism-record. UP6 packages UPCategory
-- as terms modulo equations.
------------------------------------------------------------------------
