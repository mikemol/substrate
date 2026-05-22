------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.ContractionSequent
--
-- contraction-sequent : A × A ⊢ A. Merge duplicate assumptions —
-- picks the first; contraction is order-agnostic when both copies
-- are identical (typical scenario).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.ContractionSequent where

open import Substrate.Foundation.Product using (_×_; proj₁)
open import Substrate.Pipeline.Sequent.SequentRule using (contraction)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

contraction-sequent : (A : Set)
                    → Sequent (record { A = A × A ; B = A })
contraction-sequent A = record
  { rule       = contraction
  ; derivation = proj₁
  }
