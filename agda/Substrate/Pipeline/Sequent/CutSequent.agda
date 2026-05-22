------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.CutSequent
--
-- cut-sequent : Γ ⊢ A and A ⊢ B yield Γ ⊢ B. Function composition
-- for sequents — the structural-rule analog of Composition.compose.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.CutSequent where

open import Substrate.Pipeline.Sequent.SequentRule using (cut)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

cut-sequent : ∀ {A B C : Set}
            → Sequent (record { A = A ; B = B })
            → Sequent (record { A = B ; B = C })
            → Sequent (record { A = A ; B = C })
cut-sequent s₁ s₂ = record
  { rule       = cut
  ; derivation = λ a → Sequent.derivation s₂ (Sequent.derivation s₁ a)
  }
