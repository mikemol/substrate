------------------------------------------------------------------------
-- Substrate.Foundation.List.Any
--
-- `Any P xs` — a proof that the predicate P holds at SOME element of xs
-- (the constructive existential over a list: here = at the head, there =
-- somewhere in the tail). `x ∈ xs` is the membership instance `Any (x ≡_) xs`.
-- A submodule (not List.agda itself) so adding it doesn't recompile every
-- List importer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.List.Any where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.List using (List; []; _∷_)

private
  variable
    ℓ ℓ′ : Level

data Any {A : Set ℓ} (P : A → Set ℓ′) : List A → Set (ℓ ⊔ ℓ′) where
  here  : ∀ {x xs} → P x      → Any P (x ∷ xs)
  there : ∀ {x xs} → Any P xs → Any P (x ∷ xs)

infix 4 _∈_
_∈_ : {A : Set ℓ} → A → List A → Set ℓ
x ∈ xs = Any (λ y → x ≡ y) xs
