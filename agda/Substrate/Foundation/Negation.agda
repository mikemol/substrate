------------------------------------------------------------------------
-- Substrate.Foundation.Negation
--
-- Substrate-native negation + decidability. Phase 2: native.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Negation where

open import Substrate.Foundation.Empty using (⊥)

infix 3 ¬_

¬_ : Set → Set
¬ A = A → ⊥

data Dec (A : Set) : Set where
  yes : A   → Dec A
  no  : ¬ A → Dec A
