------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.IdentitySequent
--
-- identity-sequent : the trivial wire — A ⊢ A. Used when D-out and
-- D-in are the SAME type and no transformation is needed.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.IdentitySequent where

open import Substrate.Pipeline.Sequent.SequentRule using (identity)
open import Substrate.Pipeline.Sequent.SequentType using (SequentType)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

identity-sequent : (A : Set) → Sequent (record { A = A ; B = A })
identity-sequent A = record
  { rule       = identity
  ; derivation = λ a → a
  }
