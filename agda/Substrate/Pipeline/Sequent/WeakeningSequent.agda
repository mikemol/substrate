------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.WeakeningSequent
--
-- weakening-sequent : A ⊢ A × B (add an unused B to the context).
-- Requires a B-value to provide; passed as a parameter.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.WeakeningSequent where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Pipeline.Sequent.SequentRule using (weakening)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

weakening-sequent : (A B : Set) → B → Sequent {A} {A × B} (record {})
weakening-sequent A B b = record
  { rule       = weakening
  ; derivation = λ a → a , b
  }
