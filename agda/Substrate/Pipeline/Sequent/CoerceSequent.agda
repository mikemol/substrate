------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.CoerceSequent
--
-- coerce-sequent : A ⊢ B via a named isomorphism. The user provides
-- the forward direction; the inverse is the consumer's responsibility
-- (e.g., Galois pairs for round-trip codecs).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.CoerceSequent where

open import Substrate.Pipeline.Sequent.SequentRule using (coerce)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

coerce-sequent : (A B : Set) → (A → B) → Sequent {A} {B} (record {})
coerce-sequent A B f = record
  { rule       = coerce
  ; derivation = f
  }
