------------------------------------------------------------------------
-- Substrate.Probability.ConjugateMonad.Term (T17)
--
-- Term-algebra encoding of conjugate-prior updates.
-- A ConjugateTerm represents a SEQUENCE of Bayesian updates over a
-- parameter type — a typed cons-list of observations (or other
-- update operations).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.ConjugateMonad.Term where

open import Substrate.Foundation.Product using (_,_; _×_)

-- Conjugate-monad parameter pair: (parameter-type, observation-type).
ConjState : Set₁
ConjState = Set × Set

data ConjGen : ConjState → ConjState → Set₁ where
  lift-conj : (s₁ s₂ : ConjState) → ConjGen s₁ s₂

data ConjTerm : ConjState → ConjState → Set₁ where
  []  : {s : ConjState} → ConjTerm s s
  _∷_ : {s₁ s₂ s₃ : ConjState} →
        ConjGen s₁ s₂ → ConjTerm s₂ s₃ → ConjTerm s₁ s₃

infixr 5 _∷_

_++ᶜ_ : {s₁ s₂ s₃ : ConjState} →
        ConjTerm s₁ s₂ → ConjTerm s₂ s₃ → ConjTerm s₁ s₃
[]       ++ᶜ ys = ys
(x ∷ xs) ++ᶜ ys = x ∷ (xs ++ᶜ ys)

infixr 4 _++ᶜ_
