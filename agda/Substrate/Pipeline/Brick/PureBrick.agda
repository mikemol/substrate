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

-- ⟡set1-paydown: parameterize homomorphism-tag (the `homomorphism-tag : Set` FIELD forced
-- PureBrick : Set₁; as a module parameter every field is Set-valued, so PureBrick : Set.
-- Consumers write `PureBrick homomorphism-tag A B`.)
module _ (homomorphism-tag : Set) where
  record PureBrick (A B : Set) : Set where
    field
      f : A → B

  open PureBrick public

pure→Brick : ∀ {tag A B : Set} → PureBrick tag A B → BrickType
pure→Brick {tag} {A} {B} P = record
  { D-in  = A
  ; D-out = B
  ; S-in  = ⊤
  ; S-out = ⊤
  }

pure→Brick-step : ∀ {tag A B : Set} → (P : PureBrick tag A B)
                → (A × ⊤) → (B × ⊤)
pure→Brick-step P (a , _) = f P a , tt

pure-as-brick : ∀ {tag A B : Set} → (P : PureBrick tag A B)
              → Brick (pure→Brick P)
pure-as-brick {tag} P = record
  { witnesses        = D⇒S
  ; step             = λ x → f P (proj₁ x) , tt
  ; homomorphism-tag = tag
  }
