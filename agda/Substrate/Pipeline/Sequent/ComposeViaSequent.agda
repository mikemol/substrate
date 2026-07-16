------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.ComposeViaSequent
--
-- compose-via-sequent: bridge two Bricks by an inserted Sequent.
-- The Sequent's A matches the upstream brick's D-out (refl) and
-- the Sequent's B matches the downstream brick's D-in (refl); state
-- edges thread through directly (refl).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.ComposeViaSequent where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Pipeline.Brick
open import Substrate.Pipeline.Sequent.SequentType using (SequentType)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

-- ⟡set1-rp: telescope carriers for Brick (auto).
private variable
  Tagb₁ Tagb₂ : Set

-- ⟡set1-paydown: BrickType edges are now type indices — thread them and read directly; the
-- composite's edges are supplied explicitly to Brick, its tag is `record {}`.
compose-via-sequent
  : ∀ {Di₁ Do₁ Si₁ So₁ Di₂ Do₂ Si₂ So₂ : Set}
    {T₁ : BrickType Di₁ Do₁ Si₁ So₁} {T₂ : BrickType Di₂ Do₂ Si₂ So₂} {A B : Set}
  → (b₁ : Brick T₁ Tagb₁)
  → (S : SequentType A B)
  → (seq : Sequent S)
  → (b₂ : Brick T₂ Tagb₂)
  → Do₁ ≡ A
  → B   ≡ Di₂
  → So₁ ≡ Si₂
  → Brick {Di₁} {Do₂} {Si₁} {So₂} (record {}) ⊤
compose-via-sequent b₁ S seq b₂ refl refl refl = record
  { witnesses = Brick.witnesses b₁
  ; step      = λ (d , s) →
                  let (d₁ , s₁) = Brick.step b₁ (d , s)
                      d₁'       = Sequent.derivation seq d₁
                  in Brick.step b₂ (d₁' , s₁)
  }
