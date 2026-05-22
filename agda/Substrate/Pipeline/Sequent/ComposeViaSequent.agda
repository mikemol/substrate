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

compose-via-sequent
  : ∀ {T₁ T₂ : BrickType}
  → (b₁ : Brick T₁)
  → (S : SequentType)
  → (seq : Sequent S)
  → (b₂ : Brick T₂)
  → BrickType.D-out T₁ ≡ SequentType.A S
  → SequentType.B S    ≡ BrickType.D-in  T₂
  → BrickType.S-out T₁ ≡ BrickType.S-in  T₂
  → Brick (record
      { D-in  = BrickType.D-in  T₁
      ; D-out = BrickType.D-out T₂
      ; S-in  = BrickType.S-in  T₁
      ; S-out = BrickType.S-out T₂
      })
compose-via-sequent {T₁} {T₂} b₁ S seq b₂ refl refl refl = record
  { witnesses = Brick.witnesses b₁
  ; step      = λ (d , s) →
                  let (d₁ , s₁) = Brick.step b₁ (d , s)
                      d₁'       = Sequent.derivation seq d₁
                  in Brick.step b₂ (d₁' , s₁)
  ; homomorphism-tag = ⊤
  }
