------------------------------------------------------------------------
-- Substrate.Category.CascadedCoalgebra.Term (T15)
-- Term-algebra encoding of cascaded-coalgebra morphisms.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CascadedCoalgebra.Term where

open import Substrate.Foundation.Product using (_,_; _×_)

-- A cascade state-pair (inner-state-type, outer-state-type).

CascadeState : Set₁
CascadeState = Set × Set

data CascadeGen : CascadeState → CascadeState → Set₁ where
  lift-cascade : (s₁ s₂ : CascadeState) → CascadeGen s₁ s₂

data CascadeTerm : CascadeState → CascadeState → Set₁ where
  []  : {s : CascadeState} → CascadeTerm s s
  _∷_ : {s₁ s₂ s₃ : CascadeState} →
        CascadeGen s₁ s₂ → CascadeTerm s₂ s₃ → CascadeTerm s₁ s₃

infixr 5 _∷_

_++ᶜᶜ_ : {s₁ s₂ s₃ : CascadeState} →
         CascadeTerm s₁ s₂ → CascadeTerm s₂ s₃ → CascadeTerm s₁ s₃
[]       ++ᶜᶜ ys = ys
(x ∷ xs) ++ᶜᶜ ys = x ∷ (xs ++ᶜᶜ ys)

infixr 4 _++ᶜᶜ_
