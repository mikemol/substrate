------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Identity
--
-- The identity permutation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Identity (A : Set) where

open import Substrate.Foundation.Function using (id)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Foundation.Eq

ε : Permutation
ε = record
  { apply = id
  ; invₐ  = id
  ; inv-l = λ _ → refl
  ; inv-r = λ _ → refl
  }
