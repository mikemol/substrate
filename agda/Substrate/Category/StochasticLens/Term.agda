------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Term
--
-- T4: term-algebra encoding of stochastic lenses.
--
-- A LensTerm (S₁, A₁, B₁) (S₂, A₂, B₂) is a sequence of lens
-- generators stacking from one (state, view, obs) triple to another.
-- Each generator is a named elementary lens move: identity, compose,
-- or lift-of-an-abstract-lens.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Term where

------------------------------------------------------------------------
-- Lens triple: (state, view, observation).

LensTriple : Set₁
LensTriple = Set × Set × Set
  where
    open import Substrate.Foundation.Product using (_×_)
open import Substrate.Foundation.Product using (_,_; _×_)

------------------------------------------------------------------------
-- T4a: LensGen — generators.

data LensGen : LensTriple → LensTriple → Set₁ where
  -- Lift an opaque lens between two triples.
  lift-lens : (t₁ t₂ : LensTriple) → LensGen t₁ t₂

------------------------------------------------------------------------
-- T4b: LensTerm — typed cons-list.

data LensTerm : LensTriple → LensTriple → Set₁ where
  []  : {t : LensTriple} → LensTerm t t
  _∷_ : {t₁ t₂ t₃ : LensTriple} →
        LensGen t₁ t₂ → LensTerm t₂ t₃ → LensTerm t₁ t₃

infixr 5 _∷_

------------------------------------------------------------------------
-- T4c: Term concatenation.

_++ₗ_ : {t₁ t₂ t₃ : LensTriple} →
        LensTerm t₁ t₂ → LensTerm t₂ t₃ → LensTerm t₁ t₃
[]       ++ₗ ys = ys
(x ∷ xs) ++ₗ ys = x ∷ (xs ++ₗ ys)

infixr 4 _++ₗ_
