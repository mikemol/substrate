------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Term (T19)
-- Term-algebra encoding of DFT morphisms.
-- Generators: forward DFT, inverse DFT, identity, lift opaque.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Term where

-- DFT context = (carrier-type, coefficient-type).
DFTContext : Set₁
DFTContext = Set × Set
  where open import Data.Product using (_×_)
open import Substrate.Foundation.Product using (_,_; _×_)

data DFTGen : DFTContext → DFTContext → Set₁ where
  forward-DFT : (s₁ s₂ : DFTContext) → DFTGen s₁ s₂
  inverse-DFT : (s₁ s₂ : DFTContext) → DFTGen s₁ s₂
  lift-DFT    : (s₁ s₂ : DFTContext) → DFTGen s₁ s₂

data DFTTerm : DFTContext → DFTContext → Set₁ where
  []  : {s : DFTContext} → DFTTerm s s
  _∷_ : {s₁ s₂ s₃ : DFTContext} →
        DFTGen s₁ s₂ → DFTTerm s₂ s₃ → DFTTerm s₁ s₃

infixr 5 _∷_

_++ᶠ_ : {s₁ s₂ s₃ : DFTContext} →
        DFTTerm s₁ s₂ → DFTTerm s₂ s₃ → DFTTerm s₁ s₃
[]       ++ᶠ ys = ys
(x ∷ xs) ++ᶠ ys = x ∷ (xs ++ᶠ ys)

infixr 4 _++ᶠ_
