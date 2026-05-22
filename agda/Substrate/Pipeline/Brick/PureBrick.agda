------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.PureBrick
--
-- PureBrick A B = a typed function A → B with a homomorphism tag.
-- The pure→Brick* helpers lift a PureBrick into the full Brick
-- framework with trivial S edges (⊤) and Witnessing = D⇒S.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.PureBrick where

open import Substrate.Foundation.Product using (_×_; _,_; proj₁)
open import Substrate.Pipeline.Brick.Unit using (⊤; tt)
open import Substrate.Pipeline.Brick.Type using (BrickType)
open import Substrate.Pipeline.Brick.Record using (Brick)
open import Substrate.Pipeline.Brick.Witnessing using (D⇒S)

record PureBrick (A B : Set) : Set₁ where
  field
    f : A → B
    homomorphism-tag : Set

pure→Brick : ∀ {A B : Set} → PureBrick A B → BrickType
pure→Brick {A} {B} P = record
  { D-in  = A
  ; D-out = B
  ; S-in  = ⊤
  ; S-out = ⊤
  }

pure→Brick-step : ∀ {A B : Set} → (P : PureBrick A B)
                → (A × ⊤) → (B × ⊤)
pure→Brick-step P (a , _) = PureBrick.f P a , tt

pure-as-brick : ∀ {A B : Set} → (P : PureBrick A B)
              → Brick (pure→Brick P)
pure-as-brick P = record
  { witnesses        = D⇒S
  ; step             = λ x → PureBrick.f P (proj₁ x) , tt
  ; homomorphism-tag = PureBrick.homomorphism-tag P
  }
