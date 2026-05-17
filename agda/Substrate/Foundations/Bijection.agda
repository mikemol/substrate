------------------------------------------------------------------------
-- Substrate.Foundations.Bijection
--
-- A small set-level bijection record + composition primitives. Used as
-- the universal-property shape for the M-12 bridges (Pairing,
-- Chirality, OrbitKey) and any future "bare type ↔ structural type"
-- migration.
--
-- BHK reading: an inhabitant of `Bijection A B` is constructive
-- evidence that A and B are interchangeable at the SET level (no
-- operation preservation here; that lives in tighter universal-
-- property records, e.g. F₂-Like, Image-Equivalent).
--
-- Scope: just to/from + two round-trips, and one combinator (product
-- of bijections, used by N-5 to derive OrbitKey ↔ V4-Nonzero × F₂).
-- Identity and inverse are trivial and added when a consumer needs
-- them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundations.Bijection where

open import Level using (Level; _⊔_)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; cong; cong₂)

------------------------------------------------------------------------
-- The bijection record.
------------------------------------------------------------------------

record Bijection {ℓa ℓb : Level} (A : Set ℓa) (B : Set ℓb) : Set (ℓa ⊔ ℓb) where
  field
    to      : A → B
    from    : B → A
    to-from : (b : B) → to (from b) ≡ b
    from-to : (a : A) → from (to a) ≡ a

------------------------------------------------------------------------
-- Product of bijections.
--
-- Given A ↔ A' and B ↔ B', construct A × B ↔ A' × B' componentwise.
------------------------------------------------------------------------

_×-bij_ : ∀ {ℓa ℓa' ℓb ℓb'}
          {A : Set ℓa} {A' : Set ℓa'}
          {B : Set ℓb} {B' : Set ℓb'}
        → Bijection A A' → Bijection B B'
        → Bijection (A × B) (A' × B')
_×-bij_ {A = A} {A' = A'} {B = B} {B' = B'} F G =
  record
    { to      = λ (a , b) → BF.to a , BG.to b
    ; from    = λ (a' , b') → BF.from a' , BG.from b'
    ; to-from = λ (a' , b') → cong₂ _,_ (BF.to-from a') (BG.to-from b')
    ; from-to = λ (a , b)   → cong₂ _,_ (BF.from-to a) (BG.from-to b)
    }
  where
    module BF = Bijection F
    module BG = Bijection G
