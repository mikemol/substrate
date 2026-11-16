------------------------------------------------------------------------
-- Reflexivity: the identity in both directions — the ex-`refl` witness.
-- Context: Substrate/Foundation/Iff/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Iff.IffRefl where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Iff.Iff

⇔-refl : {A : Set} → A ⇔ A
⇔-refl = (λ x → x) , (λ x → x)
