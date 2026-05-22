------------------------------------------------------------------------
-- Substrate.Foundation.Empty.Polymorphic
--
-- Universe-polymorphic empty type. Distinguished from
-- Substrate.Foundation.Empty (mono-universe, ⊥ : Set) for higher-universe
-- contexts. ⊥-elim is the eliminator.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Empty.Polymorphic where

open import Substrate.Foundation.Level using (Level)

private
  variable
    ℓ ℓ′ : Level

data ⊥ {ℓ} : Set ℓ where

⊥-elim : {A : Set ℓ′} → ⊥ {ℓ} → A
⊥-elim ()
