------------------------------------------------------------------------
-- Substrate.Foundation.List.Length
--
-- List length: structurally recursive count via ℕ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.List.Length where

open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)

private
  variable
    ℓ : Level

length : {A : Set ℓ} → List A → ℕ
length []       = zero
length (_ ∷ xs) = suc (length xs)
