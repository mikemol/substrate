------------------------------------------------------------------------
-- Substrate.Foundation.Negation
--
-- Substrate-native negation + decidability. Phase 2: native.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Negation where

open import Substrate.Foundation.Empty using (⊥; ⊥-elim)

infix 3 ¬_

¬_ : Set → Set
¬ A = A → ⊥

data Dec (A : Set) : Set where
  yes : A   → Dec A
  no  : ¬ A → Dec A

-- Negation of a decidable proposition is decidable.
dec-¬ : {A : Set} → Dec A → Dec (¬ A)
dec-¬ (yes a)  = no (λ ¬a → ¬a a)
dec-¬ (no  ¬a) = yes ¬a

-- Decidable propositions are ¬¬-stable (the constructive elimination
-- of double negation that the substrate otherwise withholds, available
-- exactly when the proposition is decidable).
from-¬¬ : {A : Set} → Dec A → ¬ ¬ A → A
from-¬¬ (yes a)  _   = a
from-¬¬ (no  ¬a) ¬¬a = ⊥-elim (¬¬a ¬a)
