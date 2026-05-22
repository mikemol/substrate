------------------------------------------------------------------------
-- Substrate.Foundation.Empty
--
-- Substrate-native empty type. Phase 2: native definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Empty where

data ⊥ : Set where

⊥-elim : {A : Set} → ⊥ → A
⊥-elim ()
