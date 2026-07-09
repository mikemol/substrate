------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.ExchangeSequent
--
-- exchange-sequent : A × B ⊢ B × A. Swap two parallel streams.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.ExchangeSequent where

open import Substrate.Foundation.Product using (_×_; swap)
open import Substrate.Pipeline.Sequent.SequentRule using (exchange)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

exchange-sequent : (A B : Set)
                 → Sequent {A × B} {B × A} (record {})
exchange-sequent A B = record
  { rule       = exchange
  ; derivation = swap
  }
