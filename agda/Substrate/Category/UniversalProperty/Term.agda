------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Term
--
-- UP3 of the UP-topos arc — the TERM-ALGEBRA of UP-morphisms, now fully
-- dissolved to Set₀ (⟡ta-upterm-retire: the telescope UPGen/UPTerm over
-- UPArrowP are gone; these ARE the former O-forms, promoted).
--
-- An object-level UP-morphism is a typed cons-list of GENERATORS over a
-- Set₀ object-alphabet O with a Hom-generator payload:
--   * UPGen O Hom X Y = a single elementary refinement X → Y (a Hom choice).
--   * UPTerm O Hom X Y = a sequence of generators X → Y (a free-category word).
-- Identity = []; composition = _++ᵤ_ (append). The free category on the Hom
-- generators; Eval folds it into any UPCategory (Free⊣Forgetful).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Term where

------------------------------------------------------------------------
-- 1. The generator datatype: UPGen. A named elementary refinement X → Y,
-- carrying a Hom-generator choice (K = Hom, κ = id at eval).
------------------------------------------------------------------------

data UPGen (O : Set) (Hom : O → O → Set) : O → O → Set where
  lift : {X Y : O} → Hom X Y → UPGen O Hom X Y

------------------------------------------------------------------------
-- 2. The term datatype: UPTerm = typed cons-list of UPGen. [] = identity,
-- _∷_ = cons.
------------------------------------------------------------------------

data UPTerm (O : Set) (Hom : O → O → Set) : O → O → Set where
  []  : {X : O} → UPTerm O Hom X X
  _∷_ : {X Y Z : O} → UPGen O Hom X Y → UPTerm O Hom Y Z → UPTerm O Hom X Z

infixr 5 _∷_

------------------------------------------------------------------------
-- 3. Term concatenation = composition at the term level.
------------------------------------------------------------------------

_++ᵤ_ : {O : Set} {Hom : O → O → Set} {X Y Z : O}
      → UPTerm O Hom X Y → UPTerm O Hom Y Z → UPTerm O Hom X Z
[]       ++ᵤ ys = ys
(x ∷ xs) ++ᵤ ys = x ∷ (xs ++ᵤ ys)

infixr 4 _++ᵤ_
