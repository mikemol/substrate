------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Eval
--
-- T6: evaluation LensTerm → opaque-lens semantic target.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Eval where

open import Substrate.Category.StochasticLens.Term

module _ {Lens : LensTriple → LensTriple → Set}
         (id-Lens : ∀ {t} → Lens t t)
         (comp-Lens : ∀ {t₁ t₂ t₃} → Lens t₂ t₃ → Lens t₁ t₂ → Lens t₁ t₃)
         (lift-Lens : ∀ {t₁ t₂} → Lens t₁ t₂) where

  eval-gen : ∀ {t₁ t₂} → LensGen t₁ t₂ → Lens t₁ t₂
  eval-gen (lift-lens _ _) = lift-Lens

  eval : ∀ {t₁ t₂} → LensTerm t₁ t₂ → Lens t₁ t₂
  eval []       = id-Lens
  eval (g ∷ ts) = comp-Lens (eval ts) (eval-gen g)
