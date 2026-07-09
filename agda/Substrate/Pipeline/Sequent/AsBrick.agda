------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.AsBrick
--
-- sequent-as-brick: lift a Sequent into the full Brick framework.
-- Witnessing is D⇒S (degenerates to D→D since S = ⊤);
-- homomorphism-tag is `SequentRule` (the rule itself names the
-- structural property preserved).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.AsBrick where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Pipeline.Brick
open import Substrate.Pipeline.Sequent.SequentRule using (SequentRule)
open import Substrate.Pipeline.Sequent.SequentType using (SequentType; sequent→BrickType)
open import Substrate.Pipeline.Sequent.Type using (Sequent)

sequent-as-brick : ∀ {A B} {S : SequentType A B} → Sequent S → Brick (sequent→BrickType S)
sequent-as-brick seq = record
  { witnesses = D⇒S
  ; step      = λ (a , _) → Sequent.derivation seq a , tt
  ; homomorphism-tag = SequentRule
  }
