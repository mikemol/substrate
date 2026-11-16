------------------------------------------------------------------------
-- Substrate.Foundation.Empty.Polymorphic
--
-- Universe-polymorphic empty type. Distinguished from
-- Substrate.Foundation.Empty (mono-universe, ⊥ᵖ : Set) for higher-universe
-- contexts. ⊥-elim is the eliminator.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Empty.Polymorphic where

open import Substrate.Foundation.Level using (Level)

private
  variable
    ℓ ℓ′ : Level

data ⊥ᵖ {ℓ} : Set ℓ where

⊥-elim : {A : Set ℓ′} → ⊥ᵖ {ℓ} → A
⊥-elim ()
