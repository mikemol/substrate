------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.RightCancelEpsilon
--
-- a ·₄ b ≡ b forces a ≡ ε.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.RightCancelEpsilon where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε; v4×v4-cover)
open import Substrate.Foundation.Eq

·-right-cancel-ε : (a b : V₄) → a ·₄ b ≡ b → a ≡ ε
·-right-cancel-ε = v4×v4-cover _
  ( ((λ _ → refl) , (λ _ → refl) , (λ _ → refl) , (λ _ → refl))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  )
